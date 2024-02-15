import csv
import numpy as np
import os
from pathlib import Path
import re
import sys
import tensorflow as tf
from tensorflow.data import Dataset
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
from typing import List, Optional, Tuple


BINARY_CLASSES = [
    "positive",
    "negative",
    "negative",
    "positive",
    "negative",
    "positive",
]
MULTICLASS_CLASSES = ["joy", "anger", "fear", "fun", "sad", "happy"]
CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-{epoch:03d}.ckpt"


def get_data(csv_paths: List[Path], classes: List[str], window_size: int = 100):
    """
    Get the data from the .csv files and create the training, validation and test sets.

    Args:
        csv_paths: The list of paths to the .csv files containing the pupillometry data.
        classes: The list of classes to be used in the output layer.
        window_size: The number of data samples to be considered at a time.

    Returns:
        The training, validation and test sets.
    """
    # Load the dataset from the .csv file
    dilations_dict = {}
    for c in classes:
        dilations_dict[c] = []

    for path in csv_paths:
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if match := re.search(
                    "(?P<id>\d+)_video_\d+\.\w+", row["names"]
                ):
                    dilations_dict[classes[int(match["id"]) - 1]].append(
                        float(row["diameters"])
                    )

    label = np.zeros((1, len(set(classes))))

    dilation_windows = []
    label_windows = []
    for emotion, dilations in dilations_dict.items():
        new_label = np.copy(label)
        new_label[0][list(set(classes)).index(emotion)] = 1.0
        num_windows = int(len(dilations) // window_size)
        for i in range(num_windows):
            dilation_windows.append(dilations[i * window_size : (i + 1) * window_size])
            label_windows.append(list(set(classes)).index(emotion))

    # Make a list of indices for the dataset
    indices = []
    for i in range(len(dilation_windows)):
        indices.append(i)
    # Shuffle the indices
    np.random.shuffle(indices)

    train_val_split = int(len(indices) * 0.6)
    val_test_split = int(len(indices) * 0.8)

    train_indices = indices[:train_val_split]
    val_indices = indices[train_val_split:val_test_split]
    test_indices = indices[val_test_split:]

    def make_dataset(dilations_set, labels_set, indices_set):
        shuffled_dilations = []
        shuffled_labels = []
        for idx in indices_set:
            shuffled_dilations.append(dilations_set[idx])
            shuffled_labels.append(labels_set[idx])

        dilations_t = tf.expand_dims(tf.convert_to_tensor(shuffled_dilations), 1)
        labels_t = tf.expand_dims(tf.convert_to_tensor(shuffled_labels), 1)

        # Last batch is dropped because it may not be the correct size
        return Dataset.from_tensor_slices((dilations_t, labels_t))

    train_set = make_dataset(dilation_windows, label_windows, train_indices)
    val_set = make_dataset(dilation_windows, label_windows, val_indices)
    test_set = make_dataset(dilation_windows, label_windows, test_indices)

    return train_set, val_set, test_set


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

    model.add(Rescaling(1.0 / 35))
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
    np.random.seed(496)
    tf.random.set_seed(496)

    csv_paths = []
    for file in os.listdir(sys.argv[1]):
        if re.search("pupil_\w+\.csv", Path(file).name):
            csv_paths.append(Path(sys.argv[1]) / file)

    classes = BINARY_CLASSES
    window_size = 100

    train_set, val_set, test_set = get_data(csv_paths, classes, window_size)

    input_shape = (window_size, 1)
    num_classes = len(set(classes))

    # Create the LSTM model
    model = create_model(num_classes, input_shape)

    # Training
    cp_callback = ModelCheckpoint(CHECKPOINT_PATH, save_weights_only=True, verbose=1)
    model.fit(train_set, validation_data=val_set, epochs=3, callbacks=[cp_callback])
