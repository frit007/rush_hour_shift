import random
import time
import pygame

from state import CarState, RoadState, State
from type import Action, Owner
from ui import *

class Player:
    name: str
    def play(self, state, history: set[State]):
        pass

class AIPlayer(Player):
    name = "Random player"
    # random AI(currently cheats by moving your car)
    def play(self, state: State, history: set[State]):
        shifts = state.all_shifts()
        shift = None
        if len(shifts) > 0:
            shift = random.choice(state.all_shifts())
        
        state = state.apply_action(Action(shift, []))
        move_limit = 3
        played_moves = []
        while move_limit > 0:
            car = random.choice(state.cars)
            moves = state.car_moves(car, move_limit)
            if len(moves) > 0:
                move = random.choice(moves)
                if (move.car.owner == Owner.NEUTRAL) or move.car.owner == state.turn:
                    move_limit -= move.magnitude()
                    state = state.apply_action(Action(None, [move]))
                    played_moves.append(move)
                
        return Action(shift, played_moves)
    
    def heuristic():
        # Heuristic should probably be moved to ai player, since each AI is free to choose their own heuristic
        # Calculate a heuristic for this field, this could include
        # - distance of to the goal
        # - cars blocking the cars
        pass
    