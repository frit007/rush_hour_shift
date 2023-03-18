import os
import time
import concurrent.futures

from logic.state import State
from logic.type import Action, Owner
from players.monte_carlo_player import *

class PoolMonteCarloPlayer(MonteCarloPlayer):
    name = "Pool Monte Carlo Player"
    owner: Owner
    map: Map
    max_processes: int

    def __init__(self) -> None:
        super().__init__()
        self.max_processes = os.cpu_count()

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = Map(map.map_id, map.initial_state, map.player1_goal, 
                       map.player2_goal, map.potential_roadblocks, [])
        tree = Node(None, [], state)
        return self.monte_carlo_tree_search(tree)

    def monte_carlo_tree_search(self, tree: Node) -> Action:
        start = time.time()
        end = time.time()
        counter = 0
        with concurrent.futures.ProcessPoolExecutor() as executor:
            while end - start < self.seconds:
                leafs = self.select_initial(tree)
                children = list(map(self.expand, leafs))
                children_states = map(lambda c: c.state, children)
                for child, result in zip(children, executor.map(self.simulate, children_states)):
                    if child.won_in_path:
                        self.back_propagate(child.won_in_path, child)
                    else:
                        self.back_propagate(result, child)
                counter += 1
                end = time.time()

        #print(tree)
        best_child = max(tree.children, key=lambda c: c.playouts)
        return best_child.state.lead_to

    def select_initial(self, node: Node) -> list[Node]:
        if node.isLeaf():
            return [node]
        else:
            selections = []
            for child in node.children:
                selections.append((self.UCB1(child), child))

            selections.sort(key=lambda c: c[0], reverse=True)
            scores, children = zip(*selections[0:self.max_processes])
            return list(map(self.select, list(children)))
