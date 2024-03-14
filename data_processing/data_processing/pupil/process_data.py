#!/usr/bin/env python3

import csv
from dataclasses import asdict, dataclass
import os
from pathlib import Path
import pickle
import re
from scipy.interpolate import CubicSpline
import sys
from typing import Dict, List

EXCLUSION_WORDS = ("transition",)
OUTPUT_FILE_FORMAT = "pupil_{}_{}.pkl"

SEG_NAME_TO_EMOTION = {
    "1.mp4": "joy",
    "2.mp4": "anger",
    "3.mp4": "fear",
    "4.mp4": "fun",
    "5.mp4": "sad",
    "6.mp4": "happy",
    "7.mp4": "calm",
}


@dataclass
class Segment:
    name: str
    start: float
    end: float


def process_participant(
    data_dir: Path, data_file: Path, segments_file: Path, inits: str
):
    # TODO: Call process_data.m from python

    # Read the segments csv file
    segments: List[Segment] = []
    with open(segments_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            segments.append(
                Segment(
                    row["segmentName"],
                    float(row["segmentStart"]) * 1000,
                    float(row["segmentEnd"]) * 1000,
                )
            )

    # Read the data csv file
    curr_seg_idx = 0
    data: Dict[Dict[List[float], List[float]]] = {segments[0].name: {"times": [], "diameters": []}}
    with open(data_file, "r") as f:
        reader = csv.DictReader(f)
        for row in reader:
            # Get the current segment for each time
            time = float(row["times"])
            if time > segments[curr_seg_idx].end:
                curr_seg_idx += 1
                data[segments[curr_seg_idx].name] = {"times": [], "diameters": []}

            # Add the data point to the current segment
            data[segments[curr_seg_idx].name]["times"].append(time - segments[curr_seg_idx].start)
            data[segments[curr_seg_idx].name]["diameters"].append(float(row["diameters"]))

    # Write the output csv files
    for seg_name, seg_data in data.items():
        exclude = False
        for word in EXCLUSION_WORDS:
            if word in seg_name:
                exclude = True
                break

        if not exclude:
            output_file = data_dir / OUTPUT_FILE_FORMAT.format(
                inits, SEG_NAME_TO_EMOTION[seg_name.strip()]
            )

            # Cubic smoothing
            cspline = CubicSpline(seg_data["times"], seg_data["diameters"])

            '''
            TODO: Implement option to graph the data and save it in a separate directory

            import matplotlib.pyplot as plt
            import numpy as np
            plt.clf()
            xnew = np.linspace(0, seg_data["times"][-1], num=1001)
            plt.plot(xnew, cspline(xnew), 'o', label='spline')
            plt.plot(seg_data["times"], seg_data["diameters"], 'k', label='discrete')
            plt.savefig(f'./{output_file}.png')
            '''

            with open(output_file, 'wb') as f:
                pickle.dump(cspline, f)


def process_data(data_dir: Path):
    # Iterate over all csv files in the data_dir
    csv_files = {}
    for file in os.listdir(data_dir):
        # If a matching data csv file is found add a new tuple for that participant
        if match := re.search("data_(?P<inits>\w+)\.csv", Path(file).name):
            csv_files[match["inits"]] = [data_dir / file, ""]
        # If a matching segments csv file is found add it to the tuple for that participant
        elif match := re.search("segments_(?P<inits>\w+)\.csv", Path(file).name):
            csv_files[match["inits"]][1] = data_dir / file

    # Iterate over all found csv files
    for inits, files in csv_files.items():
        # Process each participants pupillometry data
        process_participant(data_dir, files[0], files[1], inits)


if __name__ == "__main__":
    process_data(Path(sys.argv[1]))
