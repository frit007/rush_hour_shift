import os

os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame

from loader import load_maps
from ui.menu import *
from players.human_player import HumanPlayer
from players.random_player import Random
from players.minimax_player import MinimaxPlayer
from players.greedy_player import GreedyPlayer
from players.iterative_deepening_player import IterativeDeepeningPlayer
from players.iterative_deepening_with_history import IterativeDeepeningPlayerWithHistory
from players.beam_player import BeamPlayer
from players.monte_carlo_player import MonteCarloPlayer

def main():
    pygame.init()
    root = Tk()
    game_maps = load_maps()
    players = [HumanPlayer, Random, MinimaxPlayer, BeamPlayer,
               IterativeDeepeningPlayer, IterativeDeepeningPlayerWithHistory,
               MonteCarloPlayer, GreedyPlayer]
    init_main_screen(root, game_maps, players)
    root.mainloop()
    pygame.quit()

if __name__ == "__main__":
    main()
