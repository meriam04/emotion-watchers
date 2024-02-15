import os
import pytest
from pathlib import Path
import logging

from data_processing.data_processing import separate_images

TEST_FILES_DIR = Path(__file__).parent / "test_files" / "separate_images"
TEAR_DOWN = True

"""
General Input Directory Info: There is one large dir with all data points inside
The data points are a participant plus an emotion
eg: /source_dir_cropped_images/kirti_happy.file

Output Directory Info: One large dir with all emotions as dirs
eg:
/source_dir
  -/happy
  -/sad
  -/fear
  -/anger
  -/fun
  -/calm
  -/joy
the emotion dirs have all participant data files within
eg:
/happy/kirti_happy.file
"""


@pytest.fixture(autouse=True)
def set_logging_level(caplog):
    """Set logging level to capture debug messages"""
    caplog.set_level(logging.DEBUG)


def setup_test_folders(setup_folders):
    """
    Create test directories and populate them with dummy image values.
    Each folder will have 5 images named image_0_emotion.jpg, image_1_emotion.jpg, etc.
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


def teardown_test_folders(setup_folders, output_folder):
    """
    Remove test directories and their contents
    """
    for folder in setup_folders:
        os.system(f"rm -rf {folder}")

    os.system(f"rm -rf {output_folder}")


@pytest.mark.parametrize(
    "setup_folders, output_folders",
    [
        (
            [
                TEST_FILES_DIR / "test_happy",
                TEST_FILES_DIR / "test_sad",
                TEST_FILES_DIR / "test_fear",
                TEST_FILES_DIR / "test_anger",
                TEST_FILES_DIR / "test_fun",
                TEST_FILES_DIR / "test_calm",
                TEST_FILES_DIR / "test_joy",
            ],
            TEST_FILES_DIR,
        ),
    ],
)
def test_separate_images_binary(setup_folders, output_folders, caplog):
    """
    Test for separate_images_binary function.
    Given a list of source directories, the function should move images to positive
    and negative folders based on their emotion.
    """

    # Call the setup_test_folders function to prepare test directories
    setup_test_folders(setup_folders)

    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    positive_dir, negative_dir = separate_images(
        setup_folders, output_folders, binary=True
    )

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

    if TEAR_DOWN:
        teardown_test_folders(setup_folders, output_folders)


@pytest.mark.parametrize(
    "setup_folders, output_folders",
    [
        (
            [
                TEST_FILES_DIR / "test_happy",
                TEST_FILES_DIR / "test_sad",
                TEST_FILES_DIR / "test_fear",
                TEST_FILES_DIR / "test_anger",
                TEST_FILES_DIR / "test_fun",
                TEST_FILES_DIR / "test_calm",
                TEST_FILES_DIR / "test_joy",
            ],
            TEST_FILES_DIR,
        ),
    ],
)
def test_separate_images_multiclass(setup_folders, output_folders, caplog):
    """
    Test for separate_images_multiple function.
    Given a list of source directories, the function should move images to folders
    based on their emotion.
    """

    # Call the setup_test_folders function to prepare test directories
    setup_test_folders(setup_folders)

    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    destination_paths = separate_images(setup_folders, output_folders, binary=False)

    for path in destination_paths:
        assert path.exists() and path.is_dir()
        assert len(os.listdir(path)) > 0

    # Ensure the files weren't deleted from source folders
    for folder in setup_folders:
        assert len(os.listdir(folder / "cropped")) > 0

    # Ensure that all files in a folder have the same emotion as the folder name
    for folder in setup_folders:
        emotion_name = folder.stem.split("_")[1]
        for file in os.listdir(folder / "cropped"):
            assert emotion_name in file

    if TEAR_DOWN:
        teardown_test_folders(setup_folders, output_folders)


@pytest.mark.parametrize(
    "setup_folders, output_folders, error_type, error_msg",
    [
        (
            [TEST_FILES_DIR / "fake"],
            TEST_FILES_DIR,
            FileNotFoundError,
            "Source folder {} does not exist".format(TEST_FILES_DIR / "fake"),
        ),
        (
            [TEST_FILES_DIR, TEST_FILES_DIR / "fake"],  # One real and one fake folder
            TEST_FILES_DIR,
            FileNotFoundError,
            "Source folder {} does not exist".format(TEST_FILES_DIR / "fake"),
        ),
    ],
)
def test_separate_fake_dir(
    setup_folders, output_folders, error_type, error_msg, caplog
):
    """
    Test for a fake source directory that doesn't exist when passed to separate_images_binary
    """
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    logging.debug("Running separate fake dir test")

    with pytest.raises(FileNotFoundError) as e:
        separate_images(source_dirs=setup_folders, output_dir=output_folders)

        assert e.type == error_type
        assert str(e.value) == error_msg


@pytest.mark.parametrize(
    "setup_folders, output_folders, error_type, error_msg",
    [
        (
            [
                TEST_FILES_DIR / "test_happy",
                TEST_FILES_DIR / "test_sad",
                TEST_FILES_DIR / "test_fear",
                TEST_FILES_DIR / "test_anger",
                TEST_FILES_DIR / "test_fun",
                TEST_FILES_DIR / "test_calm",
                TEST_FILES_DIR / "test_joy",
            ],
            TEST_FILES_DIR,
            FileNotFoundError,
            "Source folder does not contain a 'cropped' directory, skipping.",
        ),
    ],
)
def test_separate_no_cropped_dir(
    setup_folders, output_folders, error_type, error_msg, caplog
):
    """
    Test for a source directory that exists but doesn't contain a cropped subdirectory
    """
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    logging.debug("Running separate no cropped dir test")

    setup_test_folders(setup_folders)

    # Remove the cropped subdirectory from the first folder
    os.system(f"rm -rf {setup_folders[0] / 'cropped'}")

    logging.debug("Removed cropped dir")
    logging.debug(os.listdir(setup_folders[0]))

    with pytest.raises(FileNotFoundError) as e:
        separate_images(source_dirs=setup_folders, output_dir=output_folders)

        assert e.type == error_type
        assert str(e.value) == error_msg

    if TEAR_DOWN:
        teardown_test_folders(setup_folders, output_folders)
