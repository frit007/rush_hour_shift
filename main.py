import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from loader import load_maps
from main_ui import *
from human_player import HumanPlayer
from random_player import Random
from minimax_player import MinimaxPlayer
from greedy_player import GreedyPlayer
from iterativ_deepening_player import IterativeDeepeningPlayer
from beam_player import BeamPlayer
from monte_carlo_player import MonteCarloPlayer

def main():
    pygame.init()
    root = Tk()
    game_maps = load_maps()
    players = [HumanPlayer, Random, MinimaxPlayer, BeamPlayer,
               IterativeDeepeningPlayer, MonteCarloPlayer, GreedyPlayer]
    init_main_screen(root, game_maps, players)
    root.mainloop()
    pygame.quit()

if __name__ == "__main__":
    main()
