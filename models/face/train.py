import numpy as np
from pathlib import Path
import re
import sys
import tensorflow as tf
from tensorflow.data import AUTOTUNE
from tensorflow.data.experimental import cardinality
from tensorflow.keras.callbacks import ModelCheckpoint
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import (
    Conv2D,
    Dense,
    Flatten,
    Input,
    MaxPooling2D,
    Rescaling,
)
from tensorflow.keras.utils import image_dataset_from_directory
from typing import List, Optional, Tuple


CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-{epoch:03d}.ckpt"


def get_individual_sets(samples, test_indices):
    """
    Get the indices of the samples that belong to the same individual.

    Args:
        samples: The list of samples.
        test_indices: The indices of the samples in the test set.

    Returns:
        A dictionary with the indices of the samples that belong to the same individual.
    """
    individual_sets = {}
    for test_idx in test_indices:
        # Expects files of the format:
        # <emotion_id>_<initial>_<emotion_name>_<second_in_video>_c.png
        # Example: 1_cs_joy_1.0_c.png
        individual = re.search(
            ".*\d_(?P<individual>\w+)_\w+_\d+\.\d+_c\.png", samples[test_idx][0]
        )["individual"]
        if individual not in individual_sets:
            individual_sets[individual] = []
        individual_sets[individual].append(test_idx)
    return individual_sets


def get_data(image_dir: List[Path], image_size: Tuple[int, int], batch_size: int = 32):
    """
    Get the data from the emotion directories and create the training, validation and test sets.

    Args:
        image_dir: The list of directories containing the images.
        image_size: The size of the images in pixels (e.g. (224, 224)).
        batch_size: The batch size to be used in the training.

    Returns:
        The training, validation and test sets, as well as the classes present in the image directory.
    """
    # Generate train and val set from directory
    train_set = image_dataset_from_directory(
        image_dir,
        batch_size=batch_size,
        image_size=image_size,
        seed=496,
        validation_split=0.4,
        subset="training",
    )
    val_set = image_dataset_from_directory(
        image_dir,
        batch_size=batch_size,
        image_size=image_size,
        seed=496,
        validation_split=0.4,
        subset="validation",
    )

    # Split val set into val and test set
    val_split = cardinality(val_set) // 2
    test_set = val_set.take(val_split)
    val_set = val_set.skip(val_split)

    # Get the classes from the dataset
    classes = train_set.class_names

    # Prefetch datasets
    train_set = train_set.cache().shuffle(1000).prefetch(AUTOTUNE)
    val_set = val_set.cache().prefetch(AUTOTUNE)
    test_set = test_set.cache().prefetch(AUTOTUNE)

    return train_set, val_set, test_set, classes


def create_model(num_classes: int, input_shape: Optional[Tuple[int, int, int]] = None):
    """
    Create the CNN model for the facial expression images.

    Args:
        num_classes: The number of classes in the output layer.
        input_shape: The shape of the input images (e.g. (224, 224)).

    Returns:
        The CNN model.
    """
    model = Sequential()

    if input_shape:
        model.add(Input(input_shape))

    model.add(Rescaling(1.0 / 255))
    model.add(Conv2D(32, 3, activation="relu"))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, 3, activation="relu"))
    model.add(MaxPooling2D())
    model.add(Conv2D(32, 3, activation="relu"))
    model.add(MaxPooling2D())
    model.add(Flatten())
    model.add(Dense(128, "relu"))

    if num_classes == 2:
        # Binary classification
        model.add(Dense(num_classes))
        loss = tf.keras.losses.SparseCategoricalCrossentropy(from_logits=True)
    else:
        # Multiclass classification
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

    batch_size = 32
    image_shape = (224, 224, 3)

    train_set, val_set, test_set, classes = get_data(
        Path(sys.argv[1]), image_shape[0:2], batch_size
    )

    num_classes = len(classes)

    # Create the CNN model
    model = create_model(num_classes, image_shape)

    # Training
    cp_callback = ModelCheckpoint(CHECKPOINT_PATH, save_weights_only=True, verbose=1)
    model.fit(train_set, validation_data=val_set, epochs=10, callbacks=[cp_callback])
