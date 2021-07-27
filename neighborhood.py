# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Neighborhood mechanism

import numpy as np
import warnings


class Neighborhood():
    def __init__(self, config):
        self.config = config

    def census(self, adult_neighborhood):
        n_size = np.zeros(self.N_NEIGHBORHOODS)
        for n in range(self.N_NEIGHBORHOODS):
            n_size[n] = (adult_neighborhood == n).sum()
        return n_size


    def initialize_neighborhoods(self):
        """ create initial neighborhood selection """
        # this is arbitrary right now
        neighborhoods = np.full(self.config.N_FAMILIES, 0)
        neighborhoods[0 : int(self.config.N_FAMILIES/2)] = 1
        return neighborhoods


    def pick_neighborhood(self, adult_income, child_neighborhood):
        """ select into neighborhoods """
        # this is arbitrary now. should use differential selection
        return child_neighborhood


    def _compute_taxes(self, adult_income):
        taxable = adult_income > 0
        return np.where(taxable, adult_income, 0) * self.config.TAX_RATE


    def _compute_tax_revenue(self, taxes, adult_neighborhood):
        return [taxes[adult_neighborhood == n].sum() 
                for n in range(self.config.N_NEIGHBORHOODS)]


    def pay_taxes(self, adult_income, adult_neighborhood):
        taxes = self._compute_taxes(adult_income)
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            income_after_tax = adult_income - taxes
            if len(w):
                print('somethign bad')
        taxbase = self._compute_tax_revenue(taxes, adult_neighborhood)
        return income_after_tax, taxbase