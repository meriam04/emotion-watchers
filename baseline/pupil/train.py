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
from torch.utils.data import DataLoader, TensorDataset
from torch.utils.data.sampler import SubsetRandomSampler
from typing import Dict, List, Tuple

from classifier import LSTMClassifier

#temp
import matplotlib.pyplot as plt


def get_data(pkl_paths: List[Path], batch_size=1024, lookback=1):
    # Load the dataset from the .pkl file
    dilations = []
    labels = []
    classes = []
    for path in pkl_paths:
        with open(path, "rb") as f:
            data = pickle.load(f)
            for emotion, dilation in data.items():
                if emotion not in classes:
                    classes.append(emotion)
                dilations.extend(dilation)
                new_label = [0.0, 0.0]
                new_label[classes.index(emotion)] = 1.0
                labels.extend([new_label] * len(dilation))
                # plt.plot(dilation)
                # plt.savefig(Path(__file__).parent / f"{emotion}.png")
                # plt.clf()
    print(classes)

    lookback_dilations = []
    for i in range(lookback, len(dilations)):
        lookback_dilations.append(dilations[i-lookback:i])

    batched_dilations = []
    batched_labels = []
    for i in range(0, len(dilations), batch_size):
        batched_dilations.append(lookback_dilations[i:i+batch_size])
        batched_labels.append(labels[i:i+batch_size])

    # Last batch is dropped because it may not be the correct size
    dataset = TensorDataset(torch.tensor(batched_dilations[:-1]), torch.tensor(batched_labels[:-1]))

    # Split the dataset into train, val, and test sets
    train, test = train_test_split(dataset, test_size=0.2)
    train, val = train_test_split(train, test_size=0.2)

    # Load the dataset into train_loader, val_loader, and test_loader
    train_loader = DataLoader(
        train, batch_size=1, num_workers=1
    )
    val_loader = DataLoader(
        val, batch_size=1, num_workers=1
    )
    test_loader = DataLoader(
        test, batch_size=1, num_workers=1
    )

    return train_loader, val_loader, test_loader


def get_accuracy(model, data_loader, name, epoch):
    correct = 0
    total = 0
    #combined_preds = []
    for dilations, labels in iter(data_loader):
        output = model(dilations.squeeze(0))

        # select index with maximum prediction score
        pred = output.max(1)[1]
        #combined_preds.extend(pred)
        #print(f"{pred.transpose(0, 1)}, {labels.squeeze(0)}")
        correct += pred.eq(labels.max(2)[1]).sum().item()
        total += pred.shape[0]

    '''
    combined_dilations = []
    combined_labels = []
    for dilations, labels in data_loader:
        combined_dilations.extend(dilations.squeeze(0))
        #print(dilations.squeeze(0))
        combined_labels.extend(labels.max(2)[1])
        #print(labels.transpose(0, 1))
    #plt.plot(combined_dilations)
    plt.plot(combined_labels, c='c')
    plt.plot(combined_preds, c='r')
    plt.savefig(Path(__file__).parent / f"{name}_{epoch}.png")
    plt.clf()
    '''

    return correct / total


def get_model_name(name, learning_rate, epoch):
    path = "model_{0}_lr{1}_epoch{2}".format(
        name, learning_rate, epoch
    )
    return path


def train(model, train_loader, val_loader, batch_size=32, learning_rate=0.01, num_epochs=10):
    # Train the model
    criterion = nn.MSELoss()
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    iters, losses, train_acc, val_acc = [], [], [], []

    n = 0
    for epoch in range(num_epochs):
        model.train()
        for dilations, labels in iter(train_loader):
            #print(dilations.shape)
            #print(labels.shape)
            # Forward pass
            out = model(dilations.squeeze(0))
            #print(out.shape)
            #print()

            # Compute the total loss
            loss = criterion(out, labels.squeeze(0))
            # Backward pass
            loss.backward()
            # Make the updates
            optimizer.step()
            # Clean up
            optimizer.zero_grad()

            #print(f"train: {get_accuracy(model, train_loader)}, val: {get_accuracy(model, val_loader)}")
        
        model.eval()
        # Save the training/validation loss/accuracy
        iters.append(n)
        losses.append(float(loss) / batch_size)
        train_acc.append(get_accuracy(model, train_loader, "train", epoch))
        val_acc.append(get_accuracy(model, val_loader, "val", epoch))
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

    train_loader, val_loader, _ = get_data(pkl_paths)

    model = LSTMClassifier()

    train(model, train_loader, val_loader, learning_rate=0.005, num_epochs=2000)
