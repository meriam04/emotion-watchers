#!/usr/bin/env python3

from moviepy.editor import VideoFileClip
import os
from pathlib import Path
import sys
from typing import List

video_formats = (".mov", ".mp4", ".wav")


def extract_frames(
    video: Path,
    times: List[float],
    image_dir: Path = Path(__file__).parent / "images",
    inclusion_rate: int = 1
) -> List[Path]:
    """
    This function extracts the frames of the specified video.
    It expects a rate in frames per second.\n
    It returns a list of paths to the extracted frames.
    """

    if not video.exists():
        raise Exception("Error: video does not exist")

    if not video.is_file() and video.suffix in video_formats:
        raise Exception("Error: video is not a video file")

    if not image_dir.exists():
        os.makedirs(image_dir)

    clip = VideoFileClip(video.absolute().as_posix())
    image_paths = []
    for i in range(0, len(times), inclusion_rate):
        time = (times[i] - times[0]) / 1000
        image_path = image_dir / Path(f"{video.stem}_{time}.png")
        clip.save_frame(image_path, time)
        image_paths.append(image_path)

    return image_paths


if __name__ == "__main__":
    extract_frames(Path(sys.argv[1]), int(sys.argv[2]))
