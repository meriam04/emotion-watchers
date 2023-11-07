#!/usr/bin/env python3

import cv2
import os
from pathlib import Path
from typing import List

from .utils import Region

def crop_image(image_path: Path, crop_region: Region) -> Path:
    """
    This function crops an image using the specified crop region.
    It expects a region to be defined.\n
    It returns the path to the cropped image.
    """

    image = cv2.imread(str(image_path))
    cropped_image = image[crop_region.top_left.y:crop_region.bottom_right.y, crop_region.top_left.x:crop_region.bottom_right.x]
    
    cropped_dir = image_path.parent / "cropped"
    if not cropped_dir.exists():
        os.makedirs(cropped_dir)
    
    cropped_image_path = cropped_dir / Path(f"{image_path.stem}_cropped.png")
    
    cv2.imwrite(str(cropped_image_path), cropped_image)
    
    return cropped_image_path

def crop_images(image_paths: List[Path], crop_region: Region) -> List[Path]:
    """
    This function crops a series of images using the specified crop region.
    It expects a region to be defined.\n
    It returns the paths to the cropped images.
    """

    clipped_image_paths = []
    for image_path in image_paths:
        clipped_image_path = crop_image(image_path, crop_region)
        clipped_image_paths.append(clipped_image_path)
    return clipped_image_paths
