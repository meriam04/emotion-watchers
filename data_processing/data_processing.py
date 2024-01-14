#!/usr/bin/env python3

from pathlib import Path
import sys
from typing import List

from crop_and_resize_images import crop_and_resize_images
from utils import Point, Region, Resolution
from video_to_images import extract_frames

RATE = 1
TOP_LEFT = Point(430, 80)
BOTTOM_RIGHT = Point(930, 580)
RESOLUTION = Resolution(224, 224)

def data_processing(video_path: Path, output_path: Path) -> List[Path]:
    image_paths = extract_frames(video_path, RATE, output_path)
    return crop_and_resize_images(image_paths, Region(TOP_LEFT, BOTTOM_RIGHT), RESOLUTION)

if __name__ == "__main__":
    data_processing(Path(sys.argv[1]), Path(sys.argv[2]))
