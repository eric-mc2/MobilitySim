# For debugging the Sim

from sim import Sim

sim = Sim()

sim.set('PARENTAL_INVESTMENT_COEF', .9) # directly transmits less taxes

sim.set('SKILL_FROM_NEIGHBOR_INCOME', .5)
sim.set('SKILL_FROM_PARENT_INCOME', .5)
sim.set('CAPITAL_EFFICIENCY', .7)
# sim.set('INCOME_NOISE_ADDITIVE', 1)
# sim.set('INCOME_NOISE_AUTOREG', 1)
sim.set('TAX_RATE', .1)


res = sim.run(20)


res.income.plot()
res.human_capital.plot()