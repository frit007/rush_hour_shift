from logic.state import State
from logic.type import Action
from ui.game import *
from players.player import *

BEAM_WIDTH = 3
MAX_DEPTH = 5

class BeamPlayer(Player):
    name = "Beam Search"
    owner: Owner
    map: Map

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map

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
            if queue[0][2].get_winner(self.map) != None:
                return queue[0][3][0]

        print(queue[0][3], num_expanded)
        return queue[0][3][0]

    # TODO: work on heuristic
    # There is an updated default heuristic in player.py (we discovered some off-by-one errors) 
    # you can overwrite it using the function below:
    # def heuristic(self, state: State, optimize_for: Owner = None):
    #     pass
