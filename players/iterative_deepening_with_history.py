import math
from time import sleep
from players.player import Player
from logic.state import Map, State
from logic.type import Action, Car, Direction, Owner
import pygame

from ui.game import draw_state


def transposition_key(state:State):
    return state.minimized_state()

DEPTH_LIMIT = 5

class IterativeDeepeningPlayerWithHistory(Player):
    name = "Greedy deepening"
    transpositions: dict[State, (float, Action, int)]
    history: set[State]
    owner: Owner
    depth_limit: int
    map: Map

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map
        self.transpositions = {}

        for depth_limit in range(1, DEPTH_LIMIT):
            self.depth_limit = depth_limit
            self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid", actions=[])
        
        self.depth_limit = DEPTH_LIMIT
        v, b, move = self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid", actions=[])
        
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
                state = state.apply_action(transposition[1])
                path.append(state)
            else:
                break
        for s in path:
            draw_state(s, self.map)
            pygame.display.flip()
            sleep(0.3)


    def __max_value(self, state: State, depth: int, alpha:float, beta:float,  exclude_car: Car, actions: list[Action]) -> tuple[float, Action]:
        if state.get_winner(self.map) != None:
            return -100000000 + depth * 1000, 0, None
        elif state in self.history and depth != 0:
            return math.inf, 0, None
        elif depth >= self.depth_limit: 
            return self.heuristic(state), self.path_bonus(actions), None

        transposition = self.transpositions.get(transposition_key(state))
        if transposition != None and transposition[2] <= depth + (DEPTH_LIMIT - self.depth_limit):
            return (transposition[0], self.path_bonus(actions), transposition[1])



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

        v = -math.inf
        bestValue = v
        b = 0
        move = None
        for (estimated_score, _, a, next_state) in applied_actions:
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we applied a shift then we assume the opponent won't shift
                continue
            v2, b2, a2 = self.__min_value(next_state, depth + 1, alpha=alpha, beta=beta, exclude_car=moved_car, actions=[*actions, a])
            value = v2 + b2
            if v > v2:
                self.transpositions[transposition_key(state)] = (v2, a, depth + (DEPTH_LIMIT - self.depth_limit))

            if value > bestValue:
                bestValue, v, b, move = value, v2, b2, a
                alpha = max(alpha, bestValue)

            if bestValue >= beta:
                return v, b, move
        return v, b, move

    def __min_value(self, state: State, depth: int, alpha: float, beta: float, exclude_car: Car, actions: list[Action]) -> tuple[float, float, Action]:
        if state.get_winner(self.map) != None:
            return 100000000 - depth * 1000, 0, None
        elif state in self.history:
            return -math.inf, 0, None
        elif depth >= self.depth_limit: 
            return self.heuristic(state), self.path_bonus(actions), None
        
        transposition = self.transpositions.get(transposition_key(state))
        if transposition != None and transposition[2] <= depth + (DEPTH_LIMIT - self.depth_limit):
            return (transposition[0], self.path_bonus(actions), transposition[1])



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

        bestValue = math.inf
        v = math.inf
        b = 0
        move = None
        for (estimated_score, _, a, next_state) in applied_actions:
            moved_car = a.moves[0].car if len(a.moves) > 0 else None
            if moved_car == exclude_car:
                # assume the opponent is not going to undo the move we just made, so the ai makes some progress
                # An implicit part and for now intended part of this is that we applied a shift then we assume the opponent won't shift
                continue
            v2, b2, a2 = self.__max_value(next_state, depth + 1, alpha=alpha, beta=beta, exclude_car=moved_car, actions=[*actions, a])
            value = v2 + b2
            if v < v2:
                self.transpositions[transposition_key(state)] = (v2, a, depth + (DEPTH_LIMIT - self.depth_limit))

            if value < bestValue:
                bestValue, v, b, move = value, v2, b2, a
                beta = min(beta, bestValue)
                
            
            if bestValue <= alpha:
                return v, b, move
        return v, b, move

    def path_bonus(self, actions: list[Action]):
        movement_bonus = 0

        stepBonus = 10
        potentialBonus= len(actions) * stepBonus
        wanted_direction = [1,2,3] if self.owner == Owner.PLAYER1 else [-1,-2,-3]
        for action in actions:
            if (len(action.moves) > 0 
                and action.moves[0].car.owner == self.owner):
                move = action.moves[0]
                if move.x_delta in wanted_direction:
                    movement_bonus += potentialBonus * abs(move.x_delta)
                else:
                    movement_bonus -= potentialBonus * abs(move.x_delta)
            potentialBonus -= stepBonus
        
        return movement_bonus
