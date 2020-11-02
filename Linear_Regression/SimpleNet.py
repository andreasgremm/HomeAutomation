import torch.nn as nn
#######################################
### Using built-in linear function ####
#######################################

class SimpleNet(nn.Module):  ### inheriting from nn.Module!

    def __init__(self):
        super().__init__()

        ###############################
        ##### YOUR SOLUTION START #####
        ###############################
        ##
        ## Task (1): add torch.nn.Linear as a class-member
        ##

        self.linear1 = nn.Linear(2, 3)
        self.act1 = nn.ReLU() # Activation function
        self.linear2 = nn.Linear(3, 5)
        self.act2 = nn.ReLU() # Activation function
        self.linear3 = nn.Linear(5, 2)
        self.act3 = nn.ReLU() # Activation function
        self.linear4 = nn.Linear(2, 1)

        ###############################
        ##### YOUR SOLUTION End   #####
        ###############################

    def forward(self, x):
        ###############################
        ##### YOUR SOLUTION START #####
        ###############################
        ##
        ## Task (2): call the member function on x and return the result
        ##

        x = self.linear1(x)
        x = self.act1(x)
        x = self.linear2(x)
        x = self.act2(x)
        x = self.linear3(x)
        x = self.act3(x)
        x = self.linear4(x)
        return x

        ###############################
        ##### YOUR SOLUTION End   #####
        ###############################
