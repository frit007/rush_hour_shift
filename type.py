import pygame
from enum import Enum
from dataclasses import dataclass

# # Car positions indicate the head of the car, the other positions are implicitly stored. 
class Direction(Enum):
    # A VERTICAL car with head at position (0,0) and length 2 has the positions [(0,0), (0,-1)]
    VERTICAL = 1
    # A Horizontal car with head at position (0,0) and length 2 has positions [(0,0), (1,0)]
    HORIZONTAL = 2

class Owner(Enum):
    PLAYER1 = 1
    PLAYER2 = 2
    NEUTRAL = 3

### Board ###

@dataclass(frozen=True, slots=True)
class Road:
    fromX: int
    toX: int
    fromY: int
    toY: int

@dataclass(frozen=True, slots=True)
class Car:
    image: pygame.Surface
    carLength: int
    direction: Direction
    owner: Owner

### Card ###

@dataclass(frozen=True, slots=True)
class Card:
    moves: int # how many car moves they can make
    isSlideX: bool # slider allows them to move 1 car as far as they want to
    moveRoads: int # how many roads they can move

### Action ###

@dataclass(frozen=True, slots=True)
class Move:
    car: Car
    xDelta:int 
    yDelta:int

@dataclass(frozen=True, slots=True)
class Shift:
    road: Road
    yDelta: int

@dataclass(frozen=True, slots=True)
class Action:
    shift: Shift
    moves: list[Move]
