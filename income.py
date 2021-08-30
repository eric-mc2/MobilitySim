# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Intergenerational income transition mechanism


from mechanism import SimMech
import numpy as np
from numpy import ndarray

class Income(SimMech):
    def __init__(self, config, globals):
        super().__init__(config, globals)
        self.income = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES))
        self.noise = np.zeros(config.N_FAMILIES)

    def _inherit_income(self):
        """ pass down money directly to offspring """
        # follows eq(1) for now
        income_of_parent = self.income[self.globals.t-1, :]
        return self.config.PARENTAL_INVESTMENT_COEF * income_of_parent


    def _inherit_income_shock(self):
        """part of epsilon, the MA(1) process from eq (1)"""
        return self.config.INCOME_NOISE_AUTOREG * self.noise


    def _income_shock(self):
        """part of epsilon, the MA(1) process from eq (1)"""
        # in proposition 6, page 19, the authors limit epsilon > 0
        shock = self.generate_white_noise(self.config.N_FAMILIES, 1, 1, 0)
        return self.config.INCOME_NOISE_ADDITIVE * shock


    def gain_income(self, earned_income: ndarray):
        """one intergenerational timestep. eq(1) """
        income_from_parent = self._inherit_income()
        income_shock = self._income_shock()
        inherited_shock = self._inherit_income_shock()
        offspring_income = (self.config.INCOME_GROWTH + 
                            income_from_parent +
                            earned_income + 
                            income_shock + 
                            inherited_shock) 
        self.income[self.globals.t, :] = offspring_income
        self.noise = income_shock + inherited_shock


    def initialize_income(self):
        """ create initial income distribution """
        # this is arbitrary right now
        self.income = np.zeros((self.config.N_TIMESTEPS, self.config.N_FAMILIES))
        self.income[0, :] = np.full(self.config.N_FAMILIES, 1)
        self.noise = np.zeros(self.config.N_FAMILIES)
