#!/usr/bin/env python3

import numpy as np
import os
from pathlib import Path
import sys
import torch
import torch.nn as nn
import torch.optim as optim
from torch.utils.data.sampler import SubsetRandomSampler
import torchvision
import torchvision.transforms as transforms

from .classifier import BinaryClassifier, MulticlassClassifier


def get_data(data_dir, batch_size=32):
    # Transform the images to tensors of normalized range [-1, 1]
    transform = transforms.Compose(
        [transforms.ToTensor(), transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))]
    )

    # Load the dataset
    dataset = torchvision.datasets.ImageFolder(data_dir, transform=transform)
    dataset.classes = [c for c in os.listdir(data_dir)]

    # Make a list of indices for the dataset
    indices = []
    for i in range(len(dataset)):
        indices.append(i)
    # Shuffle the indices
    np.random.shuffle(indices)

    train_val_split = int(len(indices) * 0.6)
    val_test_split = int(len(indices) * 0.8)

    # Split the indices and load the dataset using the split indices into train_loader, val_loader, and test_loader
    train_indices = indices[:train_val_split]
    train_sampler = SubsetRandomSampler(train_indices)
    train_loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, num_workers=1, sampler=train_sampler
    )
    val_indices = indices[train_val_split:val_test_split]
    val_sampler = SubsetRandomSampler(val_indices)
    val_loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, num_workers=1, sampler=val_sampler
    )
    test_indices = indices[val_test_split:]
    test_sampler = SubsetRandomSampler(test_indices)
    test_loader = torch.utils.data.DataLoader(
        dataset, batch_size=batch_size, num_workers=1, sampler=test_sampler
    )

    return train_loader, val_loader, test_loader, dataset.classes


def get_accuracy(model, data_loader):
    correct = 0
    total = 0
    for imgs, labels in iter(data_loader):
        output = model(imgs)

        # select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        correct += pred.eq(labels.view_as(pred)).sum().item()
        total += imgs.shape[0]
    return correct / total


def get_model_name(name, batch_size, learning_rate, epoch):
    path = "model_{0}_bs{1}_lr{2}_epoch{3}".format(
        name, batch_size, learning_rate, epoch
    )
    return path


# Training
def train(
    model, train_loader, val_loader, batch_size=32, learning_rate=0.01, num_epochs=10
):
    # I chose cross entropy loss because this is a classification problem
    criterion = nn.CrossEntropyLoss()
    # I chose to use SGD with momentum to better search for a global maximum and easily navigate ravines
    optimizer = optim.SGD(model.parameters(), lr=learning_rate, momentum=0.9)

    iters, losses, train_acc, val_acc = [], [], [], []

    n = 0
    for epoch in range(num_epochs):
        for imgs, labels in iter(train_loader):
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

        # Save the training/validation loss/accuracy
        iters.append(n)
        losses.append(float(loss) / batch_size)
        train_acc.append(get_accuracy(model, train_loader))
        val_acc.append(get_accuracy(model, val_loader))
        n += 1
        print(
            ("Epoch {}: Train acc: {}, Train loss: {} |" + "Validation acc: {}").format(
                epoch + 1, train_acc[epoch], losses[epoch], val_acc[epoch]
            )
        )
        # Save the current model (checkpoint) to a file
        model_path = (
            get_model_name(model.name, batch_size, learning_rate, epoch) + ".weights"
        )
        torch.save(model.state_dict(), model_path)


if __name__ == "__main__":
    np.random.seed(496)
    train_loader, val_loader, _, _ = get_data(Path(sys.argv[1]))

    model = MulticlassClassifier()

    train(model, train_loader, val_loader, learning_rate=0.005, num_epochs=10)
