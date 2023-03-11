from tkinter import *
from tkinter import ttk

from player import *
from state import State, Map
from ui import NAME, SCREEN_SIZE, MAIN_BG_COLOR, FONT_COLOR, FONT
from game import new_game

def main_game(root: Tk, initial_state: State, player1: Player, player2: Player):
    root.withdraw()
    new_game(initial_state, player1, player2)
    root.deiconify()

def init_main_screen(root: Tk, game_maps: list[tuple[str, Map]], players: list[Player]):
    map_options, maps = map(list, zip(*game_maps))
    player_options = [player.name for player in players]

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

    start_btn = ttk.Button(content, text='Start', command=lambda: main_game(root, 
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
