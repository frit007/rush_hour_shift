from logic.state import State
from logic.type import Action
from players.player import *
    
class GreedyPlayer(Player):
    name = "Greedy Player"
    map: Map

    def __init__(self) -> None:
        super().__init__()
        self.history = set()

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.map = map
        self.owner = state.turn

        actions = state.get_legal_actions()
        scored_actions = []
        i = 0
        for action in actions:
            next_state = state.apply_action(action)
            heuristic = self.heuristic(next_state)
            scored_actions.append((heuristic, i, action))
            i += 1
        scored_actions.sort(reverse=True)

        return scored_actions[0][2]
