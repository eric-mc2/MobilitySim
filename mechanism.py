# Author: Eric Chandler <echandler@uchicago.edu>
# Brief: Base class for simulation mechanisms

from config import Config, Globals

class SimMech():
    def __init__(self, config: Config, globals: Globals):
        self.config = config
        self.globals = globals
        