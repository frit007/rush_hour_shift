from dataclasses import dataclass
import pygame
from enum import Enum
import math
import os

from state import CarState, RoadState, State
from type import *
from players.player import *

MAIN_BG_COLOR = '#C5E0DB'
GAME_BG_COLOR = pygame.Color(MAIN_BG_COLOR)
FONT = 'Roboto'
FONT_COLOR = '#313131'

SCREEN_WIDTH = 600
SCREEN_HEIGHT = 600
SCREEN_SIZE = (SCREEN_WIDTH, SCREEN_HEIGHT)

TILE_SIZE = 30
NAME = 'Rush Hour Shift'

tile_image = pygame.image.load(os.path.join("data/images", "Tile.png"))
tile_image = pygame.transform.scale(tile_image, (TILE_SIZE, TILE_SIZE))

road_frame_image = pygame.image.load(os.path.join("data/images", "RoadFrame.png"))

screen = None

def create_window():
    global screen
    pygame.init()
    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT)) # pygame.RESIZABLE (resolution switch?)

    pygame.display.set_caption(NAME)
    
    screen.fill(GAME_BG_COLOR)


def draw_car(car_state: CarState, draw_offset:tuple[int, int]):
    screen.blit(car_state.car.image, screen_coord(car_state.x, car_state.y, draw_offset))

def draw_cars(car_states: list[CarState], draw_offset:tuple[int, int]):
    for car_state in car_states:
        draw_car(car_state, draw_offset)

def calculate_draw_offset(roads: list[RoadState]):
    # height = roads[0].road.to_y

    vertical_tiles = SCREEN_HEIGHT/TILE_SIZE

    prefered_y = vertical_tiles / 2

    # y_offsets = map(lambda state: state.y_offset, roads)
    y_offsets = [x.y_offset for x in roads]
    y_mins = [x.from_y() for x in roads]
    y_maxs = [x.to_y() for x in roads]

    top = min(y_offsets)

    height = (max(y_maxs) - min(y_mins)) + 1
    # x-top-height/2=prefered_y
    # +prefered_y+top+height/2=prefered_y
    y_offset = -top + (prefered_y - height/2)

    # TODO make width dynamic
    return (3, math.floor(y_offset))
    # return (3, math.floor(center_y + height / 2))

def screen_coord(x:int, y:int, draw_offset:tuple[int, int]):
    return (
                TILE_SIZE * (x + draw_offset[0]),
                TILE_SIZE * (y + draw_offset[1]),
            )

def draw_road(road: Road, draw_offset: tuple[int, int]):
    scaled_road_frame_image = pygame.transform.scale(road_frame_image, ((road.to_x-road.from_x + 1) * TILE_SIZE, TILE_SIZE))
    for x in range(road.from_x, road.to_x + 1):
        for y in range(road.from_y, road.to_y + 1):
            screen.blit(tile_image, screen_coord(x, y, draw_offset))
    screen.blit(scaled_road_frame_image, screen_coord(road.from_x, road.from_y-1, draw_offset))
    screen.blit(scaled_road_frame_image, screen_coord(road.from_x, road.to_y+1, draw_offset))

def draw_roads(roads: list[RoadState], draw_offset: tuple[int, int]):
    for road in roads:
        draw_road(road.road, (draw_offset[0], draw_offset[1] + road.y_offset))

def draw_car_ids(state: State, draw_offset: tuple[int, int]):
    font = pygame.font.Font(None, 32)
    for car_state in state.cars:
        text = font.render(str(car_state.car.id), True, (0,255,0), None)
        textRect = text.get_rect()
        textRect.center = ((car_state.x + draw_offset[0] + 0.5) * TILE_SIZE, (car_state.y + draw_offset[1] + 0.5) * TILE_SIZE)
        screen.blit(text, textRect)

def draw_car_positions(state: State, draw_offset: tuple[int, int]):
    font = pygame.font.Font(None, 16)
    for car_state in state.cars:
        text = font.render(f"({car_state.x},{car_state.y})", True, (0,255,0), None)
        textRect = text.get_rect()
        textRect.center = ((car_state.x + draw_offset[0] + 0.5) * TILE_SIZE, (car_state.y + draw_offset[1] + 0.5) * TILE_SIZE)
        screen.blit(text, textRect)

def draw_state(state: State):
    screen.fill(GAME_BG_COLOR)
    draw_offset = calculate_draw_offset(state.roads)
    draw_roads(state.roads, draw_offset)
    draw_cars(state.cars, draw_offset)
    # draw_car_ids(state, draw_offset)
    # draw_car_positions(state, draw_offset)
    highlight_turn_car(state, draw_offset)
    return draw_offset

def highlight_turn_car(state: State, draw_offset: tuple[int, int]):
    for car in state.cars:
        if car.car.owner == state.turn:
            paint_highlight((car.x, car.y), (2, 1), pygame.Color(50, 168, 82, 255), draw_offset)

def paint_highlight(position:tuple[int, int], size: tuple[int, int], color: pygame.Color, draw_offset:tuple[int, int]):
    top_left_corner = screen_coord(position[0], position[1], draw_offset)
    top_right_corner = (top_left_corner[0] + size[0] * TILE_SIZE, top_left_corner[1])
    bottom_right_corner = (top_left_corner[0] + size[0] * TILE_SIZE, top_left_corner[1] + size[1] * TILE_SIZE)
    bottom_left_corner = (top_left_corner[0], top_left_corner[1] + size[1] * TILE_SIZE)
    pygame.draw.lines(screen, color, True, [top_left_corner, top_right_corner, bottom_right_corner, bottom_left_corner], 3)

def paint_highlight_rect(rect: pygame.Rect, color: pygame.Color):
    pygame.draw.lines(screen, color, True, [rect.topleft, rect.topright, rect.bottomright, rect.bottomleft], 3)


class CollisionType(Enum):
    CAR = 1
    SQUARE = 2
    ROAD = 3


def car_rect(car: CarState, draw_offset: tuple[int, int]):
    return car.car.image.get_rect().move(screen_coord(car.x, car.y, draw_offset))

def field_rect(x: int,y: int, draw_offset: tuple[int, int], size: tuple[int, int]=(1,1)):
    top_left = screen_coord(x, y, draw_offset)
    return pygame.Rect(top_left[0],top_left[1], size[0] * TILE_SIZE, size[1] * TILE_SIZE)

def road_borders(road: RoadState, draw_offset: tuple[int, int]):
    return [
        field_rect(road.road.from_x,road.road.from_y - 1 + road.y_offset, draw_offset, (road.road.to_x-road.road.from_x + 1,1)),
        field_rect(road.road.from_x,road.road.to_y + 1 + road.y_offset, draw_offset, (road.road.to_x-road.road.from_x + 1,1)),
    ]

@dataclass(frozen=True, slots=True)
class OverlappingElement:
    target: None | CarState | RoadState
    type: CollisionType
    rect: pygame.Rect
    grid_pos: tuple[int, int]

def get_overlapping_elements(x: int, y: int, state: State) -> list[OverlappingElement]:
    overlaps = []
    draw_offset = calculate_draw_offset(state.roads)
    
    grid_pos = (math.floor((x) / TILE_SIZE) - draw_offset[0], math.floor((y) / TILE_SIZE) - draw_offset[1])

    for car in state.cars:
        image_rect = car_rect(car, draw_offset)
        if image_rect.collidepoint(x, y):
            overlaps.append(OverlappingElement(car, CollisionType.CAR, image_rect, grid_pos))
    

    overlaps.append(OverlappingElement(None, CollisionType.SQUARE, field_rect(grid_pos[0], grid_pos[1],draw_offset), grid_pos))

    for road in state.roads:
        for road_border in road_borders(road, draw_offset):
            if road_border.collidepoint(x,y):
                overlaps.append(OverlappingElement(road, CollisionType.ROAD, road_border, grid_pos))
        

    return overlaps

@dataclass(slots=True, frozen=True)
class MoveAndPosition:
    move: Move
    position: tuple[int, int]

def translate_move_to_position(car_state: CarState, moves: list[Move]) -> list[MoveAndPosition]:
    positions = []
    for move in moves:
        offset_y = 1 if car_state.car.direction == Direction.VERTICAL and move.y_delta > 0 else 0
        offset_x = 1 if car_state.car.direction == Direction.HORIZONTAL and move.x_delta > 0 else 0
        position = (
            car_state.x + offset_x * (car_state.car.car_length - 1) + move.x_delta,
            car_state.y + offset_y * (car_state.car.car_length - 1) + move.y_delta
        )
        positions.append(MoveAndPosition(move, position))
    return positions

@dataclass(slots=True, frozen=True)
class ShiftAndRect:
    shift: Shift
    rect: pygame.Rect

def translate_shifts_to_rects(road_state: RoadState, rect:pygame.Rect, shifts: list[Shift]) -> list[ShiftAndRect]:
    positions = []
    for shift in shifts:
        if shift.road != road_state.road:
            continue
        positions.append(
            ShiftAndRect(
                shift,
                rect.move(
                    0,
                    shift.y_delta * TILE_SIZE
                )
            )
        )
    return positions

def draw_shift_rects(shifts: list[ShiftAndRect]):
    for shift in shifts:
        paint_highlight_rect(shift.rect, pygame.Color(0, 255, 0, 255))

def draw_car_movement_options(positions:list[MoveAndPosition], draw_offset: tuple[int, int]):
    for position in positions:
        paint_highlight(
                position.position,
                (1,1),
                pygame.Color(0,255,0,255),
                draw_offset
        )
