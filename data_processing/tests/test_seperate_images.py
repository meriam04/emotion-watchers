import os
import pytest
from pathlib import Path
import logging
from ..data_processing import separate_images_binary, separate_images_multiple
from ..crop_and_resize_images import crop_and_resize_image, crop_and_resize_images
from ..utils import Point, Region, Resolution

test_files_dir = Path(__file__).parent / "test_files"


@pytest.fixture(autouse=True)
def set_logging_level(caplog):
    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)


@pytest.fixture
def setup_folders(tmp_path):
    source_folder = test_files_dir / "cropped"
    positive_folder = tmp_path / "positive"
    negative_folder = tmp_path / "negative"
    output_folders = [
        tmp_path / "anger",
        tmp_path / "sad",
        tmp_path / "fear",
        tmp_path / "happy",
        tmp_path / "fun",
        tmp_path / "calm",
        tmp_path / "joy",
    ]
    keywords = ["anger", "sad", "fear", "happy", "fun", "calm", "joy"]

    os.makedirs(source_folder, exist_ok=True)
    os.makedirs(positive_folder, exist_ok=True)
    os.makedirs(negative_folder, exist_ok=True)
    for folder in output_folders:
        os.makedirs(folder, exist_ok=True)

    # Create some dummy data
    # dummy_data = [
    # ("happy_video", ["happy_frame1.jpg", "happy_frame2.jpg"]),
    # ("sad_video", ["sad_frame1.jpg", "sad_frame2.jpg"]),
    # Add more dummy data as needed
    # ]

    # for video, frames in dummy_data:
    #     video_folder = source_folder / video
    #     os.makedirs(video_folder, exist_ok=True)
    #     for frame in frames:
    #         open(video_folder / frame, 'a').close()

    # return source_folder, positive_folder, negative_folder, output_folders, keywords


@pytest.mark.parametrize(
    "setup_folders, output_folders, keywords",
    [([test_files_dir, test_files_dir, "positive"])],
)
def test_separate_images_binary(setup_folders, output_folders, keywords, caplog):

    # Set logging level to capture debug messages
    caplog.set_level(logging.DEBUG)

    # Make these the parameters.
    # source_folder, positive_folder, negative_folder, _, _ = setup_folders
    keywords = "positive"
    positive_dir, negative_dir = separate_images_binary(
        setup_folders, output_folders, keywords
    )

    # Assert that files are moved correctly to positive and negative folders
    assert positive_dir.exists() and positive_dir.is_dir()
    assert negative_dir.exists() and negative_dir.is_dir()

    assert True is False

    # Assert that files are moved correctly to positive and negative folders
    # assert len(os.listdir(positive_folder)) > 0
    # assert len(os.listdir(negative_folder)) > 0

    # os.makedirs(source_folder, exist_ok=True)
    # os.makedirs(positive_folder, exist_ok=True)
    # os.makedirs(negative_folder, exist_ok=True)
    # for folder in output_folders:
    #     os.makedirs(folder, exist_ok=True)

    # return source_folder, positive_folder, negative_folder, output_folders, keywords


# def test_separate_images_multiple(setup_folders):
#     source_folder, _, _, output_folders, keywords = setup_folders
#     separate_images_multiple(source_folder, output_folders, keywords)

#     # Assert that files are moved correctly to output folders
#     for folder in output_folders:
#         assert len(os.listdir(folder)) > 0


# #Make sure to replace your_module with the actual name of the module where your separate_images_binary and separate_images_multiple functions are defined.

# #These tests use the pytest library and fixtures to set up a temporary folder structure for testing. The test_separate_images_binary and test_separate_images_multiple functions then call your separation functions and assert that the files are moved correctly.

# #You can run the tests by executing the pytest command in your terminal, assuming you have pytest installed (pip install pytest).

# import os
# import shutil
# import pytest
# import logging
# from pathlib import Path
# from ..data_processing import separate_images_binary, separate_images_multiple

# # Define test data directories
# TEST_FILES_DIR = Path(__file__).parent / "test_files"
# SOURCE_FOLDER = TEST_FILES_DIR / "source"
# POSITIVE_FOLDER = TEST_FILES_DIR / "positive"
# NEGATIVE_FOLDER = TEST_FILES_DIR / "negative"
# OUTPUT_FOLDERS = [
#     TEST_FILES_DIR / "output" / "anger",
#     TEST_FILES_DIR / "output" / "sad",
#     TEST_FILES_DIR / "output" / "fear",
#     TEST_FILES_DIR / "output" / "happy",
#     TEST_FILES_DIR / "output" / "fun",
#     TEST_FILES_DIR / "output" / "calm",
#     TEST_FILES_DIR / "output" / "joy",
# ]
# KEYWORDS = ["anger", "sad", "fear", "happy", "fun", "calm", "joy"]


# @pytest.fixture
# def setup_test_data():
#     # Create test directories and files
#     os.makedirs(SOURCE_FOLDER, exist_ok=True)
#     os.makedirs(POSITIVE_FOLDER, exist_ok=True)
#     os.makedirs(NEGATIVE_FOLDER, exist_ok=True)
#     for folder in OUTPUT_FOLDERS:
#         os.makedirs(folder, exist_ok=True)

#     yield  # This is where the test runs

#     # Cleanup after the test
#     shutil.rmtree(SOURCE_FOLDER)
#     shutil.rmtree(POSITIVE_FOLDER)
#     shutil.rmtree(NEGATIVE_FOLDER)
#     for folder in OUTPUT_FOLDERS:
#         shutil.rmtree(folder)


# def test_separate_images_binary(setup_test_data):

#     separate_images_binary(SOURCE_FOLDER, POSITIVE_FOLDER, NEGATIVE_FOLDER, "happy")
#     # Debugging: Print out the contents of POSITIVE_FOLDER
#     print("Contents of POSITIVE_FOLDER:", os.listdir(POSITIVE_FOLDER))

#     # Assert that files are moved correctly to positive and negative folders
#     assert len(os.listdir(POSITIVE_FOLDER)) > 0
#     assert len(os.listdir(NEGATIVE_FOLDER)) > 0

#     # Check if SOURCE_FOLDER contains a folder named "cropped"
#     assert "cropped" in os.listdir(SOURCE_FOLDER)


# def test_separate_images_multiple(setup_test_data):
#     separate_images_multiple(SOURCE_FOLDER, OUTPUT_FOLDERS, KEYWORDS)
#     # Assert that files are moved correctly to output folders
#     for folder in OUTPUT_FOLDERS:
#         assert len(os.listdir(folder)) > 0

#     # Check if SOURCE_FOLDER contains a folder named "cropped"
#     assert "cropped" in os.listdir(SOURCE_FOLDER)
