import os
import pytest
from pathlib import Path
from ..data_processing import separate_images_binary, separate_images_multiple
from ..crop_and_resize_images import crop_and_resize_image, crop_and_resize_images
from ..utils import Point, Region, Resolution

@pytest.fixture
def setup_folders(tmp_path):
    source_folder = tmp_path / "source"
    positive_folder = tmp_path / "positive"
    negative_folder = tmp_path / "negative"
    output_folders = [
        tmp_path / "anger",
        tmp_path / "sad",
        tmp_path / "fear",
        tmp_path / "happy",
        tmp_path / "fun",
        tmp_path / "calm",
        tmp_path / "joy"
    ]
    keywords = ["anger", "sad", "fear", "happy", "fun", "calm", "joy"]

    os.makedirs(source_folder, exist_ok=True)
    os.makedirs(positive_folder, exist_ok=True)
    os.makedirs(negative_folder, exist_ok=True)
    for folder in output_folders:
        os.makedirs(folder, exist_ok=True)

    # Create some dummy data
    dummy_data = [
        ("happy_video", ["happy_frame1.jpg", "happy_frame2.jpg"]),
        ("sad_video", ["sad_frame1.jpg", "sad_frame2.jpg"]),
        # Add more dummy data as needed
    ]

    for video, frames in dummy_data:
        video_folder = source_folder / video
        os.makedirs(video_folder, exist_ok=True)
        for frame in frames:
            open(video_folder / frame, 'a').close()

    return source_folder, positive_folder, negative_folder, output_folders, keywords

def test_separate_images_binary(setup_folders):
    source_folder, positive_folder, negative_folder, _, _ = setup_folders
    keyword = "positive"
    separate_images_binary(source_folder, positive_folder, negative_folder, keyword)

    # Assert that files are moved correctly to positive and negative folders
    assert len(os.listdir(positive_folder)) > 0
    assert len(os.listdir(negative_folder)) > 0

def test_separate_images_multiple(setup_folders):
    source_folder, _, _, output_folders, keywords = setup_folders
    separate_images_multiple(source_folder, output_folders, keywords)

    # Assert that files are moved correctly to output folders
    for folder in output_folders:
        assert len(os.listdir(folder)) > 0


#Make sure to replace your_module with the actual name of the module where your separate_images_binary and separate_images_multiple functions are defined.

#These tests use the pytest library and fixtures to set up a temporary folder structure for testing. The test_separate_images_binary and test_separate_images_multiple functions then call your separation functions and assert that the files are moved correctly.

#You can run the tests by executing the pytest command in your terminal, assuming you have pytest installed (pip install pytest).
