import torch.nn as nn


class LSTMClassifier(nn.Module):
    def __init__(self):
        super(LSTMClassifier, self).__init__()
        self.name = "LSTM Model"
        self.lstm = nn.LSTM(1, 50, 1)
        self.fc1 = nn.Linear(50, 6)

    def forward(self, x):
        x, _ = self.lstm(x)
        x = self.fc1(x)
        x = x.squeeze(1)
        return x
