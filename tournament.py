import json
import os
import sys
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

from heuristics.heuristic_b import heuristic_b


from dataclasses import asdict, dataclass
import time
from logic.loader import load_maps
from logic.type import Owner
from players.human_player import HumanPlayer
from players.player import Player
from players.random_player import Random
from players.minimax_player import MinimaxPlayer
from players.greedy_player import GreedyPlayer
from players.iterative_deepening_player import IterativeDeepeningPlayer
from players.iterative_deepening_with_history import IterativeDeepeningPlayerWithHistory
from players.beam_player import BeamPlayer
from players.monte_carlo_player import MonteCarloPlayer
from players.monte_carlo_player_processed import MonteCarloPlayerProcessed
from players.pool_monte_carlo import PoolMonteCarloPlayer


def replace_heuristic(algo, heuristic):
    algo.name += " Heuristic B"
    # algo.heuristic = lambda state, optimize_for=None: heuristic(algo, state, optimize_for)
    algo.use_heuristic = heuristic
    return algo

def set_time_limit(algo, seconds):
    algo.seconds = seconds
    algo.name += f" time limit {seconds}"
    return algo


contenders = [
    Random(), # 0
    MinimaxPlayer(), # 1
    IterativeDeepeningPlayer(), # 2
    IterativeDeepeningPlayerWithHistory(), # 3
    GreedyPlayer(), # 4
    MonteCarloPlayer(), # 5
    MonteCarloPlayerProcessed(), # 6
    replace_heuristic(MonteCarloPlayerProcessed(), heuristic_b), # 7
    PoolMonteCarloPlayer() # 8
]
# contenders = [Random(), GreedyPlayer(),MonteCarloPlayerProcessed(),IterativeDeepeningPlayer()]

# contenders = [
#     # set_time_limit(replace_heuristic(MonteCarloPlayerProcessed(), heuristic_b), 1), 
#     set_time_limit(MonteCarloPlayerProcessed(), 1),
#     set_time_limit(MonteCarloPlayer(), 1),
#     set_time_limit(PoolMonteCarloPlayer(), 1),
#     # set_time_limit(replace_heuristic(MonteCarloPlayerProcessed(), heuristic_b), 2), 
#     # set_time_limit(MonteCarloPlayerProcessed(), 2),
#     ]

def blockPrint():
    sys.stdout = open(os.devnull, 'w')

def enablePrint():
    sys.stdout = sys.__stdout__

@dataclass(frozen=True, slots=True)
class Result:
    player1: str
    player2: str
    result: int
    moves: int
    time: float

results : list[Result] = []

map_options, maps = map(list, zip(*load_maps()))
map = maps[0]

move_limit = 1000
time_limit = 60*60*1 # 1 hour time limit

def findMatch(a, b):
    player1 = contenders[a]
    player2 = contenders[b]
    for result in results:
        if result["player1"] == player1.name and result["player2"] == player2.name:
            return result

def result_to_latex(results):
    cs = "|c|"
    for i in range(len(contenders) ):
        cs += "c|"

    latex = "\\begin{center} \\begin{tabular}{" + cs + "}\\hline\n"


    first_row = ""

    for column in range(len(contenders)):
        first_row += "&"+str(column + 1)

    latex+= first_row + "\\\\\hline\n"

    symbol = {0:"0", 1: "-", 2: "+"}
    index = 0
    for row in range(len(contenders)):
        latex += str(row + 1)
        for column in range(len(contenders)):
            match = findMatch(row, column)
            if match == None:
                # Match against themselves
                latex +=  "&0"
            else:
                if row == 5:
                    print(match)
                # latex += "&" + symbol[results[index]["result"]]
                latex += "&" + symbol[match["result"]]
                index += 1
        latex += "\\\\\hline\n"

    latex += "\\end{tabular}\\end{center}"
    latex += "\n\n"
    latex += "\\begin{enumerate}\n"
    for player in contenders:
        latex += f"\t \item {player.name}\n"
    latex += "\\end{enumerate}\n"
    return latex


def main():
    for player1 in contenders:
        for player2 in contenders:
            if player1 == player2:
                continue
            players = [player1, player2]
            turn = 0
            current_state = map.initial_state
            history = set()
            moves = 0
            start = time.time()
            end = start
            print(" ")
            print(" ")
            print(f"{player1.name} vs {player2.name}")
            
            filename = f"tournament_{player1.name}_vs_{player2.name}.json"
            if os.path.isfile(filename):
                in_file = open(filename, "r")
                result = json.load(in_file)
                results.append(result)
                in_file.close()
                print("skip")
                continue

            while current_state.get_winner(map) == None and not(end - start > time_limit) and moves < move_limit:
                blockPrint()
                action = players[turn].play(current_state, map, history)
                enablePrint()
                history.add(current_state)
                current_state = current_state.apply_action(action)
                turn = (turn + 1) % 2 # switch players
                moves += 1
                end = time.time()
                print(".", end="",flush=True)

            print("")
            time_used = end - start
            print(f"used {moves} moves and {time_used} seconds")
            result = None
            if current_state.get_winner(map) == Owner.PLAYER1:
                print(f"Player 1 won in {moves} moves")
                result = Result(player1.name, player2.name, 1, moves, time_used)
            elif current_state.get_winner(map) == Owner.PLAYER2:
                print(f"Player 2 won in {moves} moves")
                result = Result(player1.name, player2.name, 2, moves, time_used)
            else:
                print(f"Draw")
                result = Result(player1.name, player2.name, 0, moves, time_used)
            results.append(asdict(result))
            out_file = open(filename, "w")
            
            json.dump(asdict(result), out_file, indent = 4)
            
            out_file.close()

    out_file = open(f"tournament.json", "w")
    
    json.dump(results, out_file, indent = 4)
    
    out_file.close()

    print(result_to_latex(results))

if __name__ == "__main__":
    main()
