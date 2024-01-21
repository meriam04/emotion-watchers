#!/usr/bin/env python3

from pathlib import Path
import pickle
import re
import sys
from typing import Dict, List, Tuple

ID_TO_EMOTION = {2: "joy", 3: "joy", 4: "joy", 5: "anger", 6: "anger", 7: "anger"}


def process_raw(yaml_path: Path, pkl_path: Path):
    emotion_dialations = {}

    for emotion in ID_TO_EMOTION.values():
        emotion_dialations[emotion] = []

    with open(yaml_path, "r") as f:
        curr_id = 0
        curr_lpd = 0
        for line in f:
            if match := re.search(".*MID:(?P<MID>\d+),.*", line):
                curr_id = int(match["MID"])
            elif match := re.search(".*LPD:(?P<LPD>[0-9.e+\-]+),.*", line):
                curr_lpd = float(match["LPD"])
            elif match := re.search(".*RPD:(?P<RPD>[0-9.e+\-]+),.*", line):
                if curr_id in ID_TO_EMOTION:
                    emotion_dialations[ID_TO_EMOTION[curr_id]].append(
                        (curr_lpd + float(match["RPD"])) / 2
                    )

    with open(pkl_path, "wb") as f:
        pickle.dump(emotion_dialations, f)


def load_raw(pkl_path: Path) -> Dict[str, List[Tuple]]:
    with open(pkl_path, "rb") as f:
        data = pickle.load(f)
    return data


if __name__ == "__main__":
    process_raw(Path(sys.argv[1]), Path(sys.argv[2]))
    print(load_raw(Path(sys.argv[2])))
