from __future__ import annotations
import time
import random
import math
from logic.loader import load_maps

from logic.state import State, reconstruct_from_minimal_state_and_map
from logic.type import Action, Owner
from players.player import *
from multiprocessing import Process, Pipe, Queue, cpu_count

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

class MonteCarloPlayerProcessed(Player):
    name = "Monte Carlo Player Processed"
    owner: Owner
    map: Map
    def __init__(self) -> None:
        super().__init__()
        self.job_id = 0

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = map
        tree = Node(None, [], None, state)
        work_queue = Queue()
        results_queue = Queue()
        # print(f"threads {cpu_count()}")
        processes:list[Process] = []
        for i in range(cpu_count()):
            process = Process(target = monte_carlo_tree_worker, args=[self.owner, self.map.map_id, work_queue, results_queue])
            process.start()
            processes.append(process)

        move = self.monte_carlo_tree_manager(tree, work_queue, results_queue)

        for p in processes:
            work_queue.put_nowait("stop")
            # p.terminate()
            # p.close()
        
        # for p in processes:
            # p.close()

        return move

    def monte_carlo_tree_manager(self, tree: Node, work: Queue, results: Queue) -> Action:
        start = time.time()
        end = time.time()
        jobs = {}
        limit = self.job_id + 5000
        while not results.empty():
            # Remove backlog
            results.get()

        def assignWork():
            leaf = self.select(tree) 
            child = self.expand(leaf)
            self.back_propagate(None, child, True, False)
            work.put_nowait((self.job_id, child.state.minimized_state()))
            jobs[self.job_id] = child
            self.job_id += 1

        def receiveWork():
            (job_id, winner) = results.get()
            child = jobs[job_id]
            if child is not None:
                self.back_propagate(winner, child, False, True)

        for i in range(cpu_count()):
            assignWork()

        seconds = 30

        while end - start < seconds:
        # while self.job_id < limit:
            receiveWork()
            # print("receive")
            assignWork()
            # print("assign")
            end = time.time()



        print("loops: " + str(self.job_id))
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

    def simulate(self, state: State) -> Owner:
        # greedy = GreedyPlayer()
        # rand = AIPlayer()
        current_state = state
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

    def back_propagate(self, winner: Owner, node: Node, affect_playout: bool, affect_wins: bool) -> None:
        while True:
            if affect_playout:
                node.playouts += 1
            # if node.state.turn == winner:
            #     node.wins += 1
            if affect_wins:
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

def monte_carlo_tree_worker(owner:Owner, map_id: int, work: Queue, results: Queue) -> Action:
    maps = load_maps()
    map = None
    for m in maps:
        if m[1].map_id == map_id:
            map = m[1]
            break
    player = MonteCarloPlayerProcessed()
    player.owner = owner
    player.map = map
    while True:
        # job (id, tuple)
        job = work.get()
        # print(f"job {job}" )
        if job == "stop":
            exit()
        minimized_state = job[1]
        state = reconstruct_from_minimal_state_and_map(map, minimized_state)
        result = player.simulate(state)
        results.put_nowait((job[0], result) )