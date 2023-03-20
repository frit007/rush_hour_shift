from __future__ import annotations
import time

from logic.type import Action, Owner
from players.monte_carlo_player import *
from multiprocessing import Process, Queue, cpu_count

class MonteCarloPlayerProcessed(MonteCarloPlayer):
    name = "Monte Carlo Player Processed"
    owner: Owner
    map: Map


    def __init__(self) -> None:
        super().__init__()
        self.job_id = 0

    def play(self, state: State, map: Map, history: set[State]) -> Action:
        self.history = history
        self.owner = state.turn
        self.map = Map(map.map_id, map.initial_state, map.player1_goal, 
                       map.player2_goal, map.potential_roadblocks, [])
        tree = Node(None, [], state)
        work_queue = Queue()
        results_queue = Queue()
        # print(f"threads {cpu_count()}")
        processes:list[Process] = []
        for i in range(cpu_count()):
            process = Process(target = monte_carlo_tree_worker, args=[self, work_queue, results_queue])
            process.start()
            processes.append(process)

        move = self.monte_carlo_tree_manager(tree, work_queue, results_queue)

        for p in processes:
            work_queue.put_nowait("stop")

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
            if child.won_in_path:
                self.back_propagate(child.won_in_path, child, False, True)
                return True
            work.put_nowait((self.job_id, child.state))
            jobs[self.job_id] = child
            self.job_id += 1
            return False

        def receiveWork():
            (job_id, winner) = results.get()
            child = jobs[job_id]
            if child is not None:
                self.back_propagate(winner, child, False, True)

        for i in range(cpu_count()):
            assignWork()

        while end - start < self.seconds:
        # while self.job_id < limit:
            receiveWork()
            # print("receive")
            while assignWork():
                # Keep trying to assign work
                pass
            
            # print("assign")
            end = time.time()

        #print("loops: " + str(self.job_id))
        #print(tree)
        best_child = max(tree.children, key=lambda c: c.playouts)
        return best_child.state.lead_to

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

    def simulate(self, current_state: State) -> Owner:
        counter = 0
        while current_state.get_winner(self.map) == None:
            counter += 1
            current_state = self.playout_policy(current_state, counter)
        return current_state.get_winner(self.map)
def monte_carlo_tree_worker(player: MonteCarloPlayerProcessed, work: Queue, results: Queue) -> Action:
    # maps = load_maps()
    # map = None
    # for m in maps:
    #     if m[1].map_id == map_id:
    #         map = m[1]
    #         break
    # player = MonteCarloPlayerProcessed()
    # player.owner = owner
    # player.map = map
    while True:
        # job (id, tuple)
        job = work.get()
        # print(f"job {job}" )
        if job == "stop":
            exit()
        state = job[1]
        result = player.simulate(state)
        results.put_nowait((job[0], result) )

# def monte_carlo_tree_worker(owner:Owner, map_id: int, work: Queue, results: Queue) -> Action:
#     maps = load_maps()
#     map = None
#     for m in maps:
#         if m[1].map_id == map_id:
#             map = m[1]
#             break
#     player = MonteCarloPlayerProcessed()
#     player.owner = owner
#     player.map = map
#     while True:
#         # job (id, tuple)
#         job = work.get()
#         # print(f"job {job}" )
#         if job == "stop":
#             exit()
#         state = job[1]
#         result = player.simulate(state)
#         results.put_nowait((job[0], result) )
