from ui import *
from loader import load_maps
from monte_carlo_player import MonteCarloPlayer
from iterativ_deepening_player import IterativeDeepeningPlayer
from greedy_player import GreedyPlayer
from minimax_player import MinimaxPlayer
from beam_player import BeamPlayer
from human_player import HumanPlayer
from player import *
from state import *
from type import *
from time import sleep
import pygame
import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'


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
        turn = (turn + 1) % 2  # switch players
        draw_state(current_state)
        pygame.display.flip()
        sleep(0.4)

    if (current_state.get_winner() == Owner.PLAYER1):
        print("Player 1 won")
    else:
        print("Player 2 won")
    pygame.display.quit()


def main():
    pygame.init()
    map_options, maps = map(list, zip(*load_maps()))
    players = [HumanPlayer, AIPlayer, MinimaxPlayer,
               IterativeDeepeningPlayer, MonteCarloPlayer, GreedyPlayer,
               BeamPlayer]
    new_game(maps[0], players[0](), players[6]())
    pygame.quit()


if __name__ == "__main__":
    main()
