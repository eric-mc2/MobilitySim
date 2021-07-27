# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Configuration file for simulation parameters

from numpy.random import default_rng

class Config():
    def __init__(self):
        self.N_FAMILIES = 50
        self.N_TIMESTEPS = 100
        self.N_NEIGHBORHOODS = 2 # TODO: make endogeneous
        self.INCOME_GROWTH = 0   # alpha in eq(1)
        self.PARENTAL_INVESTMENT_COEF = 0  # beta in eq(1)
        self.SKILL_FROM_PARENT_INCOME = 0  # theta in eq(9)
        self.SKILL_FROM_NEIGHBOR_INCOME = 0  # theta in eq(9)
        self.CAPITAL_EFFICIENCY = 0 # phi in eq(4)
        self.INCOME_NOISE_ADDITIVE = 0 # epsilon in eq(1) 
        self.INCOME_NOISE_AUTOREG = 0 # epsilon in eq(1)
        self.TAX_RATE = 0
        # self.UTILITY_CONSUMPTION = .5
        # self.UTILITY_INCOME = (1 - self.UTILITY_CONSUMPTION)
        self.rng = default_rng(seed=12345)

    def set(self, param, value):
        if hasattr(self, param):
            setattr(self, param, value)
        else:
            print(f"Error: Invalid parameter {param}")
    