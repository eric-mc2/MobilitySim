# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Base class for simulation mechanisms

import numpy as np
from config import Config, Globals

class SimMech():
    def __init__(self, config: Config, globals: Globals):
        self.config = config
        self.globals = globals
        
    def generate_white_noise(self, size:int, mean=0, var=1, min=None):
        """returns `size` random samples"""
        # any white noise process will do
        draw = self.globals.rng.normal(mean, var, size)
        if min is not None:
            return np.maximum(min, draw)
        else:
            return draw