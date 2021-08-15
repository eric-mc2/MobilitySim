# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: A simulation of intergenerational mobility
# Description: Modeled after the Durlauf-Seshadri paper "Understanding the
#   Great Gatsby Curve"

from results import SimResult, SimResultAgg, SimResultSweep
from income import Income
from config import Config, Globals, HoodFormation
from human_capital import HumanCapital
from neighborhood import Neighborhood, StaticNeighborhood, SortedPairsNeighborhood, SortedNeighborhood

# TODO: Set a baseline consumption of 1 unit of income. Their preferences kick in above this threshold. 
#       People die if they can't meet this consumption. This sets a natural scale on the income units and is
#       convenient because it helps us take log(y>1).
class Sim():

    def __init__(self):
        self.config = Config()
        self.globals = Globals()
        self.income = Income(self.config, self.globals)
        self.capital = HumanCapital(self.config, self.globals)
        switch = {
            HoodFormation.STATIC : StaticNeighborhood(self.config, self.globals),
            HoodFormation.PERFECT_SORTING_PAIRS : SortedPairsNeighborhood(self.config, self.globals),
            HoodFormation.PERFECT_SORTING : SortedNeighborhood(self.config, self.globals)
        }
        self.neighborhood = switch[self.config.HOOD_FORMATION]    

    def set(self, param: str, value: float):
        self.config.set(param, value)


    def _run_trial(self) -> SimResult:
        self.globals.t = 0
        self.income.initialize_income()
        self.capital.initialize_human_capital()
        self.neighborhood.initialize_neighborhoods()
        
        for t in range(1, self.config.N_TIMESTEPS):
            self.globals.t = t
            # Adult things
            self.income.inherit_income()
            self.income.earn_income(self.capital.earn_income())
            self.neighborhood.pick_neighborhood(self.income)
            taxbase = self.neighborhood.pay_taxes(self.income)
            # Child things
            self.capital.develop_human_capital(self.income, self.neighborhood, taxbase)
        
        return SimResult(self.income.income, self.neighborhood.hood,
            self.neighborhood.pop, self.capital.capital)


    def run(self, ntrials=1, keep_trials=False) -> SimResultAgg:
        result = SimResultAgg(keep_trials)
        for trial in range(ntrials):
            result.add(self._run_trial())
        return result


    def run_sweep(self, param: str, values: list, ntrials=1) -> SimResultSweep:
        result = SimResultSweep()
        for value in values:
            self.config.set(param, value)
            result.add(self.run(ntrials), value)
        return result
