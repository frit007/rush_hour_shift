import math
from logic.state import State, Map
from logic.state import State, Map, CarState, RoadState
from logic.type import Owner, Direction
from heuristics.heuristic_a import *
from heuristics.heuristic_b import *

class Player:
    name: str
    owner: Owner
    map: Map
    
    def play(self, state: State, map: Map, history: set[State]):
        pass

    def heuristic(self, state: State, optimize_for: Owner = None):
        if hasattr(self, 'use_heuristic'):
            return self.use_heuristic(self, state, optimize_for)
        else:
            return heuristic_a(self, state, optimize_for)
