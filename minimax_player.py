from state import State
from type import Action
from ui import *
from player import Player

DEPTH_LIMIT = 5
class MinimaxPlayer(Player):
    name = "MinMax Player"
    # TODO: Add depth to transpositions, since it is important at which depth a state was analyzed
    transpositions: dict[State, (float, Action, int)]
    history: set[State]
    owner: Owner

    def __init__(self) -> None:
        super().__init__()
        self.transpositions = {}

    def play(self, state: State, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
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

    def heuristic(self, state:State):
        player1_car, player2_car = state.get_player_cars()

        player1_score = player1_car.x

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
                player1_blocking += 1
            
        for x in range(player2_car.x - 1, 0, -1):
            car = state.car_map.get((x, player2_car.y))
            if car != None:
                player2_blocking += 1

        player1_score = - player1_blocking - player1_roadblocks + abs(player1_car.x - 0) * 20
        player2_score = - player2_blocking - player2_roadblocks + abs(player2_car.x - 13) * 20

        if self.owner == Owner.PLAYER1:
            # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0 
            # score = player_1_car.x - abs(player_2_car.x - 13) * 0.0
            score = player1_score 
        else:
            # print(player2_blocking)
            # score = abs(player_2_car.x - 13) - player_1_car.x * 0.0
            score = player2_score
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
