# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: A simulation of intergenerational mobility
# Description: Modeled after the Durlauf-Seshadri paper "Understanding the
#   Great Gatsby Curve"

import numpy as np
import warnings
from results import SimResult, SimResultAgg, SimResultSweep
from income import Income
from config import Config
from human_capital import HumanCapital
from neighborhood import Neighborhood

class Sim():

    def __init__(self):
        self.config = Config()
        self.income = Income(self.config)
        self.capital = HumanCapital(self.config)
        self.neighborhood = Neighborhood(self.config)
    
    def set(self, param, value):
        self.config.set(param, value)

        
    # def __compute_utility(self, adult_income, adult_neighborhood, taxbase):
    #     """ eq(3). there's no point in using this yet since we have PARENTAL_INVESTMENT_COEF"""
    #     # right now assume adults only know their own income and 
    #     # each neihborhoods' tax base and population
    #     # and the efficiency of human capital
    #     known_rng = default_rng.rng(seed=42)
    #     known_noise = np.zeros(self.N_FAMILIES)
    #     ex_child_capital = self.__develop_human_capital(adult_income, adult_neighborhood, taxbase)
    #     ex_consumption = (1-self.PARENTAL_INVESTMENT_COEF) * adult_income
    #     ex_child_income = (self.PARENTAL_INVESTMENT_COEF * adult_income
    #                         + self.CAPITAL_EFFICIENCY * ex_child_capital)
    #     return (self.UTILITY_CONSUMPTION * np.log(ex_consumption)
    #             + self.UTILITY_INCOME * np.log(ex_child_income))

    # def __maximize_utility(self, adult_consumption, adult_neighborhood, adult_income):
    #     """ eq(3) """
    #     pass

    def _run_trial(self):
        income = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        neighborhoods = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        neighborhood_size = np.zeros((self.N_TIMESTEPS, self.N_NEIGHBORHOODS))
        human_capital = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        taxbase = np.zeros(self.N_NEIGHBORHOODS)
        income[0, :], income_noise = self.income.initialize_income()
        neighborhoods[0, :] = self.neighborhood.initialize_neighborhoods()
        neighborhood_size[0, :] = self.neighborhood.census(neighborhoods[0, :])
        human_capital[0, :] = self.capital.initialize_human_capital()

        for t in range(1, self.N_TIMESTEPS):
            # Adult things
            income[t, :], income_noise = self.income.receive_income(income[t-1, :], income_noise, human_capital[t-1, :])
            neighborhoods[t, :] = self.neighborhood.pick_neighborhood(income[t-1, :], neighborhoods[t-1, :])
            neighborhood_size[t, :] = self.neighborhood.census(neighborhoods[t, :])
            income[t, :], taxbase = self.neighborhood.pay_taxes(income[t, :], neighborhoods[t, :])
            # Child things
            human_capital[t, :] = self.capital.develop_human_capital(income[t, :], neighborhoods[t, :], taxbase)
        
        return SimResult(income, neighborhoods, neighborhood_size, human_capital)

    def run(self, ntrials=1, keep_trials=False):
        result = SimResultAgg(keep_trials)
        for trial in range(ntrials):
            result.add(self._run_trial())
        return result

    def run_sweep(self, param, values, ntrials=1):
        result = SimResultSweep()
        for value in values:
            self.config.set(param, value)
            result.add(self.run(ntrials), value)
        return result
