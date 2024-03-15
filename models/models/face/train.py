from pathlib import Path
import sys
import tensorflow as tf
from tensorflow.data import AUTOTUNE
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
from typing import Optional, Tuple


CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-{epoch:03d}.ckpt"


def get_data(image_dir: Path, image_size: Tuple[int, int], batch_size: int = 32):
    """
    Get the data from the emotion directories and create the dataset.

    Args:
        image_dir: The directory containing the images.
        image_size: The size of the images in pixels (e.g. (224, 224)).
        batch_size: The batch size to be used in the training.

    Returns:
        The dataset, as well as the classes present in the image directory.
    """
    # Generate train and val set from directory
    dataset = image_dataset_from_directory(
        image_dir,
        batch_size=batch_size,
        image_size=image_size,
    )

    # Get the classes from the dataset
    classes = dataset.class_names

    # Prefetch datasets
    dataset = dataset.cache().shuffle(1000).prefetch(AUTOTUNE)

    return dataset, classes


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
    tf.random.set_seed(496)

    batch_size = 32
    image_shape = (224, 224, 3)

    train_set, classes = get_data(
        Path(sys.argv[1]) / "train", image_shape[0:2], batch_size
    )
    val_set, classes = get_data(
        Path(sys.argv[1]) / "val", image_shape[0:2], batch_size
    )

    num_classes = len(classes)

    # Create the CNN model
    model = create_model(num_classes, image_shape)

    # Training
    cp_callback = ModelCheckpoint(CHECKPOINT_PATH, save_weights_only=True, verbose=1)
    model.fit(train_set, validation_data=val_set, epochs=10, callbacks=[cp_callback])
