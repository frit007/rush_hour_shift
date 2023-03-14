from enum import Enum
from dataclasses import dataclass, field

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
    from_x: int
    to_x: int
    from_y: int
    to_y: int
    allow_movement: bool

@dataclass(frozen=True, slots=True)
class Car:
    id: int
    car_length: int
    direction: Direction
    owner: Owner

### Card ###

@dataclass(frozen=True, slots=True)
class Card:
    moves: int # how many car moves they can make
    is_slide_x: bool # slider allows them to move 1 car as far as they want to
    moveRoads: int # how many roads they can move

### Action ###

@dataclass(frozen=True, slots=True)
class Move:
    car: Car
    x_delta:int 
    y_delta:int
    def magnitude(self):
        return abs(self.x_delta) + abs(self.y_delta)

@dataclass(frozen=True, slots=True)
class Shift:
    road: Road
    y_delta: int

@dataclass(frozen=True, slots=True)
class Action:
    shift: Shift
    moves: list[Move]
