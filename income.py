# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Intergenerational income transition mechanism


from mechanism import SimMech
import warnings
import numpy as np
from human_capital import HumanCapital

class Income(SimMech):
    def __init__(self, config, globals):
        super().__init__(config, globals)
        self.income = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES))

    def _generate_white_noise(self, size:int, mean=0, var=1):
        """returns `size` random samples"""
        # any white noise process will do
        return self.globals.rng.normal(mean, var, size)


    def _earn_income(self, human_capital: HumanCapital):
        """ eq (4) """
        capital_as_child = human_capital.capital[self.globals.t-1, :]
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            prod = (self.config.CAPITAL_EFFICIENCY
                * capital_as_child
                * self._generate_white_noise(self.config.N_FAMILIES, mean=1))
            if len(w):
                self.globals.logger.critical('numerical instability')
        return prod
        

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
        return self.config.INCOME_NOISE_ADDITIVE * self._generate_white_noise(self.config.N_FAMILIES)


    def receive_income(self, human_capital: HumanCapital):
        """one intergenerational timestep. eq(1) """
        income_from_parent = self._inherit_income()
        earned_income = self._earn_income(human_capital)
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
        self.income[0, :] = np.full(self.config.N_FAMILIES, 1)
        self.noise = np.zeros(self.income.shape)

