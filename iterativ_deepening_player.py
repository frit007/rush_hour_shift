import pygame
from time import sleep
import math

from state import State, Map
from type import Action, Owner, Direction, Car
from player import *
from ui import draw_state

def transposition_key(state:State):
    return state.minimized_state()

DEPTH_LIMIT = 5

class IterativeDeepeningPlayer(Player):
    name = "Iterative Deepening"
    # TODO: Add depth to transpositions, since it is important at which depth a state was analyzed
    transpositions: dict[State, (float, Action, int)]
    history: set[State]
    owner: Owner
    depth_limit: int
    map: Map

    def __init__(self) -> None:
        super().__init__()
        self.transpositions = {}

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map


        print(f"initial heuristic {self.heuristic(state)}")
        for depth_limit in range(1, DEPTH_LIMIT):
            self.depth_limit = depth_limit
            self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid")
        self.depth_limit = DEPTH_LIMIT
        v, move = self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid")
        print(f"selected move: {repr(move)} value: {v}")
        print(f"final heuristic {self.heuristic(state.apply_action(move))}")
        self.explain_path(state)
        # self.why_not_left(state)
        return move
    
    def why_not_left(self, state:State):
        for a in state.get_legal_actions():
            if len(a.moves) > 0 and a.moves[0].car.owner == Owner.PLAYER2 and a.moves[0].x_delta == -1:
                self.explain_path(state.apply_action(a))
                

    def explain_path(self, state:State):
        path = [state]
        i = DEPTH_LIMIT
        while i > 0:
            i -= 1
            transposition = self.transpositions.get(transposition_key(state))
            if(transposition != None):
                print(transposition[1])
                state = state.apply_action(transposition[1])
                path.append(state)
            else:
                break
        for s in path:
            draw_state(s)
            pygame.display.flip()
            sleep(0.3)


    def __max_value(self, state: State, depth: int, alpha:float, beta:float,  exclude_car: Car) -> tuple[float, Action]:
        # print(f"depth {depth}")
        if state.get_winner() != None:
            return -100000000 + depth, None
        elif state in self.history and depth != 0:
            return math.inf, None
        elif depth >= self.depth_limit: 
            return self.heuristic(state), None

        transposition = self.transpositions.get(transposition_key(state))
        if transposition != None and transposition[2] <= depth + (DEPTH_LIMIT - self.depth_limit):
            return (transposition[0], transposition[1])

        v = -math.inf
        move = None


        applied_actions = []
        i = 0
        for a in state.get_legal_actions():
            i += 1
            next_state = state.apply_action(a)
            transposition = self.transpositions.get(transposition_key(state))
            estimated_score = 0
            if transposition != None:
                estimated_score = transposition[2]
            else:
                estimated_score = self.heuristic(next_state)
            # The second argument is used to sort because we cannot sort actions or states
            applied_actions.append((estimated_score, i, a, next_state))

        applied_actions.sort(reverse=True)

        for (estimated_score, _, a, next_state) in applied_actions:
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we applied a shift then we assume the opponent won't shift
                continue
            v2, a2 = self.__min_value(next_state, depth + 1, alpha=alpha, beta=beta, exclude_car=moved_car)
            if v2 > v:
                v, move = v2, a
                self.transpositions[transposition_key(state)] = (v, move, depth + (DEPTH_LIMIT - self.depth_limit))
                alpha = max(alpha, v)

            if v >= beta:
                return v, move
        return v, move

    def __min_value(self, state: State, depth: int, alpha: float, beta: float, exclude_car: Car) -> tuple[float, Action]:
        if state.get_winner() != None:
            return 100000000 - depth, None
        elif state in self.history:
            return -math.inf, None
        elif depth >= self.depth_limit: 
            return self.heuristic(state), None
        
        transposition = self.transpositions.get(transposition_key(state))
        if transposition != None and transposition[2] <= depth + (DEPTH_LIMIT - self.depth_limit):
            return (transposition[0], transposition[1])



        applied_actions = []
        i = 0
        for a in state.get_legal_actions():
            i += 1
            next_state = state.apply_action(a)
            transposition = self.transpositions.get(transposition_key(state))
            estimated_score = 0
            if transposition != None:
                estimated_score = transposition[2]
            else:
                estimated_score = self.heuristic(next_state)
            # The second argument is used to sort because we cannot sort actions or states
            applied_actions.append((estimated_score, i, a, next_state))

        applied_actions.sort(reverse=False)

        v = math.inf
        move = None
        selected_by_alpha = None
        for (estimated_score, _, a, next_state) in applied_actions:
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we applied a shift then we assume the opponent won't shift
                continue
            v2, a2 = self.__max_value(next_state, depth + 1, alpha=alpha, beta=beta, exclude_car=moved_car)
            if v2 < v:
                v, move = v2, a
                beta = min(beta, v)
                self.transpositions[transposition_key(state)] = (v, move, depth + (DEPTH_LIMIT - self.depth_limit))
            
            if v <= alpha:
                return v, move
        return v, move
