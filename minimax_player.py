from state import State
from type import Action
from ui import *
from player import Player

class MinimaxPlayer(Player):
    def play(self, state: State) -> Action:
        v, move = self.__max_value(state)
        return move

    def __max_value(self, state: State) -> tuple[float, Action]:
        if state.get_winner() != None:
            return float(state.get_winner() == self.owner), None
        v = -math.inf

        for a in state.get_legal_actions(self.owner):
            v2, a2 = self.__min_value(state.apply_action(a))
            if v2 > v:
                v, move = v2, a
        return v, move

    def __min_value(self, state: State) -> tuple[float, Action]:
        if state.get_winner() != None:
            return float(state.get_winner() == self.opponent), None
        v = math.inf

        for a in state.get_legal_actions(self.opponent):
            v2, a2 = self.__max_value(state.apply_action(a))
            if v2 < v:
                v, move = v2, a
        return v, move
