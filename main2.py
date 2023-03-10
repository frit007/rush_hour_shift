import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from logic.loader import load_maps
from logic.game import new_game
from players.human_player import HumanPlayer
from players.random_player import Random
from players.minimax_player import MinimaxPlayer
from players.greedy_player import GreedyPlayer
from players.iterative_deepening_player import IterativeDeepeningPlayer
from players.iterative_deepening_with_history import IterativeDeepeningPlayerWithHistory
from players.beam_player import BeamPlayer
from players.monte_carlo_player import MonteCarloPlayer
from players.pool_monte_carlo import PoolMonteCarloPlayer

def main():
    pygame.init()
    map_options, maps = map(list, zip(*load_maps()))
    players = [HumanPlayer, Random, MinimaxPlayer, BeamPlayer,
               IterativeDeepeningPlayer, IterativeDeepeningPlayerWithHistory,
               MonteCarloPlayer, GreedyPlayer, PoolMonteCarloPlayer]
    new_game(maps[0], players[8](), players[0]())
    pygame.quit()

if __name__ == "__main__":
    main()
