import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
import torch
import torch.nn as nn
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from SimpleNet import SimpleNet

# from mpl_toolkits.mplot3d.axes3d import Axes3D


# Define a utility function to train the model
def fit(num_epochs, model, loss_fn, opt, train_dl):
    for epoch in range(num_epochs):
        for xb, yb in train_dl:
            # Generate predictions
            pred = model(xb)
            loss = loss_fn(pred, yb)
            # Perform gradient descent
            loss.backward()
            opt.step()
            opt.zero_grad()
    print("Training loss: ", loss_fn(model(X_tensor), y_tensor))


temp_aug = pd.read_csv(
    "csvs/grafana_Temperatur_August.csv",
    sep=";",
    index_col=0,
    parse_dates=True,
)
light_aug = pd.read_csv(
    "csvs/grafana_Helligkeit_August.csv",
    sep=";",
    index_col=0,
    parse_dates=True,
)
temp_light_aug = temp_aug.join(light_aug)

red_aug = temp_light_aug.drop(
    columns=[
        "Temperatur.temperatur {room: AUTO}",
        "Temperatur.temperatur {room: Wohnzimmer}",
        "Helligkeit.light {room: AUTO}",
        "Helligkeit.light {room: Wohnzimmer}",
        "Temperatur_nativ.temperatur_n {room: AUTO}",
        "Temperatur_nativ.temperatur_n {room: Wohnzimmer}",
    ]
)
dropedna_aug = red_aug.dropna(
    subset=[
        "M_Temperatur.m_temperatur {room: AUTO}",
        "M_Temperatur.m_temperatur {room: Wohnzimmer}",
        "M_Helligkeit.m_light {room: AUTO}",
        "M_Helligkeit.m_light {room: Wohnzimmer}",
    ]
)


X = dropedna_aug.drop(
    columns=[
        "M_Helligkeit.m_light {room: AUTO}",
        "M_Temperatur.m_temperatur {room: AUTO}",
    ]
)
X_tensor = torch.from_numpy(X.values).float()

y = dropedna_aug.drop(
    columns=[
        "M_Temperatur.m_temperatur {room: Wohnzimmer}",
        "M_Helligkeit.m_light {room: AUTO}",
        "M_Helligkeit.m_light {room: Wohnzimmer}",
    ]
)
y_tensor = torch.from_numpy(y.values).float()
print(X_tensor.shape)
print(y_tensor.shape)

train_ds = TensorDataset(X_tensor, y_tensor)
train_ds[0:3]

# Define data loader
batch_size = 100
train_dl = DataLoader(train_ds, batch_size, shuffle=True)
# next(iter(train_dl))

# Define model
model = nn.Linear(2, 1)
print(model.weight)
print(model.bias)

# Define optimizer
opt = optim.SGD(model.parameters(), lr=1e-5)

# Define loss function
loss_fn = F.mse_loss

loss = loss_fn(model(X_tensor), y_tensor)
print(loss)

# Train the model for 100 epochs
epochs = 100
fit(epochs, model, loss_fn, opt, train_dl)

# Generate predictions
preds = model(X_tensor)
preds

y_tensor

# Define data loader
batch_size = 100
train_dl1 = DataLoader(train_ds, batch_size, shuffle=True)
# next(iter(train_dl1))

model1 = SimpleNet()
opt1 = optim.SGD(model1.parameters(), 1e-5)
loss_fn1 = F.mse_loss

loss1 = loss_fn1(model1(X_tensor), y_tensor)
print(loss1)

# Train the model for 100 epochs
epochs = 100
fit(epochs, model1, loss_fn1, opt1, train_dl1)

# Generate predictions
preds = model1(X_tensor)
preds

y_tensor
