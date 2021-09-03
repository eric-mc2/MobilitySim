# For debugging the Sim

from sim import Sim

sim = Sim()

sim.set('INCOME_GROWTH', 0)
sim.set('PARENTAL_INVESTMENT_COEF', 1)
sim.set('TAX_RATE', .5)
sim.set('SKILL_FROM_INCOME', .5)
sim.set('CAPITAL_EFFICIENCY', 1.5)

res=sim.run()