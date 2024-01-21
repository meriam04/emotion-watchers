from pathlib import Path
import pytest

from ..crop_and_resize_images import crop_and_resize_image, crop_and_resize_images
from ...utils import Point, Region, Resolution

test_files_dir = Path(__file__).parent / "test_files"


@pytest.mark.parametrize(
    "test_image, test_region, test_resolution, expected_image,",
    [
        (
            test_files_dir / "happy_man.png",
            Region(Point(200, 100), Point(500, 400)),
            Resolution(224, 224),
            test_files_dir / "cropped/happy_man_c.png",
        ),
    ],
)
def test_crop_and_resize_image(
    test_image, test_region, test_resolution, expected_image
):
    assert (
        crop_and_resize_image(test_image, test_region, test_resolution)
        == expected_image
    )
    assert expected_image.exists() and expected_image.is_file()


@pytest.mark.parametrize(
    "test_images, test_region, test_resolution, expected_images,",
    [
        (
            [test_files_dir / "happy_man.png", test_files_dir / "excited_woman.png"],
            Region(Point(150, 50), Point(500, 400)),
            Resolution(224, 224),
            [
                test_files_dir / "cropped/happy_man_c.png",
                test_files_dir / "cropped/excited_woman_c.png",
            ],
        ),
        (
            [test_files_dir / "happy_man.png", test_files_dir / "excited_woman.png"],
            Region(Point(200, 200), Point(250, 250)),
            Resolution(224, 224),
            [
                test_files_dir / "cropped/happy_man_c.png",
                test_files_dir / "cropped/excited_woman_c.png",
            ],
        ),
        (
            [test_files_dir / "happy_man.png", test_files_dir / "excited_woman.png"],
            None,
            Resolution(224, 224),
            [
                test_files_dir / "cropped/happy_man_c.png",
                test_files_dir / "cropped/excited_woman_c.png",
            ],
        ),
    ],
)
def test_crop_and_resize_images(
    test_images, test_region, test_resolution, expected_images
):
    image_paths = crop_and_resize_images(test_images, test_region, test_resolution)
    assert len(image_paths) == len(expected_images)

    for i, image_path in enumerate(image_paths):
        assert image_path.exists() and image_path.is_file()
        assert image_path == expected_images[i]
