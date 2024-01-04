#!/usr/bin/env python3

import numpy as np
from pathlib import Path
import torch

from classifier import BinaryClassifier, MulticlassClassifier
from train import get_accuracy, get_data, BASELINE_DATA_DIR

BASELINE_WEIGHTS_DIR = Path(__file__).parent / "Binary_CKM.weights"

if __name__ == "__main__":
    np.random.seed(496)

    _, _, test_loader = get_data(BASELINE_DATA_DIR)

    model = BinaryClassifier()
    model.load_state_dict(torch.load(BASELINE_WEIGHTS_DIR))

    print(get_accuracy(model, test_loader))
