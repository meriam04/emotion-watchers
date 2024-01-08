#!/usr/bin/env python3

import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import torch

from classifier import BinaryClassifier, MulticlassClassifier
from train import get_accuracy, get_data, BASELINE_DATA_DIR

BASELINE_WEIGHTS_DIR = Path(__file__).parent / "Multiclass_CM.weights"
CONFUSION_MATRIX_PATH = Path(__file__).parent / "confusion_matrix.png"

def make_confusion_matrix(model, data_loader, classes):
    truth = []
    pred = []
    for imgs, labels in iter(data_loader):
        truth.extend(classes[i] for i in labels.numpy())

        output = model(imgs)
        
        #select index with maximum prediction score
        pred.extend(classes[i] for i in output.max(1, keepdim=True)[1].T[0].numpy())
    cm = confusion_matrix(truth, pred, labels=classes)
    ConfusionMatrixDisplay(cm, display_labels=classes).plot()
    plt.savefig(CONFUSION_MATRIX_PATH)

if __name__ == "__main__":
    np.random.seed(496)

    _, _, test_loader, classes = get_data(BASELINE_DATA_DIR)

    model = MulticlassClassifier()
    model.load_state_dict(torch.load(BASELINE_WEIGHTS_DIR))

    make_confusion_matrix(model, test_loader, classes)
    print(get_accuracy(model, test_loader))
