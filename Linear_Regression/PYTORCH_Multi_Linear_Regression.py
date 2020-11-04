import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F
import torch.optim as optim
from torch.utils.data import TensorDataset, DataLoader

from SimpleNet import SimpleNet, fit, get_linear_model
from Prepare_Light_Temp_Data import prepareLightTempData

august = prepareLightTempData(
    "csvs/grafana_Helligkeit_August.csv", "csvs/grafana_Temperatur_August.csv"
)
# oktober = prepareLightTempData(
#    "csvs/grafana_Helligkeit_Oktober.csv",
#    "csvs/grafana_Temperatur_Oktober.csv",
# )
komplett = prepareLightTempData(
    "csvs/grafana_Helligkeit.csv", "csvs/grafana_Temperatur.csv"
)
X = august.get_X()
y = august.get_y()
# X1 = oktober.get_X()
# y1 = oktober.get_y()
X2 = komplett.get_X()
y2 = komplett.get_y()

X_tensor = torch.from_numpy(X.values).float()
y_tensor = torch.from_numpy(y.values).float()
# X1_tensor = torch.from_numpy(X1.values).float()
# y1_tensor = torch.from_numpy(y1.values).float()
X2_tensor = torch.from_numpy(X2.values).float()

batch_size = 10
train_ds = TensorDataset(X_tensor, y_tensor)
train_dl = DataLoader(train_ds, batch_size, shuffle=True)

valid_ds = TensorDataset(X_tensor, y_tensor)
valid_dl = DataLoader(valid_ds, batch_size=batch_size * 2)

# Define model
model, opt = get_linear_model(2, 1, 1e-5)

# Define loss function
loss_fn = F.mse_loss

# Train the model for 100 epochs
epochs = 100
fit(epochs, model, loss_fn, opt, train_dl, valid_dl)

# Generate predictions
preds = model(X2_tensor)
preds

y2

plt.plot(X2['M_Temperatur.m_temperatur {room: Wohnzimmer}'].values, 'b')
plt.plot(y2.values, 'g')
plt.plot(preds.detach().numpy(), 'r')
plt.show()


# Define data loader
model1 = SimpleNet()
opt1 = optim.SGD(model1.parameters(), 1e-5)

# Train the model for 100 epochs
fit(epochs, model1, loss_fn, opt1, train_dl, valid_dl)

# Generate predictions
preds = model1(X2_tensor)
preds

y2
plt.plot(X2['M_Temperatur.m_temperatur {room: Wohnzimmer}'].values, 'b')
plt.plot(y2.values, 'g')
plt.plot(preds.detach().numpy(), 'r')
plt.show()
