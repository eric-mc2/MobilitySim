from numpy.random import default_rng
import numpy as np
import pandas as pd
import seaborn as sns


class Sim():

    def __init__(self):
        # Parameters
        self.N_FAMILIES = 50
        self.N_TIMESTEPS = 100
        self.N_NEIGHBORHOODS = 2 # TODO: make endogeneous
        self.INCOME_GROWTH = 0   # alpha in eq(1)
        self.PARENTAL_INVESTMENT_COEF = 0  # beta in eq(1)
        self.CAPITAL_EFFICIENCY = .1 # phi in eq(4)
        self.INCOME_NOISE_ADDITIVE = 1 # epsilon in eq(1) 
        self.INCOME_NOISE_AUTOREG = 1 # epsilon in eq(1)
        self.TAX_RATE = .1
        self.UTILITY_CONSUMPTION = .5
        self.UTILITY_INCOME = (1 - self.UTILITY_CONSUMPTION)
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

    def __generate_earned_income(self, child_capital):
        """ eq (4) """
        return (self.CAPITAL_EFFICIENCY
                * child_capital
                * self.__generate_white_noise(self.N_FAMILIES, mean=1))
        
    def __inherit_income(self, parent_income):
        """ pass down money directly to offspring """
        # follows eq(1) for now
        return self.PARENTAL_INVESTMENT_COEF * parent_income

    def __inherit_shock(self, parent_noise):
        """part of epsilon, the MA(1) process from eq (1)"""
        return self.INCOME_NOISE_AUTOREG * parent_noise

    def __income_shock(self):
        return self.INCOME_NOISE_ADDITIVE * self.__generate_white_noise(self.N_FAMILIES)

    def __generate_ma_income(self, parent_noise):
        return self.__inherit_shock(parent_noise) + self.__income_shock()

    def __transmit_income(self, parent_income, parent_noise, child_capital):
        """one intergenerational timestep. eq(1) """
        income_from_parent = self.__inherit_income(parent_income)
        earned_income = self.__generate_earned_income(child_capital)
        ma_noise = self.__generate_ma_income(parent_noise)
        offspring_income = (self.INCOME_GROWTH + 
                            income_from_parent +
                            earned_income +
                            ma_noise)
                            
        return offspring_income, ma_noise

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

    def __compute_taxes(self, adult_income):
        taxable = adult_income > 0
        return adult_income * taxable * self.TAX_RATE
        
    def __compute_tax_revenue(self, taxes, adult_neighborhood):
        return [taxes[adult_neighborhood == n].sum() 
                for n in range(self.N_NEIGHBORHOODS)]

    def __pay_taxes(self, adult_income, adult_neighborhood):
        taxes = self.__compute_taxes(adult_income)
        income_after_tax = adult_income - taxes
        taxbase = self.__compute_tax_revenue(taxes, adult_neighborhood)
        return income_after_tax, taxbase

    def __education_economy(self, school_size):
        upper = .9 # lambda_2 in eq (8)
        lower = .1 # lambda_1 in eq (8)
        scale = 10 / self.N_FAMILIES
        inflection = self.N_FAMILIES / 2
        sigmoid = lower + (upper - lower) / (1 + np.exp(-scale*(school_size - inflection)))
        return sigmoid * school_size

    def __receive_human_capital(self, parent_neighborhood, taxbase):
        hc = np.zeros(self.N_FAMILIES)
        for n in range(self.N_NEIGHBORHOODS):
            n_size = (parent_neighborhood == n).sum()
            scaled_size = self.__education_economy(n_size)
            hc[parent_neighborhood == n] = taxbase[n] / scaled_size
        return hc

    def __compute_utility(self, adult_income, adult_neighborhood, taxbase):
        """ eq(3). there's no point in using this yet since we have PARENTAL_INVESTMENT_COEF"""
        # right now assume adults only know their own income and 
        # each neihborhoods' tax base and population
        # and the efficiency of human capital
        known_rng = default_rng.rng(seed=42)
        known_noise = np.zeros(self.N_FAMILIES)
        ex_child_capital = self.__receive_human_capital(adult_neighborhood, taxbase)
        ex_consumption = (1-self.PARENTAL_INVESTMENT_COEF) * adult_income
        ex_child_income = (self.PARENTAL_INVESTMENT_COEF * adult_income
                            + self.CAPITAL_EFFICIENCY * ex_child_capital)
        return (self.UTILITY_CONSUMPTION * np.log(ex_consumption)
                + self.UTILITY_INCOME * np.log(ex_child_income))

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
            income[t, :], taxbase = self.__pay_taxes(income[t, :], neighborhoods[t, :])
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
            cols = [f"family_{i}" for i in range(result.shape[1])]
            self.data = pd.DataFrame(result, columns=cols)
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

    @classmethod
    def gini(cls, income_df):
        """ income is ordered time x family """
        income = income_df.to_numpy()
        min_income = income.min(axis=1).reshape((income.shape[0], 1))
        min_income[min_income > 0] = 0
        positive_income = income - min_income
        total_income = positive_income.sum(axis=1).reshape((income.shape[0], 1))
        lorenz = np.sort(positive_income, axis=1).cumsum(axis=1) / total_income
        return .5 - (lorenz.sum(axis=1) / income.shape[1])

    def add(self, result):
        self.data = pd.concat([self.data, 
                        pd.Series(result.data.mean(axis=1), name=f"mean_{self.ntrials}"), 
                        pd.Series(result.data.std(axis=1), name=f"sd_{self.ntrials}"),
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
                                pd.Series(result.data.std(axis=1), name=f"sd"),
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
    
    def add(self, result, param_val):
        self.income.add(result.income, param_val)
        self.neighborhood_size.add(result.neighborhood_size, param_val)
        self.human_capital.add(result.human_capital, param_val)


if __name__ == '__main__':
    sim = Sim()
    sim.run()