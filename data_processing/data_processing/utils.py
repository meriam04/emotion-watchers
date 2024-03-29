# TODO: Delete this

from dataclasses import dataclass
from typing import Tuple

@dataclass
class Point:
    x: int
    y: int

@dataclass
class Region:
    top_left: Point
    bottom_right: Point

@dataclass
class Resolution:
    height: int
    width: int
