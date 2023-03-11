import math

from state import State
from type import Action, Owner, Car, Direction
from player import *

DEPTH_LIMIT = 3
class MinimaxPlayer(Player):
    name = "MinMax Player"
    # TODO: Add depth to transpositions, since it is important at which depth a state was analyzed
    transpositions: dict[State, (float, Action, int)]
    history: set[State]
    owner: Owner
    map: Map

    def __init__(self) -> None:
        super().__init__()
        self.transpositions = {}

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map
        print(self.owner)
        print(f"initial heuristic {self.heuristic(state)}")
        v, move = self.__max_value(state, 0, 0)
        print(f"selected move: {repr(move)} value: {v}")
        print(f"final heuristic {self.heuristic(state.apply_action(move))}")
        return move

    def __max_value(self, state: State, depth: int, exclude_car: Car) -> tuple[float, Action]:
        if state.get_winner() != None:
            return -100000000 + depth, None
        elif state in self.history and depth != 0:
            # print("it is in history")
            return math.inf, None 
        elif depth == DEPTH_LIMIT: 
            return self.heuristic(state), None
        
        transposition = self.transpositions.get(state)
        if transposition != None and transposition[2] <= depth:
            return (transposition[0], transposition[1])

        v = -math.inf
        move = None            
        for a in state.get_legal_actions():
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we we applied a shift then we assume the opponent won't shift
                continue
            v2, a2 = self.__min_value(state.apply_action(a), depth + 1, moved_car)
            if v2 >= v:
                v, move = v2, a
            
            self.transpositions[state] = (v, move, depth)
        return v, move

    def __min_value(self, state: State, depth: int, exclude_car: Car) -> tuple[float, Action]:
        if state.get_winner() != None:
            return 100000000 - depth, None
        elif state in self.history:
            # print("(MIN)it is in history")
            return -math.inf, None
        elif depth == DEPTH_LIMIT: 
            return self.heuristic(state), None
        
        transposition = self.transpositions.get(state)
        if transposition != None and transposition[2] <= depth:
            return (transposition[0], transposition[1])

        v = math.inf
        move = None
        for a in state.get_legal_actions():
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we we applied a shift then we assume the opponent won't shift
                continue
            v2, a2 = self.__max_value(state.apply_action(a), depth + 1, moved_car)
            if v2 <= v:
                v, move = v2, a

            self.transpositions[state] = (v, move, depth)
        return v, move
