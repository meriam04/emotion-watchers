from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple

from .classifier import LSTMClassifier


def get_data(pkl_paths: List[Path]) -> Tuple[Dict[str, List[Tuple]]]:
    # Load the dataset from the .pkl file
    dataset = {}
    for path in pkl_paths:
        with open(path, "rb") as f:
            data = pickle.load(f)
            for emotion, dilations in data.items():
                if emotion not in dataset:
                    dataset[emotion] = []
                dataset[emotion].extend(dilations)

    # Split the dataset into train, val, and test sets
    for emotion, dilations in dataset.items():
        train, test = train_test_split(dilations, test_size=0.2, shuffle=False)
        train, val = train_test_split(train, test_size=0.2, shuffle=False)
    return train, val, test


def train(model, train, val, learning_rate=0.01, num_epochs=10):
    # Train the model
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    iters, losses, train_acc, val_acc = [], [], [], []

    n = 0
    for epoch in range(num_epochs):
        for imgs, labels in iter(train):
            # Forward pass
            out = model(imgs)

            # Compute the total loss
            loss = criterion(out, labels)
            # Backward pass
            loss.backward()
            # Make the updates
            optimizer.step()
            # Clean up
            optimizer.zero_grad()
