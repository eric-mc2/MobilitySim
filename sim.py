from numpy.random import default_rng
import numpy as np
import pandas as pd
import scipy
import seaborn as sns

class Sim():

    def __init__(self):
        # Parameters
        self.N_FAMILIES = 50
        self.N_TIMESTEPS = 100
        self.N_NEIGHBORHOODS = 2
        self.INCOME_GROWTH = 0   # alpha in eq(1)
        self.INCOME_MOBILITY_COEF = 0  # beta in eq(1)
        self.INCOME_NOISE_AUTOREG = 0 
        self.TAX_RATE = .5
        self.PREF_CONSUMPTION = .5
        self.PREF_INCOME = 1 - self.PREF_CONSUMPTION
        self.rng = default_rng(seed=12345)

    def set(self, param, value):
        if hasattr(self, param):
            setattr(self, param, value)
        else:
            print(f"Error: Invalid parameter {param}")
    
    def __generate_white_noise(self, size, mean=0, var=1):
        """returns `size` random samples"""
        # any white noise process will do
        return self.rng.normal(mean, var, size)

    def __generate_income_noise(self, parent_noise=None):
        """aka epsilon, a MA(1) process.  from eq (1)"""
        noise = self.__generate_white_noise(self.N_FAMILIES)
        if parent_noise is not None:
            noise += self.INCOME_NOISE_AUTOREG * parent_noise
        return noise
        
    def __generate_mobility(self, parent_income):
        """ beta in eq(1) and eq(2) """
        # follows eq(1) for now
        return np.full(parent_income.shape, self.INCOME_MOBILITY_COEF)

    def __transmit_income(self, parent_income, parent_noise, child_capital):
        """one intergenerational timestep. eq(1) """
        # TODO: switch to eq(4) but keep individual parental investment as an option
        mobility = self.__generate_mobility(parent_income)
        noise = self.__generate_income_noise(parent_noise)
        offspring_income = self.INCOME_GROWTH + mobility * parent_income + noise
        return offspring_income, noise

    def __initialize_income(self):
        """ create initial income distribution """
        # this is arbitrary right now
        income = np.full(self.N_FAMILIES, 1)
        return income, np.zeros(income.shape)

    def __initialize_human_capital(self):
        """ create initial human capital distribution """
        # this is arbitrary right now
        hc = np.full(self.N_FAMILIES, 1)
        return hc

    def __initialize_neighborhoods(self):
        """ create initial neighborhood selection """
        # this is arbitrary right now
        neighborhoods = np.full(self.N_FAMILIES, 0)
        neighborhoods[0:int(self.N_FAMILIES/2)] = 1
        return neighborhoods

    def __pick_neighborhood(self, adult_income, child_neighborhood):
        """ select into neighborhoods """
        # this is arbitrary now. should use differential selection
        return child_neighborhood

    def __calculate_taxes(self, adult_income, adult_neighborhood):
        revenue = np.zeros(self.N_NEIGHBORHOODS)
        for n in range(self.N_NEIGHBORHOODS):
            taxes = adult_income[adult_neighborhood == n] * self.TAX_RATE
            revenue[n] = taxes.sum()
        return revenue

    def __pay_taxes(self, adult_income, adult_neighborhood):
        revenue = np.zeros(self.N_NEIGHBORHOODS)
        for n in range(self.N_NEIGHBORHOODS):
            taxes = adult_income[adult_neighborhood == n] * self.TAX_RATE
            adult_income[adult_neighborhood == n] -= taxes
            revenue[n] = taxes.sum()
        return revenue

    def __receive_human_capital(self, parent_neighborhood, taxbase):
        hc = np.zeros(self.N_FAMILIES)
        for n in range(self.N_NEIGHBORHOODS):
            n_size = (parent_neighborhood == n).sum()
            hc[parent_neighborhood == n] = taxbase[n] / n_size
        return hc

    def __compute_utility(self, adult_consumption, adult_neighborhood, adult_income, income_noise, adult_capital):
        """ eq(3) """
        # expected child income part is pretty arbitrary 
        return np.full(self.N_FAMILIES, 1)
        # right now assume adults have perfect information about all other
        # adult's neighborhoods and incomes
        # known_self.rng = default_self.rng(seed=42)
        # ex_taxbase = calculate_taxes(adult_income, adult_neighborhood)
        # ex_child_capital = receive_human_capital(adult_neighborhood, ex_taxbase)
        # ex_child_income = transmit_income(known_self.rng, adult_income, income_noise, x_child_capital)
        # return self.PREF_CONSUMPTION * np.log(adult_consumption) \
        #         + PREF_INzCOME * np.log(ex_child_income)

    def __maximize_utility(self, adult_consumption, adult_neighborhood, adult_income):
        """ eq(3) """
        pass

    def __census(self, adult_neighborhood):
        n_size = np.zeros(self.N_NEIGHBORHOODS)
        for n in range(self.N_NEIGHBORHOODS):
            n_size[n] = (adult_neighborhood == n).sum()
        return n_size

    def __run(self):
        income = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        neighborhoods = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        neighborhood_size = np.zeros((self.N_TIMESTEPS, self.N_NEIGHBORHOODS))
        human_capital = np.zeros((self.N_TIMESTEPS, self.N_FAMILIES))
        taxbase = np.zeros(self.N_NEIGHBORHOODS)
        income[0, :], income_noise = self.__initialize_income()
        neighborhoods[0, :] = self.__initialize_neighborhoods()
        neighborhood_size[0, :] = self.__census(neighborhoods[0, :])
        human_capital[0, :] = self.__initialize_human_capital()

        for t in range(1, self.N_TIMESTEPS):
            # Adult things
            income[t, :], income_noise = self.__transmit_income(income[t-1, :], income_noise, human_capital[t-1, :])
            neighborhoods[t, :] = self.__pick_neighborhood(income[t-1, :], neighborhoods[t-1, :])
            neighborhood_size[t, :] = self.__census(neighborhoods[t, :])
            taxbase = self.__pay_taxes(income[t, :], neighborhoods[t, :])
            # Child things
            human_capital[t, :] = self.__receive_human_capital(neighborhoods[t, :], taxbase)
        
        return SimResult(income, neighborhoods, neighborhood_size, human_capital)

    def run(self, ntrials=1, keep_trials=False):
        result = SimResultAgg(keep_trials)
        for trial in range(ntrials):
            result.add(self.__run())
        return result

    def run_sweep(self, param, values, ntrials=1):
        result = SimResultSweep()
        for value in values:
            self.set(param, value)
            result.add(self.run(ntrials), value)
        return result


class SimResultData():
        def __init__(self, result, name):
            self.data = result
            self.name = name

        def plot(self):
            sns.relplot(data=self.data, kind='line', legend=False).set(title=self.name)
    

class SimResult():
    def __init__(self, income, neighborhoods, neighborhood_size, human_capital):
        self.income = SimResultData(income, "Income")
        self.neighborhood = SimResultData(neighborhoods, "Neighborhoods")
        self.neighborhood_size = SimResultData(neighborhood_size, "Neighborhood Size")
        self.human_capital = SimResultData(human_capital, "Capital")


class SimResultAggData():
    def __init__(self, name, keep_trials=False):
        self.data = pd.DataFrame()
        self.name = name
        self.ntrials = 0
        self.trial_data = []
        self.keep_trials = keep_trials

    def add(self, result):
        self.data = pd.concat([self.data, 
                        pd.Series(result.data.mean(axis=1), name=f"mean_{self.ntrials}"), 
                        pd.Series(result.data.std(axis=1), name=f"sd_{self.ntrials}")], 
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
                    kind='line') \
                .set_titles(col_template="{col_name}")
        rplt.fig.subplots_adjust(top=0.9)
        rplt.fig.suptitle(self.name)


class SimResultAgg():
    def __init__(self, keep_trials=False):
        self.ntrials = 0
        self.income = SimResultAggData("Income", keep_trials)
        self.neighborhood_size = SimResultAggData("Neighborhood Size", keep_trials)
        self.human_capital = SimResultAggData("Capital", keep_trials)
    
    def add(self, result):
        self.income.add(result.income)
        self.neighborhood_size.add(result.neighborhood_size)
        self.human_capital.add(result.human_capital)


class SimResultSweepData():
    def __init__(self, name):
        self.data = pd.DataFrame()
        self.name = name

    def add(self, result, param_val):
        param_idx = pd.Index([param_val]).repeat(result.data.shape[0])
        tuples = list(zip(param_idx, np.arange(result.data.shape[0])))
        new_idx = pd.MultiIndex.from_tuples(tuples, names=["Param", "Time"])
        result_data = pd.concat([pd.Series(result.data.mean(axis=1), name=f"mean"), 
                                pd.Series(result.data.std(axis=1), name=f"sd")], 
                                axis=1)  
        result_data.set_index(new_idx, inplace=True)
        self.data = pd.concat([self.data, result_data], axis=0)
    
    def plot(self):
        if self.data.empty:
            print("Error: Nothing to plot")
            return
        pdata = self.data.reset_index().melt(id_vars=['Param','Time'],var_name='Agg')
        rplt = sns.relplot(data=pdata, x='Time', y='value', col='Agg', hue='Param',
                    kind='line') \
                .set_titles(col_template="{col_name}")
        rplt.fig.subplots_adjust(top=0.9)
        rplt.fig.suptitle(self.name)

    
class SimResultSweep():
    def __init__(self):
        self.income = SimResultSweepData("Income")
        self.neighborhood_size = SimResultSweepData("Neighborhood Size")
        self.human_capital = SimResultSweepData("Capital")
    
    def add(self, result, param_val):
        self.income.add(result.income, param_val)
        self.neighborhood_size.add(result.neighborhood_size, param_val)
        self.human_capital.add(result.human_capital, param_val)