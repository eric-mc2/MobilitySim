# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Intergenerational human capital transition mechanism

from mechanism import SimMech
from income import Income
from neighborhood import Neighborhood
import numpy as np
from numpy import ndarray
import warnings
from config import Config, Globals

class HumanCapital(SimMech):
    def __init__(self, config: Config, globals: Globals):
        super().__init__(config, globals)
        self.capital = np.zeros((config.N_TIMESTEPS, config.N_FAMILIES))

        
    def initialize_human_capital(self):
        """ create initial human capital distribution """
        # this is arbitrary right now
        self.capital[0, :] = np.full(self.config.N_FAMILIES, 1)


    def _compute_edu_efficiency(self, pop: int):
        upper = self.config.EDU_EFFICIENCY_UPPER # lambda_2 in eq (8)
        lower = self.config.EDU_EFFICIENCY_LOWER # lambda_1 in eq (8)
        scale = 10 / self.config.N_FAMILIES
        inflection = self.config.N_FAMILIES / 2
        sigmoid = lower + (upper - lower) / (1 + np.exp(-scale*(pop - inflection)))
        return sigmoid * pop

    
    def _invest_education(self, neighborhoods: Neighborhood, taxbase: ndarray):
        """ eq(8) """
        investment = np.zeros(self.config.N_FAMILIES)
        parent_neighborhood = neighborhoods.hood[self.globals.t, :]
        for n in range(neighborhoods.hood_count):
            pop = neighborhoods.pop[self.globals.t, n]
            econ_of_scale = self._compute_edu_efficiency(pop)
            investment[parent_neighborhood == n] = taxbase[n] / econ_of_scale
        return investment


    def _form_skills(self, income: Income, neighborhoods: Neighborhood):
        """ zeta(*) from eq(10). must be increasing and show complementarity """
        skill = np.zeros(self.config.N_FAMILIES)
        parent_income = income.income[self.globals.t, :]
        # print(f"t={self.globals.t}; Income = {np.sum(parent_income)}")
        parent_neighborhood = neighborhoods.hood[self.globals.t, :]
        for n in range(neighborhoods.hood_count):
            # bound below by 1 so we dont get negative skill
            # TODO: actually fix/prevent negative skill due to low income
            par_income = np.maximum(1, parent_income[parent_neighborhood == n])
            # eq (10): we exclude parent income from avg 
            avg_income = (par_income.sum() - par_income) / (par_income.size - 1)
            # skill[parent_neighborhood == n] = np.log(par_income) * self.config.SKILL_FROM_PARENT_INCOME + \
            #                                   np.log(avg_income) * self.config.SKILL_FROM_NEIGHBOR_INCOME
            # skill[parent_neighborhood == n] = self.config.SKILL_FROM_INCOME * \
            #                                 np.log(par_income) * np.log(avg_income)
            skill[parent_neighborhood == n] = self.config.SKILL_FROM_INCOME * \
                                            par_income * avg_income
        return skill


    def earn_income(self):
        """ eq (4) """
        capital_as_child = self.capital[self.globals.t-1, :]
        predictable_income = (self.config.CAPITAL_EFFICIENCY * capital_as_child)
        shock = self.generate_white_noise(self.config.N_FAMILIES, mean=1, var=self.config.SKILL_NOISE_SD)
        earned_income = predictable_income * shock
        # print(f"t={self.globals.t}; Earned Income = {np.sum(earned_income)}")
        return earned_income
    

    def develop_human_capital(self, income: Income, neighborhoods: Neighborhood, taxbase: ndarray):
        """ 
            implements eq(9) 
            note: human capital develops in a child's context, therefore:
                income[t] == parents, neighborhood[t] == parents
        """
        ed = self._invest_education(neighborhoods, taxbase)
        skill = self._form_skills(income, neighborhoods)
        # XXX: this multiplication is specified in the model but i dont like
        #       how you need edu (ie. taxes) to get hc from skill
        with warnings.catch_warnings(record=True) as w:
            warnings.simplefilter("error")
            hc = skill * ed
            if len(w):
                self.globals.logger.critical('numerical instability!')
        # print(f"t={self.globals.t}; Taxes = {np.sum(taxbase)}")
        # print(f"t={self.globals.t}; Ed = {np.sum(ed)}")
        # print(f"t={self.globals.t}; Skill = {np.sum(skill)}")
        # print(f"t={self.globals.t}; HC = {np.sum(hc)}")
        self.capital[self.globals.t, :] = hc
        return hc
