from __future__ import annotations
import time
import concurrent.futures
import os

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
        self.map = Map(map.map_id, map.initial_state, map.player1_goal, map.player2_goal, map.potential_roadblocks, [])
        tree = Node(None, [], None, state)
        return self.monte_carlo_tree_search(tree, 300)

    def monte_carlo_tree_search(self, tree: Node, seconds: int) -> Action:
        start = time.time()
        end = time.time()
        counter = 0
        with concurrent.futures.ProcessPoolExecutor() as executor:
            #while end - start < seconds:
            while counter < 1000 / self.max_processes:
                leafs = self.select_initial(tree)
                children = list(map(self.expand, leafs))
                for child, result in zip(children, executor.map(self.simulate, children)):
                    self.back_propagate(result, child)

                #print(tree, flush=True)
                counter += 1
                end = time.time()

        print(tree)
        best_child = max(tree.children, key=lambda c: c.playouts)
        return best_child.lead_to

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
