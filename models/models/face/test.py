from pathlib import Path
import sys
import tensorflow as tf

from models.face.train import create_model, get_data

BINARY_CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/binary-010.ckpt"
MULTICLASS_CHECKPOINT_PATH = Path(__file__).parent / "checkpoints/multiclass-009.ckpt"

if __name__ == "__main__":
    # fix random seed for reproducibility
    tf.random.set_seed(496)

    batch_size = 32
    image_shape = (224, 224, 3)

    test_set, classes = get_data(
        Path(sys.argv[1]) / "test", image_shape[0:2], batch_size
    )

    num_classes = len(classes)

    # Create the CNN model
    model = create_model(num_classes, image_shape)
    model.load_weights(BINARY_CHECKPOINT_PATH if len(classes) == 2 else MULTICLASS_CHECKPOINT_PATH)

    # Testing
    model.evaluate(test_set)
