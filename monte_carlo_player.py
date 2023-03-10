from __future__ import annotations
import time
import random
import math

from state import State
from type import Action, Direction, Owner
from ui import *
from player import Player, AIPlayer
from greedy_player import GreedyPlayer

class Node:
    parent: Node
    children: list[Node] 
    playouts: int
    wins: int
    lead_to: Action
    state: State
    def __init__(self, parent: Node, children: Node, lead_to: Action, state: State) -> None:
        self.parent = parent
        self.playouts = 0
        self.wins = 0
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
            return f"Node: playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} action: {self.lead_to} children: {self.children}\n"
        else: 
            return f"Node: playouts: {self.playouts} depth: {self.depth()} wins: {self.wins} action: {self.lead_to} children: __omitted__\n"
class MonteCarloPlayer(Player):
    name = "Monte Carlo Player"
    owner: Owner

    def play(self, state: State, history: set[State]) -> Action:
        # self.history = history
        self.owner = state.turn
        tree = Node(None, [], None, state)
        return self.monte_carlo_tree_search(tree, 300)

    def monte_carlo_tree_search(self, tree: Node, seconds: int) -> Action:
        start = time.time()
        end = time.time()
        counter = 0
        #while end - start < seconds:
        while counter < 1000:
            leaf = self.select(tree) 
            child = self.expand(leaf)
            result = self.simulate(child)
            self.back_propagate(result, child)
            counter += 1
            end = time.time()
        
        print("loops: " + str(counter))
        print(tree)
        best_child = max(tree.children, key=lambda c: self.heuristic(c.state))
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
            child = Node(node, [], a, node.state.apply_action(a))
            node.addChild(child)

        node.children.sort(key=lambda c: self.heuristic(c.state))
        return node.children[0]

    def simulate(self, node: Node) -> State:
        greedy = GreedyPlayer()
        rand = AIPlayer()
        current_state = node.state
        counter = 0
        while current_state.get_winner() == None:
            counter += 1
            if random.randrange(0,100) > 80:
                action = rand.play(current_state, greedy.history)
            else:
                action = greedy.play(current_state, greedy.history)

            #current_state = self.playout_policy(current_state)
            greedy.history.add(current_state)
            current_state = current_state.apply_action(action)

        print("playout moves: " + str(counter))
        return Owner.PLAYER2 if current_state.turn == Owner.PLAYER1 else Owner.PLAYER1 # this is the winner right?

    def back_propagate(self, winner: Owner, node: Node) -> State:
        while True:
            node.playouts += 1
            if node.state.turn == winner:
                node.wins += 1

            if node.parent != None:
                node = node.parent
            else:
                break

    def playout_policy(self, state: State) -> State:
        pass
        # greedy.history.add(state)
        # action = greedy.play(state, greedy.history)
        # return state.apply_action(action)

        # values = []
        # actions = state.get_legal_actions()

        # for a in actions:
        #     values.append(self.heuristic(state.apply_action(a)))
        
        # rand = random.randint(0, sum(values))
        # # print(values)

        # for i in range(len(values)):
        #     rand -= values[i]
        #     if rand <= 0:
        #         # print(f"Select index {i}")
        #         return state.apply_action(actions[i])
    
    
    def heuristic(self, state: State):
        player1_car, player2_car = state.get_player_cars()

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
        
        # total amount of horizontal cars (on connected path) - horizontal cars blocking (on connected path)?

        # player1_blocking = 0
        # for x in range(player1_car.x + 2, 13):
        #     car = state.car_map.get((x, player1_car.y))
        #     if car != None:
        #         if car.direction == Direction.HORIZONTAL:
        #             # avoid horizontal cars on the same row
        #             player1_blocking += 50
        #         player1_blocking += 1
        
        # player2_blocking = 0    
        # for x in range(player2_car.x - 1, 0, -1):
        #     car = state.car_map.get((x, player2_car.y))
        #     if car != None:
        #         if car.direction == Direction.HORIZONTAL:
        #             # avoid horizontal cars on the same row
        #             player2_blocking += 10
        #         player2_blocking += 1

        #player1_score = - player1_blocking - player1_roadblocks + abs(player1_car.x - 0) * 20
        #player2_score = - player2_blocking - player2_roadblocks + abs(player2_car.x - 12) * 20

        # if self.owner == Owner.PLAYER1:
        #     return 20 * (13 - player1_car.x) + player1_roadblocks
        # else:
        #     return 20 * player2_car.x + player2_roadblocks

        if state.turn == Owner.PLAYER1:
            return 20 * player1_car.x #+ 14 - player1_roadblocks
        else:
            return 20 * abs(player2_car.x - 13) #+ 14 - player2_roadblocks
