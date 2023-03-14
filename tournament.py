import json
import os, sys

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'

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
# contenders = [Random(), MinimaxPlayer(),
#                IterativeDeepeningPlayer(), IterativeDeepeningPlayerWithHistory(),
#                MonteCarloPlayer(), MonteCarloPlayerProcessed(), GreedyPlayer(), PoolMonteCarloPlayer()]
contenders = [Random(), GreedyPlayer(),MonteCarloPlayerProcessed(),IterativeDeepeningPlayer()]

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
time_limit = 60*30 # 30 minute time limit


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
            print(f"{player1.name} vs {player2.name}")
            
            filename = f"tournament_{player1.name}_vs_{player2.name}.json"
            if os.path.isfile(filename):
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

if __name__ == "__main__":
    main()
