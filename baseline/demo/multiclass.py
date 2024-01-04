#!/usr/bin/env python3

from pathlib import Path
import sys
import torch
import torchvision
import torchvision.transforms as transforms

sys.path.append('..')

from classifier import MulticlassClassifier

DEMO_DATA_DIR = Path(__file__).parent.parent.parent / "data/demo/multiclass"
DEMO_WEIGHTS_DIR = Path(__file__).parent.parent / "Multiclass_CKM.weights"

def predict(model, data_loader):
    preds = []
    for imgs, _ in iter(data_loader):
        output = model(imgs)
        
        #select index with maximum prediction score
        pred = output.max(1, keepdim=True)[1]
        preds.extend(pred)
    return preds

if __name__ == "__main__":
    # Transform the images to tensors of normalized range [-1, 1]
    transform = transforms.Compose(
            [transforms.ToTensor(),
            transforms.Normalize((0.5, 0.5, 0.5), (0.5, 0.5, 0.5))])

    # Load the dataset
    dataset = torchvision.datasets.ImageFolder(DEMO_DATA_DIR, transform=transform)
    dataset.classes = ["anger", "fear", "fun", "happy", "joy", "sad"]
    test_loader = torch.utils.data.DataLoader(dataset, batch_size=32, num_workers=1)

    model = MulticlassClassifier()
    model.load_state_dict(torch.load(DEMO_WEIGHTS_DIR))

    preds = predict(model, test_loader)
    for i, pred in enumerate(preds):
        print(f"{dataset.imgs[i][0]}: {dataset.classes[pred[0].item()]}")
