from pathlib import Path
from typing import List

from .crop_and_resize_images import crop_and_resize_images
from .utils import Point, Region, Resolution
from .video_to_images import extract_frames

TOP_LEFT = Point(100, 100)
BOTTOM_RIGHT = Point(324, 324)
RESOLUTION = Resolution(224, 224)

def data_processing(video_paths: List[Path]) -> List[Path]:
    for video in video_paths:
        image_paths = extract_frames(video, 1)
        image_paths = crop_and_resize_images(image_paths, Region(TOP_LEFT, BOTTOM_RIGHT), RESOLUTION)