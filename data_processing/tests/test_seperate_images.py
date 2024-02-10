import os
import pytest
from pathlib import Path
import logging
from ..data_processing import separate_images_binary, separate_images_multiple
from ..crop_and_resize_images import crop_and_resize_image, crop_and_resize_images
from ..utils import Point, Region, Resolution

test_files_dir = Path(__file__).parent / "test_files" / "separate_images"


@pytest.fixture(autouse=True)
def set_logging_level(caplog):
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)


def setup_test_folders(setup_folders):
    """
    Create test directories and populate them with dummy image values.
    """
    for folder in setup_folders:
        os.makedirs(folder / "cropped", exist_ok=True)
        emotion_name = folder.stem.split("_")[
            1
        ]  # Extract emotion name from folder name
        # Create dummy image files with emotion name
        for i in range(5):
            with open(folder / f"cropped/image_{i}_{emotion_name}.jpg", "w") as f:
                f.write("Dummy image data")


@pytest.mark.parametrize(
    "setup_folders, output_folders",
    [
        (
            [
                test_files_dir / "test_happy",
                test_files_dir / "test_sad",
                test_files_dir / "test_fear",
                test_files_dir / "test_anger",
                test_files_dir / "test_fun",
                test_files_dir / "test_calm",
                test_files_dir / "test_joy",
            ],
            test_files_dir,
        ),
    ],
)
def test_separate_images_binary(setup_folders, output_folders, caplog):

    # Call the setup_test_folders function to prepare test directories
    setup_test_folders(setup_folders)

    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    positive_dir, negative_dir = separate_images_binary(setup_folders, output_folders)

    # Assert that files are moved correctly to positive and negative folders
    assert positive_dir.exists() and positive_dir.is_dir()
    assert negative_dir.exists() and negative_dir.is_dir()

    # Ensure the files were correctly moved
    assert len(os.listdir(positive_dir)) > 0
    assert len(os.listdir(negative_dir)) > 0

    # Ensure the files weren't deleted from source folders
    for folder in setup_folders:
        assert len(os.listdir(folder / "cropped")) > 0

    # Ensure that all files were moved to the correct folders
    positive_keywords = ["happy", "fun", "calm", "joy"]
    negative_keywords = ["anger", "sad", "fear"]

    for folder in setup_folders:
        for file in os.listdir(folder / "cropped"):
            if any(keyword in file for keyword in positive_keywords):
                assert (positive_dir / file).exists()
            elif any(keyword in file for keyword in negative_keywords):
                assert (negative_dir / file).exists()
            else:
                assert False, f"File {file} was not moved to the correct folder."

    # Ensure that positive folder contains no negative keyword images
    for file in os.listdir(positive_dir):
        assert not any(keyword in file for keyword in negative_keywords)

    for file in os.listdir(negative_dir):
        assert not any(keyword in file for keyword in positive_keywords)


@pytest.mark.parametrize(
    "setup_folders, output_folders",
    [
        (
            [
                test_files_dir / "test_happy",
                test_files_dir / "test_sad",
                test_files_dir / "test_fear",
                test_files_dir / "test_anger",
                test_files_dir / "test_fun",
                test_files_dir / "test_calm",
                test_files_dir / "test_joy",
            ],
            test_files_dir,
        ),
    ],
)
def test_separate_images_multiple(setup_folders, output_folders, caplog):

    # Call the setup_test_folders function to prepare test directories
    setup_test_folders(setup_folders)

    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    destination_paths = separate_images_multiple(setup_folders, output_folders)

    for path in destination_paths:
        assert path.exists() and path.is_dir()
        assert len(os.listdir(path)) > 0

    # Ensure the files weren't deleted from source folders
    for folder in setup_folders:
        assert len(os.listdir(folder / "cropped")) > 0

    # Ensure that all files in a foler have the same emotion as the folder name
    for folder in setup_folders:
        emotion_name = folder.stem.split("_")[1]
        for file in os.listdir(folder / "cropped"):
            assert emotion_name in file


# Test cases where folder doesn't exist
@pytest.mark.parametrize(
    "setup_folders, output_folders",
    [
        (
            [
                test_files_dir / "fake",
            ],
            test_files_dir,
        ),
    ],
)
def test_separate_fake_dir(setup_folders, output_folders, caplog):
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    logging.debug("Running separate fake dir test")

    with pytest.raises(FileNotFoundError) as e:
        separate_images_binary(source_dirs=setup_folders, output_dir=output_folders)

    assert str(e.value) == "Source folder {} does not exist".format(setup_folders[0])
