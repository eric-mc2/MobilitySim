# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Intergenerational human capital transition mechanism

import numpy as np
import warnings

class HumanCapital():
    def __init__(self, config):
        self.config = config
        
    def initialize_human_capital(self):
        """ create initial human capital distribution """
        # this is arbitrary right now
        hc = np.full(self.config.N_FAMILIES, 1)
        return hc


    def _compute_edu_efficiency(self, school_size):
        upper = .9 # lambda_2 in eq (8)
        lower = .1 # lambda_1 in eq (8)
        scale = 10 / self.config.N_FAMILIES
        inflection = self.config.N_FAMILIES / 2
        sigmoid = lower + (upper - lower) / (1 + np.exp(-scale*(school_size - inflection)))
        return sigmoid * school_size

    
    def _invest_education(self, parent_neighborhood, taxbase):
        """ eq(8) """
        ed = np.zeros(self.config.N_FAMILIES)
        for n in range(self.config.N_NEIGHBORHOODS):
            n_size = (parent_neighborhood == n).sum()
            econ_of_scale = self._compute_edu_efficiency(n_size)
            ed[parent_neighborhood == n] = taxbase[n] / econ_of_scale
        return ed


    def _form_skills(self, parent_income, parent_neighborhood):
        """ eq(10). must be increasing and show complementarity """
        # For now arbitrarily use income * avg(neighborhood_income)
        skill = np.zeros(self.config.N_FAMILIES)
        for n in range(self.config.N_NEIGHBORHOODS):
            # bound below by 1 so we dont get negative skill
            # TODO: actually fix/prevent negative skill due to low income
            par_income = np.maximum(1, parent_income[parent_neighborhood == n])
            # exclude parent income from avg <- eq (10) 
            avg_income = (par_income.sum() - par_income) / (par_income.size - 1)
            skill[parent_neighborhood == n] = np.log(par_income) * self.config.SKILL_FROM_PARENT_INCOME + \
                                              np.log(avg_income) * self.config.SKILL_FROM_NEIGHBOR_INCOME
        return skill


    def develop_human_capital(self, parent_income, parent_neighborhood, taxbase):
        """ eq(9) """
        ed = self._invest_education(parent_neighborhood, taxbase)
        skill = self._form_skills(parent_income, parent_neighborhood)
        # XXX: this multiplication is specified in the model but i dont like
        #       how you need edu (ie. taxes) to get hc from skill
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            prod = skill * ed
            if len(w):
                print('somethign bad')
        return prod
