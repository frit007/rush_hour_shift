from type import *

class RoadState:
    road: Road
    y_offset: int
    def __init__(self, y_offset:int, road:Road) -> None:
        self.y_offset = y_offset
        self.road = road

class CarState:
    x: int
    y: int
    car: Car
    def __init__(self, x:int, y:int, car: Car) -> None:
        self.x = x
        self.y = y
        self.car = car
    def __repr__(self):
        return "CarState: pos: ({}, {})".format(self.x, self.y)

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

    def get_legal_actions(self) -> list[Action]:
        pass

    def new_game(self):
        # Maybe move to constructor
        self.roads = [
            RoadState(0, Road(0,4,0,5)),
            RoadState(0, Road(5,8,0,5)),
            RoadState(0, Road(5,8,0,5)),
        ]
        
        self.cars = self.__place_cars()
        self.cards = [5,5,5,5,5]
        self.turn = Owner.PLAYER1

    def is_blocked(self, x:int, y:int):
        pass

    def __place_cars() -> list[CarState]:
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
