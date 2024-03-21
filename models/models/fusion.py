import csv
import numpy as np
import os
from pathlib import Path
import pickle
from PIL import Image
import re
import sys
import tensorflow as tf
from tensorflow.data import AUTOTUNE, Dataset
from tensorflow.keras.utils import img_to_array
from typing import Tuple

from data_processing.process_data import BINARY_EMOTIONS, TIMES_FILE_FORMAT
import models.face as face
import models.pupil as pupil

def get_data(pkl_dir: Path, face_dir: Path, image_shape: Tuple[int, int], window_size: int = 100):
    """
    Get the functions from the .pkl files and timestamps from the face directories, then create the dataset.

    Args:
        pkl_dir: The path to the directory of .pkl files containing the pupillometry splines.
        face_dir: The path to the directory of face images (for getting the times files)
        window_size: The number of data samples to be considered at a time.
        batch_size: The batch size to be used in the training.

    Returns:
        The dataset and the label classes.
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
    images = []
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
                        if end_time < pupil.PERIOD * window_size:
                            continue

                        # Get the image for the time
                        image = Image.open(face_dir / label / f"{inits}_{emotion}_{end_time}_c.png")
                        image = image.resize(image_shape)
                        images.append(img_to_array(image))

                        # Generate a window for this time
                        times = np.linspace(end_time - pupil.PERIOD * window_size, end_time, window_size)
                        dilation_windows.append(spline(times))
                        labels.append(i)

    # Convert the dilations and labels to a tensor dataset
    images_t = tf.convert_to_tensor(images)
    dilations_t = tf.convert_to_tensor(dilation_windows)
    labels_t = tf.convert_to_tensor(labels)
    dataset = Dataset.from_tensor_slices((images_t, dilations_t, labels_t))

    # Prefetch datasets
    dataset = dataset.batch(1).cache().shuffle(1000).prefetch(AUTOTUNE)

    return dataset, classes

if __name__ == "__main__":
    # fix random seed for reproducibility
    tf.random.set_seed(496)

    window_size = 100
    image_shape = (224, 224, 3)

    # Get the dataset and classes
    test_set, classes = get_data(Path(sys.argv[1]), Path(sys.argv[2]), image_shape[0:2], window_size)

    input_shape = (window_size, 1)
    num_classes = len(classes)

    # Create the models
    face_model = face.create_model(num_classes, image_shape)
    pupil_model = pupil.create_model(2, input_shape)

    # Load the weights
    face_model.load_weights(face.BINARY_CHECKPOINT_PATH if len(classes) == 2 else face.MULTICLASS_CHECKPOINT_PATH)
    pupil_model.load_weights(pupil.CHECKPOINT_PATH)

    # Get the accuracy on the test set
    correct = 0
    for face_image, pupil_window, label in test_set:
        face_prediction = face_model.predict(face_image)
        pupil_prediction = pupil_model.predict(pupil_window)

        if len(classes) != 2:
            multiclass_pupil_prediction = []
            for v in BINARY_EMOTIONS.values():
                if v == "negative":
                    multiclass_pupil_prediction.append(pupil_prediction[0][0])
                else:
                    multiclass_pupil_prediction.append(pupil_prediction[0][1])
            pupil_prediction = multiclass_pupil_prediction

        # Check that the label matches the emotion with the highest probability
        if np.argmax(face_prediction + pupil_prediction) == label:
            correct += 1

    print(f"Test accuracy: {correct/len(test_set)}")
