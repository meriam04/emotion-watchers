import torch.nn as nn
import torch.nn.functional as F

class BinaryClassifier(nn.Module):
  def __init__(self):
    super(BinaryClassifier, self).__init__()
    self.name = "Base Model (k = 5 and k = 3)"
    self.conv1 = nn.Conv2d(3, 6, 5)
    self.pool = nn.MaxPool2d(2, 2)
    self.conv2 = nn.Conv2d(6, 16, 3)
    self.fc1 = nn.Linear(54*54*16, 54*54)
    self.fc2 = nn.Linear(54*54, 54)
    self.fc3 = nn.Linear(54, 2)

  def forward(self, x):
    x = self.pool(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv2(x)))
    x = x.view(-1, 54*54*16)
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    x = x.squeeze(1)
    return x

class MulticlassClassifier(nn.Module):
  def __init__(self):
    super(MulticlassClassifier, self).__init__()
    self.name = "Base Model (k = 5 and k = 3)"
    self.conv1 = nn.Conv2d(3, 6, 5)
    self.pool = nn.MaxPool2d(2, 2)
    self.conv2 = nn.Conv2d(6, 16, 3)
    self.fc1 = nn.Linear(54*54*16, 54*54)
    self.fc2 = nn.Linear(54*54, 54)
    self.fc3 = nn.Linear(54, 6)

  def forward(self, x):
    x = self.pool(F.relu(self.conv1(x)))
    x = self.pool(F.relu(self.conv2(x)))
    x = x.view(-1, 54*54*16)
    x = F.relu(self.fc1(x))
    x = F.relu(self.fc2(x))
    x = self.fc3(x)
    x = x.squeeze(1)
    return x
