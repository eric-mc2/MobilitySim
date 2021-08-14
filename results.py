# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Data structure for simulation results

from pandas.core.frame import DataFrame
from mechanism import SimMech
from sim import Sim
import numpy as np
import pandas as pd
import seaborn as sns

class SimResultData():
        def __init__(self, result: SimMech, name: str):
            cols = [f"family_{i}" for i in range(result.shape[1])]
            self.data = pd.DataFrame(result, columns=cols)
            self.name = name

        def plot(self):
            sns.relplot(data=self.data, kind='line', legend=False).set(title=self.name)
    

class SimResult():
    def __init__(self, sim: Sim):
        self.income = SimResultData(sim.income, "Income")
        self.neighborhood = SimResultData(sim.neighborhood.hood, "Neighborhoods")
        self.neighborhood_size = SimResultData(sim.neighborhood.pop, "Neighborhood Size")
        self.human_capital = SimResultData(sim.human_capital, "Capital")


class SimResultAggData():
    def __init__(self, name: str, keep_trials=False):
        self.data = pd.DataFrame()
        self.name = name
        self.ntrials = 0
        self.trial_data = []
        self.keep_trials = keep_trials

    @classmethod
    def gini(cls, income_df: DataFrame):
        """ income is ordered time x family """
        income = income_df.to_numpy()
        min_income = income.min(axis=1).reshape((income.shape[0], 1))
        min_income[min_income > 0] = 0
        positive_income = income - min_income # boost everyone's income in case of negative income
        total_income = positive_income.sum(axis=1).reshape((income.shape[0], 1))
        _lorenz = np.sort(positive_income, axis=1).cumsum(axis=1)
        lorenz = np.true_divide(_lorenz, total_income, out=np.zeros_like(_lorenz), where=total_income>0)
        return .5 - lorenz.mean(axis=1) # unit triangle - integral of lorenz

    def add(self, result: SimResultData):
        self.data = pd.concat([self.data, 
                        pd.Series(result.data.mean(axis=1), name=f"mean_{self.ntrials}"), 
                        pd.Series(result.data.std(axis=1), name=f"sd_{self.ntrials}")],
                        axis=1)
        if self.name in ["Income", "Capital"]:
            self.data = pd.concat([self.data, 
                            pd.Series(SimResultAggData.gini(result.data), name=f"gini_{self.ntrials}")],
                        axis=1)
        self.ntrials += 1
        if self.keep_trials:
            self.trial_data.append(result)

    def plot(self):
        if self.ntrials == 0:
            print("Error: Nothing to plot")
            return
        self.data.index.rename('Time', inplace=True)
        pdata = self.data.reset_index().melt(id_vars='Time')
        pdata = pd.concat([pdata.Time, pdata.variable.str.split("_", expand=True, n=1), pdata.value], axis=1)
        assert(len(pdata.columns) == 4)
        pdata.columns = ['Time','Agg','Trial','Value']
        rplt = sns.relplot(data=pdata, x='Time', y='Value', col='Agg', hue='Trial',
                    kind='line', facet_kws={'sharey':False}) \
                .set_titles(col_template="{col_name}")
        rplt.fig.subplots_adjust(top=0.9)
        rplt.fig.suptitle(self.name)


class SimResultAgg():
    def __init__(self, keep_trials=False):
        self.ntrials = 0
        self.income = SimResultAggData("Income", keep_trials)
        self.neighborhood_size = SimResultAggData("Neighborhood Size", keep_trials)
        self.human_capital = SimResultAggData("Capital", keep_trials)
    
    def add(self, result: SimResult):
        self.income.add(result.income)
        self.neighborhood_size.add(result.neighborhood_size)
        self.human_capital.add(result.human_capital)


class SimResultSweepData():
    def __init__(self, name: str):
        self.data = pd.DataFrame()
        self.name = name

    def add(self, result: SimResultAggData, param_val: float):
        param_idx = pd.Index([param_val]).repeat(result.data.shape[0])
        tuples = list(zip(param_idx, np.arange(result.data.shape[0])))
        new_idx = pd.MultiIndex.from_tuples(tuples, names=["Param", "Time"])
        result_data = pd.concat([pd.Series(result.data.mean(axis=1), name=f"mean"), 
                                pd.Series(result.data.std(axis=1), name=f"sd")],
                                axis=1)  
        if self.name in ["Income", "Capital"]:
            result_data = pd.concat([result_data,
                            pd.Series(SimResultAggData.gini(result.data), name=f"gini")],
                            axis=1)
        result_data.set_index(new_idx, inplace=True)
        self.data = pd.concat([self.data, result_data], axis=0)
    
    def plot(self):
        if self.data.empty:
            print("Error: Nothing to plot")
            return
        pdata = self.data.reset_index().melt(id_vars=['Param','Time'],var_name='Agg')
        rplt = sns.relplot(data=pdata, x='Time', y='value', col='Agg', hue='Param',
                    kind='line', facet_kws={'sharey':False}) \
                .set_titles(col_template="{col_name}")
        rplt.fig.subplots_adjust(top=0.9)
        rplt.fig.suptitle(self.name)

    
class SimResultSweep():
    def __init__(self):
        self.income = SimResultSweepData("Income")
        self.neighborhood_size = SimResultSweepData("Neighborhood Size")
        self.human_capital = SimResultSweepData("Capital")
    
    def add(self, result: SimResultAgg, param_val: float):
        self.income.add(result.income, param_val)
        self.neighborhood_size.add(result.neighborhood_size, param_val)
        self.human_capital.add(result.human_capital, param_val)
