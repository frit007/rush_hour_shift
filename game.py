import os
os.environ['PYGAME_HIDE_SUPPORT_PROMPT'] = 'hide'
import pygame
from time import sleep
from tkinter import *
from tkinter import ttk

from type import *
from state import *
from player import *
from human_player import HumanPlayer
from minimax_player import MinimaxPlayer
from loader import load_maps
from ui import *

SCREEN_SIZE = (600, 600)
FONT = 'Roboto'

#TODO: Cards based on # https://www.ultraboardgames.com/rush-hour-shift/game-rules.php
cards = [
    Card(4, False, 0),
    Card(3, False, 0),
    Card(0, False, 1),
    Card(0, True, 0),
    Card(2, False, 1)
]

def new_game(root: Tk, initial_state: State, player1: Player, player2: Player):
    root.withdraw()
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
    # running = True
    # # game loop
    # while running:
    #     for event in pygame.event.get():
    #         if event.type == pygame.QUIT:
    #             running = False

    #         if (event.type == pygame.KEYDOWN 
    #             and event.key == pygame.K_ESCAPE):
    #             running = False
    
    pygame.display.quit()
    root.deiconify()

def init_main_screen(root):
    map_options, maps = map(list, zip(*load_maps()))
    players = [HumanPlayer, AIPlayer, MinimaxPlayer]
    player_options = ['Human', 'AI', 'Minimax']

    root.title(NAME)
    root.geometry(f'{SCREEN_SIZE[0]}x{SCREEN_SIZE[1]}')
    root.resizable(False, False)

    style = ttk.Style()
    style.theme_use('clam')
    style.configure('TFrame', background=MAIN_BG_COLOR)
    style.configure('TLabel', background=MAIN_BG_COLOR, foreground=FONT_COLOR)

    content = ttk.Frame(root)
    frame = ttk.Frame(content, padding=10, width=SCREEN_SIZE[0], height=SCREEN_SIZE[1])
    title = ttk.Label(content, text=NAME, font=(FONT + ' Bold', 30))

    map_text = ttk.Label(content, text='Pick a map:', font=(FONT, 20))
    map_drop = ttk.Combobox(content, state='readonly', values=map_options)
    map_drop.current(0)

    player_text = ttk.Label(content, text='Select Players:', font=(FONT, 20))
    player1_text = ttk.Label(content, text='Player 1:', font=(FONT, 20))
    player1_drop = ttk.Combobox(content, state='readonly', values=player_options)
    player1_drop.current(0)

    player2_text = ttk.Label(content, text='Player 2:', font=(FONT, 20))
    player2_drop = ttk.Combobox(content, state='readonly', values=player_options)
    player2_drop.current(0)

    start_btn = ttk.Button(content, text='Start', command=lambda: new_game(root, 
                                                                           maps[map_drop.current()], 
                                                                           players[player1_drop.current()](), 
                                                                           players[player2_drop.current()]()))
    quit_btn = ttk.Button(content, text='Quit', command=root.destroy)

    content.grid(column=0, row=0)
    frame.grid(column=0, row=0, columnspan=8, rowspan=16)
    title.grid(column=0, row=0, columnspan=8, rowspan=6)
    map_text.grid(column=2, row=6, columnspan=2)
    map_drop.grid(column=4, row=6, columnspan=2)
    player_text.grid(column=0, row=8, columnspan=8)
    player1_text.grid(column=1, row=9, columnspan=2)
    player2_text.grid(column=5, row=9, columnspan=2)
    player1_drop.grid(column=1, row=10, columnspan=2)
    player2_drop.grid(column=5, row=10, columnspan=2)
    quit_btn.grid(column=2, row=13, columnspan=2)
    start_btn.grid(column=4, row=13, columnspan=2)

def main():
    pygame.init()
    root = Tk()
    init_main_screen(root)
    root.mainloop()
    pygame.quit()

if __name__ == "__main__":
    main()

# Optimizing for minimal state size(We are going to have a lot of states, this is probably required if we do A* or similar)
# 
# # Attributes store everything that doesn't change between states
# CarAttributes = {"image": Image, carLength: int, "direction": VERTICAL/HORIZONTAL, "owner": PLAYER1/PLAYER2/NEUTRAL}
# fromY and toY don't include the yOffset
# RoadAttributes = {"fromX": int, "toX": int, "fromY": int, "toY": int}
#
# Card: {
#   "move": int, 
#   "isSlideX": bool, # move a car x fields forwards
#   "moveRoads":int # How many roads can they move
# }
# cards: card[]
#
# 
# state = {
#     # Cars could be sorted by x, that way we only have to search part of the cars array to check collisions. This would let us binary search for all cars on a road.
#     # Since we only need to reorder the array when positions are shifted, sorting should be fast, since we likely only need 2-4 swaps until the array is sorted again
#     # This optimization might not be necessary since the array size is max ~15-20
#     "cars": {"x":int, "y": int, "car":CarAttributes}[],
#     "roads": {"yOffset": int, "road": RoadAttributes}[],
#     "turn": PLAYER1/PLAYER2,
#     # each index refers to a card in the cards array
#     # we could store it this way to minimize state size
#     "cards": int[]
# }
#
#
#
# 
# If we use DFS, we have more flexibility to use more memory to allow faster movement checks
# This is because we rarely copy a state, instead, we move or undo moves.
#
# Road = {"fromX": int, "toX": int, "fromY": int, "toY": int, "yOffset": int}
# Cars = {"image": Image, carLength: int, "direction": VERTICAL/HORIZONTAL, "owner": PLAYER1/PLAYER2/NEUTRAL, "positions"=[(x:int,y:int)], road: Road}
# state = {
#   # O(1) lookup for collision checks, but moving a car, requires updating 
#   "fields":Dictionary<(int, int), Car>
#   "cars": Dictionary<int, Car>
#   "roads": List<road>
#   "turn": PLAYER1/PLAYER2
# }
