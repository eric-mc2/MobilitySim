# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Intergenerational income transition mechanism


import warnings
import numpy as np

class Income():
    def __init__(self, config):
        self.config = config

    def _generate_white_noise(self, size, mean=0, var=1):
        """returns `size` random samples"""
        # any white noise process will do
        return self.config.rng.normal(mean, var, size)


    def _earn_income(self, child_capital):
        """ eq (4) """
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            prod = (self.config.CAPITAL_EFFICIENCY
                * child_capital
                * self._generate_white_noise(self.config.N_FAMILIES, mean=1))
            if len(w):
                print('somethign bad')
        return prod
        

    def _inherit_income(self, parent_income):
        """ pass down money directly to offspring """
        # follows eq(1) for now
        return self.config.PARENTAL_INVESTMENT_COEF * parent_income


    def _inherit_shock(self, parent_noise):
        """part of epsilon, the MA(1) process from eq (1)"""
        return self.config.INCOME_NOISE_AUTOREG * parent_noise


    def _income_shock(self):
        """part of epsilon, the MA(1) process from eq (1)"""
        return self.config.INCOME_NOISE_ADDITIVE * self._generate_white_noise(self.config.N_FAMILIES)


    def receive_income(self, parent_income, parent_noise, child_capital):
        """one intergenerational timestep. eq(1) """
        income_from_parent = self._inherit_income(parent_income)
        earned_income = self._earn_income(child_capital)
        income_shock = self._income_shock()
        inherited_shock = self._inherit_shock(parent_noise)
        offspring_income = (self.config.INCOME_GROWTH + 
                            income_from_parent +
                            earned_income +
                            income_shock + 
                            inherited_shock)
                            
        return offspring_income, (income_shock + inherited_shock)


    def initialize_income(self):
        """ create initial income distribution """
        # this is arbitrary right now
        income = np.full(self.config.N_FAMILIES, 1)
        return income, np.zeros(income.shape)

