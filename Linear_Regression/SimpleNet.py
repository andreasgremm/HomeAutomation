import torch
import torch.nn as nn
import torch.optim as optim
import numpy as np


def get_linear_model(in_features, out_features, lr):
    model = nn.Linear(in_features, out_features)
    return model, optim.SGD(model.parameters(), lr=lr)


def loss_batch(model, loss_func, xb, yb, opt=None):
    loss = loss_func(model(xb), yb)

    if opt is not None:
        loss.backward()
        opt.step()
        opt.zero_grad()

    return loss.item(), len(xb)


# Define a utility function to train the model
def fit(num_epochs, model, loss_fn, opt, train_dl, valid_dl):
    for epoch in range(num_epochs):
        model.train()
        for xb, yb in train_dl:
            loss_batch(model, loss_fn, xb, yb, opt)

        model.eval()
        with torch.no_grad():
            losses, nums = zip(
                *[loss_batch(model, loss_fn, xb, yb) for xb, yb in valid_dl]
            )
        val_loss = np.sum(np.multiply(losses, nums)) / np.sum(nums)

        print(epoch, val_loss)
    # print("Training loss: ", loss_fn(model(X), y))


#######################################
#  Using built-in linear function     #
#######################################


class SimpleNet(nn.Module):  # inheriting from nn.Module!
    def __init__(self):
        super().__init__()

        ###############################
        # YOUR SOLUTION START         #
        ###############################
        #
        # Task (1): add torch.nn.Linear as a class-member
        #

        self.linear1 = nn.Linear(2, 2)
        self.act1 = nn.ReLU()  # Activation function
        self.linear2 = nn.Linear(2, 1)

        ###############################
        # YOUR SOLUTION End           #
        ###############################

    def forward(self, x):
        ###############################
        # YOUR SOLUTION START         #
        ###############################
        #
        # Task (2): call the member function on x and return the result
        #

        x = self.linear1(x)
        x = self.act1(x)
        x = self.linear2(x)
        return x

        ###############################
        # YOUR SOLUTION End           #
        ###############################
