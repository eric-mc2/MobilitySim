# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Neighborhood mechanism

from config import Config, Globals
from mechanism import SimMech
import numpy as np
from numpy import ndarray
import warnings
from enum import Enum, auto
from income import Income

class Formation(Enum):
    STATIC = auto()
    PERFECT_SORTING_PAIRS = auto()
    PERFECT_SORTING = auto()

class Neighborhood(SimMech):
    def __init__(self, config: Config, globals: Globals):
        super().__init__(config, globals)
        self.hood = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES))
        self.pop = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES))
        self.count = 0


    def _census(self):
        pop = np.bincount(self.hood[self.globals.t, :])
        ragged_len = self.config.N_FAMILIES - pop.size
        padded_pop = np.pad(pop, (0, ragged_len), constant_value=0)
        self.pop[self.globals.t, :] = padded_pop
        self.count = pop.size


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
        return [taxes[adult_neighborhood == n].sum() for n in range(self.count)]


    def pay_taxes(self, income: Income):
        adult_income = income.income[self.globals.t, :]
        taxes = self._compute_taxes(adult_income)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            income_after_tax = adult_income - taxes
            if len(w):
                print('somethign bad')
        taxbase = self._compute_tax_revenue(taxes)
        income.income[self.globals.t] = income_after_tax
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

class SortedNeighborhood(SortedPairsNeighborhood):
    def pick_neighborhood(self, income):
        """ select into neighborhoods """
        joining = {}
        sorting = np.argsort(income.income[self.globals.t, :])
        for i in range(len(sorting)):
            for j in range(i+1, len(sorting)):
                pass
        self._census()