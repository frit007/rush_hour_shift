import pygame
from player import Player

from state import *
from type import Action, Owner
from ui import *

class HumanPlayer(Player):

    selected_road: OverlappingElement
    selected_car: OverlappingElement
    shifts_remaining: int
    moves_remaining: int
    original_state: State
    current_state: State
    current_shift: Shift


    def play(self, state: State) -> Action:

        self.original_state = state
        self.current_state = state
        self.shifts_remaining = 1
        self.moves_remaining = 3
        self.selected_car = None
        self.selected_road = None
        self.action = Action(None, [])
        self.current_shift = None

        while self.moves_remaining > 0:
            if self.selected_car != None:
                self.__move_selected_car()
            elif self.selected_road != None:
                self.__shift_selected_road()
            else:
                self.__select_car_or_road()
        return self.action
    
    def __move_selected_car(self):
        draw_offset = draw_state(self.current_state)
        paint_highlight_rect(self.selected_car.rect, pygame.Color(0,0,255,255))

        # Highlight moves
        # car_state = self.current_state.find_car_state(self.selected_car)
        moves = self.current_state.car_moves(self.selected_car.target, self.moves_remaining)
        move_and_positions = translate_move_to_position(self.selected_car.target, moves)
        draw_car_movement_options(move_and_positions, draw_offset)

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for element in get_overlapping_elements(mouse_x, mouse_y, self.current_state):
                    if element.type == CollisionType.SQUARE:
                       moves = [x.move for x in move_and_positions if x.position == element.grid_pos]
                       if len(moves) > 0:
                           # The player made a legal move
                           self.current_state = self.current_state.apply_action(Action(None, moves))
                           self.moves_remaining -= moves[0].magnitude()
                           # Once you move a car you can no longer move a road
                           self.shifts_remaining = 0
                           # update action so we can update the state once the player has done their turn
                           self.action = Action(self.action.shift, self.action.moves + moves)

                # if they clicked nothing deselect the car
                self.selected_car = None



    def __shift_selected_road(self):
        shifts = self.original_state.all_shifts()
        relevant_shifts = [shift for shift in shifts if shift.road == self.selected_road.target.road]

        mouse_x, mouse_y = pygame.mouse.get_pos()
        
        mouse_shift = -math.floor((self.selected_road.rect.top - mouse_y) / tile_size) - 1
        existing_shift = self.action.shift.y_delta if self.action.shift != None else 0

        new_shift = Shift(self.selected_road.target.road, mouse_shift + existing_shift)
        # Highlight moves
        # car_state = self.current_state.find_car_state(self.selected_car)
        if new_shift in relevant_shifts or new_shift.y_delta == 0:
            self.current_shift = new_shift
        if self.current_shift != None:
            self.current_state = self.original_state.apply_action(Action(self.current_shift,  []))

        draw_offset = draw_state(self.current_state)

        # Find the road including the offset from the current state
        for road in self.current_state.roads:
            if road.road == self.selected_road.target.road:
                for border in road_borders(road, draw_offset):
                    if len(relevant_shifts) == 0:
                        # Indicate that the road cannot be moved
                        paint_highlight_rect(border, pygame.Color(255,0,0,255))
                    else:
                        paint_highlight_rect(border, pygame.Color(0,0,255,255))
            

        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                if self.current_shift != None:
                    self.action = Action(self.current_shift, [])
                else:
                    self.action = Action(None, [])
                    self.current_state = self.original_state
                self.selected_road = None


    def __select_car_or_road(self):
        draw_state(self.current_state)
        pygame.display.flip()
        for event in pygame.event.get():
            if event.type == pygame.MOUSEBUTTONDOWN:
                mouse_x, mouse_y = pygame.mouse.get_pos()
                for element in get_overlapping_elements(mouse_x, mouse_y, self.current_state):
                    if element.type == CollisionType.CAR:
                        car = element.target.car
                        player_owns_car = car.owner == self.current_state.turn
                        car_is_neutral = car.owner == Owner.NEUTRAL
                        if player_owns_car or car_is_neutral:
                            self.selected_car = element
                            break
                    if element.type == CollisionType.ROAD and self.shifts_remaining > 0:
                        self.selected_road = element

                        if self.current_shift != None and self.current_shift.road != element.target.road:
                            # Reset the road if the user select a different road
                            self.current_state = self.original_state
                            self.current_shift = None
                        break
