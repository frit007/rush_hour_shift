import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from time import sleep

from type import *
from state import *
from player import *
from human_player import HumanPlayer
from minimax_player import MinimaxPlayer
from greedy_player import GreedyPlayer
from iterativ_deepening_player import IterativeDeepeningPlayer
from monte_carlo_player import MonteCarloPlayer
from loader import load_maps
from ui import *

SCREEN_SIZE = (600, 600)
FONT = 'Roboto'

def new_game(initial_state: State, player1: Player, player2: Player):
    create_window()
    players = [player1, player2]
    turn = 0

    current_state = initial_state

    history = set()

    while current_state.get_winner() == None:
        action = players[turn].play(current_state, history)
        history.add(current_state)
        current_state = current_state.apply_action(action)
        turn = (turn + 1) % 2 # switch players
        draw_state(current_state)
        pygame.display.flip()
        sleep(0.4)

    
    if(current_state.get_winner() == Owner.PLAYER1):
        print("Player 1 won")
    else:
        print("Player 2 won")
    pygame.display.quit()

def main():
    pygame.init()
    map_options, maps = map(list, zip(*load_maps()))
    players = [HumanPlayer, AIPlayer, MinimaxPlayer, IterativeDeepeningPlayer, MonteCarloPlayer, GreedyPlayer]
    new_game(maps[0], players[0](), players[3]())
    pygame.quit()

if __name__ == "__main__":
    main()
