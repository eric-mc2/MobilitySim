# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Neighborhood mechanism

from abc import ABC, abstractmethod
from config import Config, Globals
from mechanism import SimMech
import numpy as np
from numpy import ndarray
from income import Income


class Neighborhood(ABC, SimMech):
    def __init__(self, config: Config, globals: Globals):
        super().__init__(config, globals)
        self.hood = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES), dtype=np.int32)
        self.pop = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES), dtype=np.int32)
        equilib = config.UTILITY_CONSUMPTION / (config.UTILITY_CONSUMPTION + self.config.UTILITY_CHILD_INCOME)
        self.taxrate_pref = np.repeat(equilib, config.N_FAMILIES)
        self.hood_count = 0

    @classmethod
    def _pad_right(cls, arr, length):
        end_length = length - arr.size
        margins = (0, end_length)
        return np.pad(arr, margins, constant_values=0)

    def _census(self):
        pop = np.bincount(self.hood[self.globals.t, :])
        padded_pop = Neighborhood._pad_right(pop, self.config.N_FAMILIES) 
        self.pop[self.globals.t, :] = padded_pop
        self.hood_count = pop.size


    @abstractmethod
    def pick_neighborhood(self, income):
        """ select into neighborhoods """
        pass    

    def initialize_neighborhoods(self):
        """ create initial neighborhood selection """
        # this is arbitrary right now
        selection = np.full(self.config.N_FAMILIES, 0)
        selection[0 : int(self.config.N_FAMILIES/2)] = 1
        self.hood[0, :] = selection
        self._census()


    def _compute_taxes(self, adult_income: ndarray):
        taxable = adult_income > 0
        return np.where(taxable, adult_income, 0) * self.config.TAX_RATE


    def _compute_tax_revenue(self, taxes: ndarray):
        adult_neighborhood = self.hood[self.globals.t, :]
        return [taxes[adult_neighborhood == n].sum() for n in range(self.hood_count)]


    def collect_taxes(self, income: Income):
        adult_income = income.income[self.globals.t, :]
        taxes = self._compute_taxes(adult_income)
        income_after_tax = adult_income - taxes
        taxbase = self._compute_tax_revenue(taxes)
        income.income[self.globals.t, :] = income_after_tax
        return taxbase

        
class StaticNeighborhood(Neighborhood):
    def pick_neighborhood(self, income):
        """ select into neighborhoods """
        self.hood[self.globals.t, :] = self.hood[self.globals.t-1, :]
        self._census()

class SortedPairsNeighborhood(Neighborhood):
    def pick_neighborhood(self, income):
        """ select into neighborhoods """
        sorting = np.argsort(income.income[self.globals.t, :])
        self.hood[self.globals.t, :] = sorting // 2
        self._census()

class SortedNeighborhood(Neighborhood):
    def pick_neighborhood(self, income):
        """ select into neighborhoods """
        joining = {}
        sorting = np.argsort(income.income[self.globals.t, :])
        for i in range(len(sorting)):
            for j in range(i+1, len(sorting)):
                # start from highest income person. add next income person if
                # they contribute positively to marginal income.
                pass
        self._census()