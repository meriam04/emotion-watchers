from pathlib import Path
import pytest

from ..crop_images import crop_image, crop_images
from ..utils import Point, Region

@pytest.mark.parametrize("test_image, test_region, expected_image,",
    [(Path(__file__).parent / "happy_man.png", Region(Point(100, 100), Point(400, 400)), Path(__file__).parent / "cropped/happy_man_cropped.png"),])
def test_crop_image(test_image, test_region, expected_image):
    assert crop_image(test_image, test_region) == expected_image
    assert expected_image.exists() and expected_image.is_file()

@pytest.mark.parametrize("test_images, test_region, expected_images,",
    [([Path(__file__).parent / "happy_man.png", Path(__file__).parent / "excited_woman.png"], Region(Point(100, 100), Point(324, 324)), [Path(__file__).parent / "cropped/happy_man_cropped.png", Path(__file__).parent / "cropped/excited_woman_cropped.png"]),])
def test_crop_images(test_images, test_region, expected_images):
    image_paths = crop_images(test_images, test_region)
    assert len(image_paths) == len(expected_images)

    for i, image_path in enumerate(image_paths):
        assert image_path.exists() and image_path.is_file()
        assert image_path == expected_images[i]
