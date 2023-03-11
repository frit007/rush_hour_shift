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
    lead_to: Action
    state: State
    def __init__(self, parent: Node, children: Node, lead_to: Action, state: State) -> None:
        self.parent = parent
        self.playouts = 0
        self.wins = 0
        self.our_wins = 0
        self.children = children
        self.lead_to = lead_to
        self.state = state
        
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
            return f"Node: player: {self.state.turn} playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} our_wins {self.our_wins} action: {self.lead_to} children: {self.children}\n"
        else:
            return f"Node: player: {self.state.turn} playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} our_wins {self.our_wins} action: {self.lead_to} children: __omitted__\n"

class MonteCarloPlayer(Player):
    name = "Monte Carlo Player"
    owner: Owner
    map: Map

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map
        tree = Node(None, [], None, state)
        return self.monte_carlo_tree_search(tree, 300)

    def monte_carlo_tree_search(self, tree: Node, seconds: int) -> Action:
        start = time.time()
        end = time.time()
        counter = 0
        #while end - start < seconds:
        while counter < 1000:
            print(f"({counter}) ",end="")
            leaf = self.select(tree) 
            child = self.expand(leaf)
            result = self.simulate(child)
            self.back_propagate(result, child)
            counter += 1
            end = time.time()

        print("loops: " + str(counter))
        print(tree)
        best_child = max(tree.children, key=lambda c: c.playouts)
        return best_child.lead_to

    def UCB1(self, node: Node) -> Node:
        if node.playouts == 0:
            return math.inf
        else:
            exploit = node.wins / node.playouts
            explore = math.sqrt(math.log(node.parent.playouts) / node.playouts)
            C = math.sqrt(2) # Test with other values
            return exploit + C * explore

    def select(self, node: Node):
        if node.isLeaf():
            return node
        else:
            max = None, -math.inf
            for child in node.children:
                selection_policy = self.UCB1(child)
                if selection_policy > max[1]:
                    max = child, selection_policy
            
            return self.select(max[0])

    def expand(self, node: Node):
        if node.playouts == 0 and node.parent != None:
            return node
        
        for a in node.state.get_legal_actions():
            new_state = node.state.apply_action(a)
            if new_state not in self.history:
                child = Node(node, [], a, new_state)
                node.addChild(child)

        node.children.sort(key=lambda c: self.heuristic(c.state, self.owner), reverse = True)
        return node.children[0]

    def simulate(self, node: Node) -> State:
        # greedy = GreedyPlayer()
        # rand = AIPlayer()
        current_state = node.state
        counter = 0
        # history = self.history.copy()
    
        while current_state.get_winner(self.map) == None:
            counter += 1
            # if random.randrange(0,100) > 80:
            #     action = rand.play(current_state, greedy.history)
            # else:
            #     action = greedy.play(current_state, greedy.history)
            current_state = self.playout_policy(current_state, counter)
            # history.add(current_state)
            # greedy.history.add(current_state)
            # current_state = current_state.apply_action(action)

        print("playout moves: " + str(counter), flush=True)
        return current_state.get_winner(self.map)

    def back_propagate(self, winner: Owner, node: Node) -> State:
        while True:
            node.playouts += 1
            # if node.state.turn == winner:
            #     node.wins += 1
            if node.state.turn != winner:
                node.wins += 1
            if self.owner == winner:
                node.our_wins += 1

            if node.parent != None:
                node = node.parent
            else:
                break

    def playout_policy(self, state: State, iteration:int) -> State:
        # pass
        # greedy.history.add(state)
        # action = greedy.play(state, greedy.history)
        # return state.apply_action(action)

        values = []
        actions = state.get_legal_actions()
        allowed_actions = []
        for a in actions:
            next_state = state.apply_action(a)
            if not next_state.is_draw():
                allowed_actions.append(a)
                h = self.heuristic(next_state, state.turn)
                values.append(h)
        
        minVal = min(values)
        values = [x - minVal + 1 for x in values]
        if iteration < 300:
            values = [pow(x, 7) for x in values]
        else:
            values = [pow(x, 1) for x in values]

        rand = random.randint(0, sum(values))
        # print(values)

        for i in range(len(values)):
            rand -= values[i]
            if rand <= 0:
                # print(f"Select index {i}")
                return state.apply_action(allowed_actions[i])
