from state import State
from type import Action
from ui import *
from player import Player

BEAM_WIDTH = 3
MAX_DEPTH = 5


class BeamPlayer(Player):
    name = "Beam Search"
    owner: Owner

    def __init__(self) -> None:
        super().__init__()

    def play(self, state: State, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn

        move = self.beam_search(state, BEAM_WIDTH, MAX_DEPTH)
        return move

    def beam_search(self, state: State, beam_width: int, max_depth: int) -> Action:

        sort_number = 0
        queue = [(self.heuristic(state), sort_number, state, [])]
        num_expanded = 0

        for depth in range(max_depth):
            new_queue = []
            for i in range(min(len(queue), beam_width)):
                current_heuristic, sort_number, current_state, current_actions = queue[i]
                for action in current_state.get_legal_actions():
                    next_state = current_state.apply_action(action)
                    next_actions = current_actions + [action]
                    new_queue.append((next_state, next_actions))
            queue = []
            for next_state, next_actions in new_queue:
                queue.append((self.heuristic(next_state), sort_number,
                             next_state, next_actions))
                sort_number += 1
                queue.sort(reverse=True)
            num_expanded += len(new_queue)
            if queue[0][2].get_winner() != None:
                return queue[0][3][0]

        print(queue[0][3], num_expanded)
        return queue[0][3][0]

    # TODO: work on heuristic
    def heuristic(self, state: State):
        player1_car, player2_car = state.get_player_cars()

        score = 0
        player1_blocking = 0
        player2_blocking = 0

        # Include road
        player1_roadblocks = 0
        for road in state.roads:
            if (not (player1_car.y >= road.from_y()
                and player1_car.y <= road.to_y())
                    and player1_car.x <= road.from_x()):

                player1_roadblocks += road.to_x() - road.from_x() + 1

        player2_roadblocks = 0
        for road in state.roads:
            if (not (player2_car.y >= road.from_y()
                and player2_car.y <= road.to_y())
                    and player2_car.x >= road.to_x()):

                player2_roadblocks += road.to_x() - road.from_x() + 1

        for x in range(player1_car.x + 2, 13):
            car = state.car_map.get((x, player1_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player1_blocking += 10
                player1_blocking += 1

        for x in range(player2_car.x - 1, 0, -1):
            car = state.car_map.get((x, player2_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player2_blocking += 10
                player2_blocking += 1

        player1_score = - player1_blocking - \
            player1_roadblocks + abs(player1_car.x - 0)
        player2_score = - player2_blocking - \
            player2_roadblocks + abs(player2_car.x - 12)

        if self.owner == Owner.PLAYER1:
            score = player1_score
        else:
            score = player2_score - player1_score * 0.2

        return score
