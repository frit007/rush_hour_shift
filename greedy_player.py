from time import sleep
import time
from state import State
from type import Action
from ui import *
from player import Player
import pygame


def transposition_key(state:State):
    return state.minimized_state()
DEPTH_LIMIT = 1
class GreedyPlayer(Player):
    name = "Greedy Player"
    # TODO: Add depth to transpositions, since it is important at which depth a state was analyzed
    transpositions: dict[State, (float, Action, int)]
    history: set[State]
    owner: Owner
    depth_limit: int

    def __init__(self) -> None:
        super().__init__()
        self.transpositions = {}

    def play(self, state: State, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn


        print(f"initial heuristic {self.heuristic(state)}")
        for depth_limit in range(1, DEPTH_LIMIT):
            self.depth_limit = depth_limit
            self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid")
        self.depth_limit = DEPTH_LIMIT
        v, move = self.__max_value(state, 0, alpha=-math.inf, beta=math.inf, exclude_car="invalid")
        print(f"selected move: {repr(move)} value: {v}")
        print(f"final heuristic {self.heuristic(state.apply_action(move))}")
        # self.explain_path(state)
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

    def heuristic(self, state:State):
        player1_car, player2_car = state.get_player_cars()

        # player2_score = player_2_car.x

        # score = abs(player2_score - 12)

        score = 0
        player1_blocking = 0
        player2_blocking = 0
        
        # Include road
        player1_roadblocks = 0
        for road in state.roads:
            if (not(player1_car.y >= road.from_y() 
                and player1_car.y <= road.to_y())
                and player1_car.x <= road.from_x()):
                
                player1_roadblocks += road.to_x() - road.from_x() + 1

        player2_roadblocks = 0
        for road in state.roads:
            if (not(player2_car.y >= road.from_y() 
                and player2_car.y <= road.to_y())
                and player2_car.x >= road.to_x()):
                
                player2_roadblocks += road.to_x() - road.from_x() + 1
        # return player2_roadblocks
        # print(f"p1 blocks {player1_roadblocks}; p2 blocks {player2_roadblocks}")
        for x in range(player1_car.x + 2, 13):
            car = state.car_map.get((x, player1_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player1_blocking += 50
                player1_blocking += 1
            
        for x in range(player2_car.x - 1, 0, -1):
            car = state.car_map.get((x, player2_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player2_blocking += 10
                player2_blocking += 1

        player1_score = - player1_blocking - player1_roadblocks + abs(player1_car.x - 0) * 20
        player2_score = - player2_blocking - player2_roadblocks + abs(player2_car.x - 12) * 20

        if self.owner == Owner.PLAYER1:
            # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0 
            # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0
            score = player1_score
        else:
            # print(player2_blocking)
            # score = abs(player_2_car.x - 13) - player
            # _1_car.x * 0.0
            score = player2_score - player1_score * 0.3
        # if state.turn == Owner.PLAYER1:
        #     # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0 
        #     # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0
        #     score = player1_score
        # else:
        #     # print(player2_blocking)
        #     # score = abs(player_2_car.x - 13) - player_1_car.x * 0.0
        #     score = player2_score


        # flipped_score = -score if state.turn != self.owner else score
        # flipped_score = score

        return score
    
