import os
import pytest
from pathlib import Path
import logging
from data_processing.data_processing import (
    separate_images_binary,
    separate_images_multiple,
)
from face.crop_and_resize_images import crop_and_resize_image, crop_and_resize_images
from utils import Point, Region, Resolution

test_files_dir = Path(__file__).parent / "test_files" / "separate_images"

"""
General Input Directory Info: There is one large dir with all datapoints inside
The datapoints are a particiapnt plus an emotion
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
    """
    Test for separate_images_binary function.
    Given a list of source directories, the function should move images to positive
    and negative folders based on their emotion.
    """

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
    """
    Test for separate_images_multiple function.
    Given a list of source directories, the function should move images to folders
    based on their emotion.
    """

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
    """
    Test for a fake source directory that doesn't exist when passed to separate_images_binary
    """
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    logging.debug("Running separate fake dir test")

    with pytest.raises(FileNotFoundError) as e:
        separate_images_binary(source_dirs=setup_folders, output_dir=output_folders)

    assert str(e.value) == "Source folder {} does not exist".format(setup_folders[0])


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
def test_multiclass_dir_not_exist(tmp_path):
    """
    Test for multiclass where the source directory doesn't exist when passed to
    separate_images_multiple
    """

    # Using the source directory and creating a temporary output directory
    output_dir = tmp_path / "source_dir"

    # Creating a non-existant directory, not existing or based off source
    non_existent_source_dir = tmp_path / "non_existent_dir"

    # Calling separate_images_multiple from data_processing and checking that non-existent
    # directory is not found
    # Assert a FileNotFoundError when trying to process the non-existent source directory
    try:
        separate_images_multiple([non_existent_source_dir], output_dir)
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError


def test_source_dir_no_cropped_subdir_multiclass(tmp_path):
    """
    Test for multi-class where the source directory exists but it doesn't contain a
    cropped subdirectory
    """

    # Using the source directory and creating a temporary output directory
    output_dir = tmp_path / "source_dir"
    os.makedirs(output_dir)

    # Creating a temporary source directory
    source_dir = tmp_path / "existing_source"
    os.makedirs(source_dir)

    # Making a dummy file in the source directory (without "cropped" subdirectory),
    # we don't need a real image here
    with open(source_dir / "example_image.jpg", "w"):
        pass

    # Calling separate_images_multiple from data_processing and checking that file is
    # not found if it does not have cropped
    with pytest.raises(FileNotFoundError):
        separate_images_multiple([source_dir], output_dir)

    # Ensuring the output directories for each emotion are not created
    emotions = ["happy", "fun", "calm", "joy", "anger", "sad", "fear"]
    for emotion in emotions:
        emotion_dir = output_dir / emotion
        assert not os.path.isdir(emotion_dir)

    # Making sure the source directory exists and crop does not
    assert "source_dir" in os.listdir(tmp_path)
    assert "cropped" not in os.listdir(tmp_path)


def test_binary_dir_not_exist(tmp_path):
    """
    A test for binary class where one of the source directories exists and another doesn't
    """
    # Creating a temporary output directory for binary output
    output_dir = tmp_path / "binary_output"
    os.makedirs(output_dir)

    # Creating a temporary source directory
    existing_source_dir = tmp_path / "existing_source"
    os.makedirs(existing_source_dir)

    # Creating a temporary source directory which is non-existent
    non_existent_source_dir = tmp_path / "non_existent_source"

    # Calling separate_images_binary from data_processing with both directories
    # (existing and non-existing)
    # If FileNotFoundError is raised it indicates that the 'non_existent_source_dir' doesn't exist
    # Assert that exception raised is FileNotFoundError
    try:
        separate_images_binary(
            [existing_source_dir, non_existent_source_dir], output_dir
        )
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError


def test_source_dir_no_cropped_subdir_binary(tmp_path):
    """
    Test for binary class where the source directory exists but it doesn't contain a
    cropped subdirectory
    """
    # Creating a temporary output directory for binary output
    output_dir = tmp_path / "binary_output"
    os.makedirs(output_dir)

    # Creating a temporary source directory
    source_dir = tmp_path / "existing_source"
    os.makedirs(source_dir)

    # Making a dummy file in the source directory (without "cropped" subdirectory),
    # we don't need a real image here
    with open(source_dir / "example_image.jpg", "w", encoding="utf-8"):
        pass

    # Call separate_images_binary with the existing source directory
    try:
        separate_images_binary([source_dir], output_dir)
    except FileNotFoundError as e:
        assert type(e) == FileNotFoundError

    # Making sure the source directory exists and crop does not
    assert "cropped" not in os.listdir(output_dir)
