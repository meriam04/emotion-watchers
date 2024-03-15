import csv
import numpy as np
import os
from pathlib import Path
import pickle
import re
import sys
import tensorflow as tf
from tensorflow.data import AUTOTUNE, Dataset
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Bidirectional,
    Conv1D,
    Dense,
    Dropout,
    Input,
    LSTM,
    Rescaling,
)
from typing import Optional, Tuple


from data_processing.process_data import TIMES_FILE_FORMAT


CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-{epoch:03d}.ckpt"
MAX_PUPIL_DILATION = 30
PERIOD = 0.01 #s


def get_data(pkl_dir: Path, face_dir: Path, window_size: int = 100, batch_size: int = 32):
    """
    Get the functions from the .pkl files and timestamps from the face directories, then create the dataset.

    Args:
        csv_paths: The list of paths to the .csv files containing the pupillometry data.
        classes: The list of classes to be used in the output layer.
        window_size: The number of data samples to be considered at a time.

    Returns:
        The dataset.
    """
    # Read the splines from the pkl files
    splines = {}
    for file in os.listdir(pkl_dir):
        # Check if the file is a pkl with the correct format
        if match := re.search(r"pupil_(?P<inits>\w+)_(?P<emotion>\w+).pkl$", str(file)):
            emotion = match["emotion"]
            inits = match["inits"]

            if match["inits"] not in splines:
                splines[match["inits"]] = {}

            with open(pkl_dir / file, 'rb') as f:
                splines[inits][emotion] = pickle.load(f)

    # Generate the dilations_windows, labels, and classes
    dilation_windows = []
    labels = []
    classes = []
    for i, label in enumerate(os.listdir(face_dir)):
        classes.append(label)
        for inits, init_splines in splines.items():
            for emotion, spline in init_splines.items():
                # Get the times file for this inits + emotion combination
                times_path = face_dir / label / TIMES_FILE_FORMAT.format(inits, emotion)
                if not os.path.isfile(times_path):
                    continue

                with open(times_path, 'r') as f:
                    reader = csv.DictReader(f)
                    for row in reader:
                        # Check if a window can be generated for this time
                        end_time = float(row["times"])
                        if end_time < PERIOD * window_size:
                            continue

                        # Generate a window for this time
                        times = np.linspace(end_time - PERIOD * window_size, end_time, window_size)
                        dilation_windows.append(spline(times))
                        labels.append(i)

    # Convert the dilations and labels to a tensor dataset
    dilations_t = tf.convert_to_tensor(dilation_windows)
    labels_t = tf.convert_to_tensor(labels)
    dataset = Dataset.from_tensor_slices((dilations_t, labels_t))

    # Prefetch datasets
    dataset = dataset.batch(batch_size).cache().shuffle(1000).prefetch(AUTOTUNE)

    return dataset, classes


def create_model(num_classes: int, input_shape: Optional[Tuple[int, int]] = None):
    """
    Create the LSTM model to be used on the pupillometry data.
    The architecture consists of 4 bidirectional LSTM layers and 2 convolutional layers,
    with dropout applied.

    Args:
        num_classes: The number of classes to be used in the output layer.
        input_shape: The shape of the input data.

    Returns:
        The LSTM model.
    """
    model = Sequential()

    if input_shape:
        model.add(Input(input_shape))

    model.add(Rescaling(1.0 / MAX_PUPIL_DILATION))
    model.add(Bidirectional(LSTM(16, dropout=0.2, return_sequences=True)))
    model.add(Conv1D(32, 3, activation="selu"))
    model.add(Dropout(0.2))
    model.add(Bidirectional(LSTM(16, dropout=0.2, return_sequences=True)))
    model.add(Bidirectional(LSTM(16, dropout=0.2, return_sequences=True)))
    model.add(Conv1D(32, 3, activation="selu"))
    model.add(Dropout(0.2))
    model.add(Bidirectional(LSTM(16, dropout=0.2, return_sequences=False)))

    if num_classes == 2:
        model.add(Dense(num_classes))
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    else:
        model.add(Dense(num_classes, "softmax"))
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)

    model.compile(loss=loss, optimizer="adam", metrics=["accuracy"])

    if input_shape:
        model.summary()

    return model


if __name__ == "__main__":
    # fix random seed for reproducibility
    tf.random.set_seed(496)

    window_size = 100
    batch_size = 32

    train_set, classes = get_data(Path(sys.argv[1]), Path(sys.argv[2]) / "train", window_size, batch_size)
    val_set, _ = get_data(Path(sys.argv[1]), Path(sys.argv[2]) / "val", window_size, batch_size)

    input_shape = (window_size, 1)
    num_classes = len(classes)

    # Create the LSTM model
    model = create_model(num_classes, input_shape)

    # Training
    cp_callback = ModelCheckpoint(CHECKPOINT_PATH, save_weights_only=True, verbose=1)
    model.fit(train_set, validation_data=val_set, epochs=10, callbacks=[cp_callback])
