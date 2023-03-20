from __future__ import annotations
import time
import random
import math

from logic.state import State
from logic.type import Action, Owner
from players.player import *

class Node:
    parent: Node
    children: list[Node] 
    playouts: int
    wins: int
    our_wins: int
    state: State
    seconds = 30
    def __init__(self, parent: Node, children: Node, state: State) -> None:
        self.parent = parent
        self.playouts = 0
        self.wins = 0
        self.our_wins = 0
        self.children = children
        self.state = state
        self.won_in_path = None
        
    def addChild(self, child: Node) -> None:
        self.children.append(child)

    def isLeaf(self) -> bool:
        return len(self.children) == 0
    
    def depth(self) -> int:
        depth = 0
        parent = self.parent
        while parent != None:
            depth += 1
            parent = parent.parent
        return depth     

    def __repr__(self):
        if(self.depth() < 2): 
            return f"Node: player: {self.state.turn} playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} our_wins {self.our_wins} action: {self.state.lead_to} children: {self.children}\n"
        else:
            return f"Node: player: {self.state.turn} playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} our_wins {self.our_wins} action: {self.state.lead_to} children: __omitted__\n"

class MonteCarloPlayer(Player):
    name = "Monte Carlo Player"
    owner: Owner
    map: Map
    seconds = 20

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map
        tree = Node(None, [], state)
        return self.monte_carlo_tree_search(tree)

    def monte_carlo_tree_search(self, tree: Node) -> Action:
        start = time.time()
        end = time.time()
        counter = 0

        while end - start < self.seconds:
            leaf = self.select(tree) 
            child = self.expand(leaf)
            
            if child.won_in_path:
                self.back_propagate(child.won_in_path, child)
            else:
                result = self.simulate(child.state)
                self.back_propagate(result, child)
            counter += 1
            end = time.time()

        best_child = max(tree.children, key=lambda c: c.playouts)
        return best_child.state.lead_to

    def UCB1(self, node: Node) -> Node:
        if node.playouts == 0:
            return math.inf
        else:
            exploit = node.wins / node.playouts
            explore = math.sqrt(math.log(node.parent.playouts) / node.playouts)
            C = math.sqrt(2) # Test with other values
            return exploit + C * explore

    def select(self, node: Node) -> Node:
        if node.isLeaf():
            return node
        else:
            max = None, -math.inf
            for child in node.children:
                selection_policy = self.UCB1(child)
                if selection_policy > max[1]:
                    max = child, selection_policy
            
            return self.select(max[0])

    def expand(self, node: Node) -> Node:
        if node.playouts == 0 and node.parent != None:
            return node
        
        for a in node.state.get_legal_actions():
            new_state = node.state.apply_action(a)
            if new_state not in self.history:
                child = Node(node, [], new_state)
                child.won_in_path = node.won_in_path
                if not child.won_in_path and new_state.get_winner(self.map) != None:
                    child.won_in_path = new_state.get_winner(self.map)
                node.addChild(child)

        node.children.sort(key=lambda c: self.heuristic(c.state, self.owner), reverse = True)
        return node.children[0]

    def simulate(self, current_state: State) -> Owner:
        counter = 0
        while current_state.get_winner(self.map) == None:
            counter += 1
            current_state = self.playout_policy(current_state, counter)
        return current_state.get_winner(self.map)

    def back_propagate(self, winner: Owner, node: Node) -> None:
        while True:
            node.playouts += 1

            if node.state.turn != winner:
                node.wins += 1
            if self.owner == winner:
                node.our_wins += 1

            if node.parent != None:
                node = node.parent
            else:
                break

    def playout_policy(self, state: State, iteration:int) -> State:
        values = []
        actions = state.get_legal_actions()
        for a in actions:
            next_state = state.apply_action(a)
            h = self.heuristic(next_state, state.turn)
            values.append(h)
        
        minVal = min(values)
        values = [x - minVal + 1 for x in values]
        if iteration < 300:
            values = [pow(x, 7) for x in values]
        else:
            values = [pow(x, 1) for x in values]

        rand = random.randint(0, sum(values))

        for i in range(len(values)):
            rand -= values[i]
            if rand <= 0:
                return state.apply_action(actions[i])
