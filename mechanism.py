# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Base class for simulation mechanisms

from config import Config, Globals

class SimMech():
    def __init__(self, config: Config, globals: Globals):
        self.config = config
        self.globals = globals
        
    def generate_white_noise(self, size:int, mean=0, var=1):
        """returns `size` random samples"""
        # any white noise process will do
        return self.globals.rng.normal(mean, var, size)