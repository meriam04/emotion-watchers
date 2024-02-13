import csv
import numpy as np
import os
from pathlib import Path
import re
import sys
import tensorflow as tf
from tensorflow.data import Dataset
from tensorflow.keras.models import Sequential
from tensorflow.keras.layers import Bidirectional, Conv1D, Dense, Dropout, Input, LSTM
from typing import List

BINARY_CLASSES = ["positive", "negative", "negative", "positive", "negative", "positive"]
MULTICLASS_CLASSES = ["joy", "anger", "fear", "fun", "sad", "happy"]

def get_data(csv_paths: List[Path], classes: List[str], window_size: int = 100):
    # Load the dataset from the .csv file
    dilations_dict = {}
    for c in classes:
        dilations_dict[c] = []

    for path in csv_paths:
        with open(path, "r") as f:
            reader = csv.DictReader(f)
            for row in reader:
                if match := re.search("(?P<id>\d+)_video_\d+\.\w+", row["processed_names"]):
                    dilations_dict[classes[int(match["id"])-1]].append(float(row["processed_diameters"]))

    label = np.zeros((1, len(set(classes))))
    
    dilation_windows = []
    label_windows = []
    for emotion, dilations in dilations_dict.items():
        new_label = np.copy(label)
        new_label[0][list(set(classes)).index(emotion)] = 1.0
        num_windows = int(len(dilations) // window_size)
        for i in range(num_windows):
            dilation_windows.append(dilations[i*window_size:(i+1)*window_size])
            label_windows.append(new_label)

    # Make a list of indices for the dataset
    indices = []
    for i in range(len(dilation_windows)):
        indices.append(i)
    # Shuffle the indices
    np.random.shuffle(indices)

    train_val_split = int(len(indices) * 0.6)
    val_test_split = int(len(indices) * 0.8)

    train_indices = indices[:train_val_split]
    val_indices = indices[train_val_split:val_test_split]
    test_indices = indices[val_test_split:]

    def make_dataset(dilations_set, labels_set, indices_set):
        shuffled_dilations = []
        shuffled_labels = []
        for idx in indices_set:
            shuffled_dilations.append(dilations_set[idx])
            shuffled_labels.append(labels_set[idx])

        dilations_t = tf.expand_dims(tf.convert_to_tensor(shuffled_dilations), 1)
        labels_t = tf.convert_to_tensor(shuffled_labels)

        # Last batch is dropped because it may not be the correct size
        return Dataset.from_tensor_slices((dilations_t, labels_t))

    train_set = make_dataset(dilation_windows, label_windows, train_indices)
    val_set = make_dataset(dilation_windows, label_windows, val_indices)
    test_set = make_dataset(dilation_windows, label_windows, test_indices)

    return train_set, val_set, test_set

def create_lstm_model(input_shape, num_classes):
        model = Sequential()
        model.add(Input(shape=input_shape))
        model.add(Bidirectional(LSTM(10, dropout=0.2, return_sequences=True)))
        model.add(Conv1D(10, 3, activation='selu'))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(10, dropout=0.2, return_sequences=True)))
        model.add(Bidirectional(LSTM(10, dropout=0.2, return_sequences=True)))
        model.add(Conv1D(10, 3, activation='selu'))
        model.add(Dropout(0.2))
        model.add(Bidirectional(LSTM(10, dropout=0.2, return_sequences=False)))
        model.add(Dense(num_classes, activation='softmax'))
        model.compile(loss='categorical_crossentropy', optimizer='adam', metrics=['accuracy'])
        return model

if __name__ == "__main__":
    # fix random seed for reproducibility
    np.random.seed(496)
    tf.random.set_seed(7)

    csv_paths = []
    for file in os.listdir(sys.argv[1]):
        if re.search("pupil_\w+\.csv", Path(file).name):
            csv_paths.append(Path(sys.argv[1]) / file)

    classes = BINARY_CLASSES
    window_size = 100

    train_set, val_set, test_set = get_data(csv_paths, classes, window_size)

    # Assuming input_shape and num_classes are determined by your specific task
    input_shape = (window_size, 1)
    num_classes = len(set(classes))

    # Create the LSTM model
    model = create_lstm_model(input_shape, num_classes)

    # Training loop
    epochs = 10

    for epoch in range(epochs):
        # Training
        model.fit(train_set, epochs=1)

        # Validation
        model.evaluate(val_set)
