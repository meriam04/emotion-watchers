#!/usr/bin/env python3

import csv
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import re
import sys
from typing import Dict, List

EXCLUSION_WORDS = ("transition",)
OUTPUT_FILE_FORMAT = "pupil_{}_{}.csv"

SEG_NAME_TO_EMOTION = {"1.mp4": "joy",
                       "2.mp4": "anger",
                       "3.mp4": "fear",
                       "4.mp4": "fun",
                       "5.mp4": "sad",
                       "6.mp4": "happy",
                       "7.mp4": "calm"}

@dataclass
class Segment:
    name: str
    start: float
    end: float

@dataclass
class DataPoint:
    time: float
    diameter: float
    seg_start: float

def process_participant(data_dir: Path, data_file: Path, segments_file: Path, inits: str):
    # TODO: Call process_data.m from python

    # Read the segments csv file
    segments: List[Segment] = []
    with open (segments_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(Segment(row["segmentName"],
                                    float(row["segmentStart"]) * 1000,
                                    float(row["segmentEnd"]) * 1000))

    # Read the data csv file
    curr_seg_idx = 0
    data: Dict[List[Dict]] = {segments[0].name: []}
    with open(data_file, 'r') as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get the current segment for each time
            time = float(row["times"])
            if time > segments[curr_seg_idx].end:
                curr_seg_idx += 1
                data[segments[curr_seg_idx].name] = []

            # Add the segment data to each data point
            data[segments[curr_seg_idx].name].append(
                asdict(DataPoint(time,
                       float(row["diameters"]),
                       segments[curr_seg_idx].start)))

    # Write the output csv files
    for seg_name, seg_data in data.items():
        exclude = False
        for word in EXCLUSION_WORDS:
            if word in seg_name:
                exclude = True
                break

        if not exclude:
            output_file = data_dir / OUTPUT_FILE_FORMAT.format(inits, SEG_NAME_TO_EMOTION[seg_name.strip()])
            with open(output_file, 'w') as f:
                writer = csv.DictWriter(f, seg_data[0].keys())
                writer.writeheader()
                writer.writerows(seg_data)

def process_data(data_dir: Path):
    # Iterate over all csv files in the data_dir
    csv_files = {}
    for file in os.listdir(data_dir):
        # If a matching data csv file is found add a new tuple for that participant
        if match := re.search("data_(?P<inits>\w+)\.csv", Path(file).name):
            csv_files[match["inits"]] = [data_dir / file, '']
        # If a matching segments csv file is found add it to the tuple for that participant
        elif match := re.search("segments_(?P<inits>\w+)\.csv", Path(file).name):
            csv_files[match["inits"]][1] = data_dir / file

    # Iterate over all found csv files
    for inits, files in csv_files.items():
        # Process each participants pupillometry data
        process_participant(data_dir, files[0], files[1], inits)

if __name__ == "__main__":
    process_data(Path(sys.argv[1]))
