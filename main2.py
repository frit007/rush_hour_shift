import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from loader import load_maps
from game import new_game
from human_player import HumanPlayer
from random_player import Random
from minimax_player import MinimaxPlayer
from greedy_player import GreedyPlayer
from iterativ_deepening_player import IterativeDeepeningPlayer
from monte_carlo_player import MonteCarloPlayer

def main():
    pygame.init()
    map_options, maps = map(list, zip(*load_maps()))
    players = [HumanPlayer, Random, MinimaxPlayer, 
               IterativeDeepeningPlayer, MonteCarloPlayer, GreedyPlayer]
    new_game(maps[0], players[0], players[0])
    pygame.quit()

if __name__ == "__main__":
    main()
