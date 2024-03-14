#!/usr/bin/env python3

# TODO: Delete this

import cv2
import os
from pathlib import Path
from typing import List, Optional

from data_processing.utils import Point, Region, Resolution


def crop_and_resize_image(
    image_path: Path, crop_region: Optional[Region], resolution: Resolution
) -> Path:
    """
    This function crops an image using the specified crop region.
    It expects a region to be defined.\n
    It returns the path to the cropped image.
    """

    image = cv2.imread(str(image_path))

    if not crop_region:
        height, width, _ = image.shape
        top_left = Point(
            (width - resolution.width) // 2, (height - resolution.height) // 2
        )
        bottom_right = Point(
            top_left.x + resolution.width, top_left.y + resolution.height
        )
        crop_region = Region(top_left, bottom_right)

    cropped_image = image[
        crop_region.top_left.y : crop_region.bottom_right.y,
        crop_region.top_left.x : crop_region.bottom_right.x,
    ]
    resized_image = cv2.resize(cropped_image, (resolution.width, resolution.height))

    cropped_dir = image_path.parent / "cropped"
    if not cropped_dir.exists():
        os.makedirs(cropped_dir)

    cropped_image_path = cropped_dir / Path(f"{image_path.stem}_c.png")

    cv2.imwrite(str(cropped_image_path), resized_image)

    return cropped_image_path


def crop_and_resize_images(
    image_paths: List[Path], crop_region: Optional[Region], resolution: Resolution
) -> List[Path]:
    """
    This function crops a series of images using the specified crop region.
    It expects a region to be defined.\n
    It returns the paths to the cropped images.
    """

    clipped_image_paths = []
    for image_path in image_paths:
        clipped_image_path = crop_and_resize_image(image_path, crop_region, resolution)
        clipped_image_paths.append(clipped_image_path)
    return clipped_image_paths
