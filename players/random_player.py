import random

from players.player import *
from logic.state import State

class Random(Player):
    name = "Random player"
    def play(self, state: State, map: Map, history: set[State]):
        return random.choice(state.get_legal_actions())
