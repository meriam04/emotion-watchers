from pathlib import Path
import pytest

from ..video_to_images import extract_frames

test_files_dir = Path(__file__).parent / "test_files"

@pytest.mark.parametrize("test_video, test_rate, expected_num_images,",
    [(test_files_dir / "keyboard_cat.mp4", 1, 54),
     (test_files_dir / "keyboard_cat.mp4", 2, 109),
     (test_files_dir / "keyboard_cat.mp4", 3, 163),])
def test_extract_frames(test_video, test_rate, expected_num_images):
    image_paths = extract_frames(test_video, test_rate, test_files_dir / "images")
    assert len(image_paths) == expected_num_images

    for image_path in image_paths:
        assert image_path.exists() and image_path.is_file()

@pytest.mark.parametrize("test_video,",
    [("dne.mp4"),
     (Path(__file__).parent),
     (Path(__file__))])
def test_nonexistent_video(test_video):
    with pytest.raises(Exception):
        extract_frames(test_video, 1, test_files_dir / "images")
