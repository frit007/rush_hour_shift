import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from time import sleep

from logic.type import *
from logic.state import *
from ui.game import *
from players.player import *

def new_game(map: Map, player1: Player, player2: Player):
    create_window()
    players = [player1, player2]
    turn = 0
    current_state = map.initial_state
    history = set()
    moves = 0
    draw_state(current_state)
    pygame.display.flip()
    pygame.event.get()

    while current_state.get_winner(map) == None:
        action = players[turn].play(current_state, map, history)
        history.add(current_state)
        current_state = current_state.apply_action(action)
        turn = (turn + 1) % 2 # switch players
        draw_state(current_state)
        pygame.display.flip()
        pygame.event.get()
        moves += 1
        sleep(0.4)
    
    if(current_state.get_winner(map) == Owner.PLAYER1):
        print(f"Player 1 won in {moves} moves")
    else:
        print(f"Player 2 won in {moves} moves")
    
    pygame.display.quit()
