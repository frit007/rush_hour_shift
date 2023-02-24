# import the pygame module
import pygame
import os
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

@dataclass(frozen=True, slots=True)
class Road:
    fromX: int
    toX: int
    fromY: int
    toY: int

class RoadState:
    road: Road
    yOffset: int
    def __init__(self, yOffset:int, road:Road) -> None:
        self.yOffset = yOffset
        self.road = road

@dataclass(frozen=True, slots=True)
class Car:
    image: pygame.Surface
    carLength: int
    direction: Direction
    owner: Owner

class CarState:
    x: int
    y: int
    car: Car
    def __init__(self, x:int, y:int, car: Car) -> None:
        self.x = x
        self.y = y
        self.car = car

class Player:
    def play(self, state):
        pass

class HumanPlayer(Player):
    def play(self, state):
        # Get user input, if you are feeling fancy by letting the user click on the screen.
        pass

class AIPlayer(Player):
    def play(self, state):
        # Do something awesome
        pass

@dataclass(frozen=True, slots=True)
class Card:
    moves: int # how many car moves they can make
    isSlideX: bool # slider allows them to move 1 car as far as they want to
    moveRoads: int # how many roads they can move

# Cards based on # https://www.ultraboardgames.com/rush-hour-shift/game-rules.php
cards = [
    Card(4, False, 0),
    Card(3, False, 0),
    Card(0, False, 1),
    Card(0, True, 0),
    Card(2, False, 1)
]

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
    moves: list[Car]

class State:
    roads: list[RoadState]
    cars: list[CarState]
    turn: Owner
    # Don't store the actual cards, instead store how many of each card is still available in the deck
    # the index in the array corresponds to 
    cards: list[int]
    def __init__(self) -> None:
        pass

    def copy(self, existingState):
        # create a somewhat shallow copy of the state, Cars and roads should not be recreated but RoadState and CarState might have to be recreated.
        # Otherwise reference existing RoadState and CarState unless they have changed in someway(This is probably too annoying to deal with)
        pass

    def play(self):
        if self.turn == Owner.PLAYER1:
            # avoid storing players as part of the state, players could be stored in an external array
            pass
        else:
            pass

    def draw(self):
        # go through roads and draw them
        # go through cars and draw them
        # Maybe move somewhere else
        pass

    def getLegalActions(self) -> list[Action]:
        pass

    def newGame(self):
        # Maybe move to constructor
        self.roads = [
            RoadState(0, Road(0,4,0,5)),
            RoadState(0, Road(5,8,0,5)),
            RoadState(0, Road(5,8,0,5)),
        ]
        
        self.cars = self.__placeCars()
        self.cards = [5,5,5,5,5]
        self.turn = Owner.PLAYER1

    def isBlocked(self, x:int, y:int):
        pass

    def __placeCars() -> list[CarState]:
        # We can take game setups from here
        # https://www.ultraboardgames.com/rush-hour-shift/game-rules.php
        # | | | | |X[ | | | ] |X| | | |
        # |P|P| | |X[X| | | ] |X|O|O|O|
        # | | | | | [X|X|X| ] |X| | | |
        # | | | |X| [ |X|X|X] | | | | |
        # |O|O|O|X| [ | | |X]X| | |P|P|
        # | | | |X| [ | | | ]X| | | | |
        pass

    def heuristic():
        # Calculate a heuristic for this field, this could include
        # - distance of to the goal
        # - cars blocking the cars
        pass

# Do some kind of search to find the next move. Maybe A-star
def findNextMove(state):
    pass
    

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

        
# Define the background colour
# using RGB color coding.
background_colour = (234, 212, 252)

tileSize = 50

image = pygame.image.load(os.path.join("images", "Ambulance.png"))
image = pygame.transform.scale(image, (tileSize,tileSize * 2))

# Define the dimensions of
# screen object(width,height)
screen = pygame.display.set_mode((600, 600))
#screen = pygame.display.set_mode((350, 250), pygame.RESIZABLE)

# Set the caption of the screen
pygame.display.set_caption('Rush hour shift')
  
# Fill the background colour to the screen
screen.fill(background_colour)

screen.blit(image, (0,0))
# Update the display using flip
pygame.display.flip()
  
# Variable to keep our game loop running
running = True
  
# game loop
while running:
    # for loop through the event queue  
    for event in pygame.event.get():
        # Check for QUIT event      
        if event.type == pygame.QUIT:
            running = False
