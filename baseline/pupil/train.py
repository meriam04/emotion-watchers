#!/usr/bin/env python3

import numpy as np
import os
from pathlib import Path
import pickle
from sklearn.model_selection import train_test_split
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data import DataLoader
from typing import Dict, List, Tuple

from classifier import LSTMClassifier


def get_data(pkl_paths: List[Path]) -> Tuple[Dict[str, List[Tuple]]]:
    # Load the dataset from the .pkl file
    dataset = {}
    classes = []
    for path in pkl_paths:
        with open(path, "rb") as f:
            data = pickle.load(f)
            for emotion, dilations in data.items():
                if emotion not in classes:
                    classes.append(emotion)
                    dataset[classes.index(emotion)] = []
                dataset[classes.index(emotion)].extend(dilations)

    # Split the dataset into train, val, and test sets
    train, val, test = {}, {}, {}
    for emotion, dilations in dataset.items():
        train[emotion], test[emotion] = train_test_split(dilations, test_size=0.2, shuffle=False)
        train[emotion], val[emotion] = train_test_split(train[emotion], test_size=0.2, shuffle=False)
    return train, val, test


def get_accuracy(model, dataset):
    correct = 0
    total = 0
    for label, dialations in dataset.items():
        dialations_t = torch.tensor([dialations]).transpose(0, 1)
        output = model(dialations_t)

        # select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        print(f"{label}, {pred}")
        correct += pred.eq(torch.full(pred.size(), float(label))).sum().item()
        total += len(dialations)
    return correct / total


def get_model_name(name, learning_rate, epoch):
    path = "model_{0}_lr{1}_epoch{2}".format(
        name, learning_rate, epoch
    )
    return path


def train(model, train, val, learning_rate=0.01, num_epochs=10):
    # Train the model
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    iters, losses, train_acc, val_acc = [], [], [], []

    n = 0
    for epoch in range(num_epochs):
        for label, dialations in train.items():
            # Forward pass
            dialations_t = torch.tensor([dialations]).transpose(0, 1)
            out = model(dialations_t)
            print(f"{out}, {torch.tensor([dialations]).transpose(0, 1)}")

            # Compute the total loss
            loss = criterion(out, torch.full(dialations_t.size(), float(label)))
            # Backward pass
            loss.backward()
            # Make the updates
            optimizer.step()
            # Clean up
            optimizer.zero_grad()

            normalized_loss = float(loss) / len(dialations)
        
        # Save the training/validation loss/accuracy
        iters.append(n)
        losses.append(normalized_loss)
        train_acc.append(get_accuracy(model, train))
        val_acc.append(get_accuracy(model, val))
        n += 1
        print(
            ("Epoch {}: Train acc: {}, Train loss: {} |" + "Validation acc: {}").format(
                epoch + 1, train_acc[epoch], losses[epoch], val_acc[epoch]
            )
        )
        # Save the current model (checkpoint) to a file
        model_path = (
            get_model_name(model.name, learning_rate, epoch) + ".weights"
        )
        #torch.save(model.state_dict(), model_path)

if __name__ == "__main__":
    np.random.seed(496)

    pkl_paths = []
    for file in os.listdir(sys.argv[1]):
        if Path(file).suffix == ".pkl":
            pkl_paths.append(Path(sys.argv[1]) / file)

    train_set, val_set, _ = get_data(pkl_paths)

    model = LSTMClassifier()

    train(model, train_set, val_set, learning_rate=0.5, num_epochs=10)
