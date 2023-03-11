from __future__ import annotations
import copy 

from logic.type import *

class RoadState:
    road: Road
    y_offset: int
    def __init__(self, y_offset:int, road:Road) -> None:
        self.y_offset = y_offset
        self.road = road
    def __repr__(self):
        return f"RoadState: y_offset: {self.y_offset} road: {self.road}\n"

    def from_x(self):
        return self.road.from_x
    
    def to_x(self):
        return self.road.to_x
    
    def from_y(self):
        return self.road.from_y + self.y_offset
    
    def to_y(self):
        return self.road.to_y + self.y_offset
    
    def width(self):
        return self.road.to_x - self.road.from_x + 1

class CarState:
    x: int
    y: int
    car: Car
    def __init__(self, x:int, y:int, car: Car) -> None:
        self.x = x
        self.y = y
        self.car = car

    def __repr__(self):
        return f"CarState: pos: ({self.x}, {self.y}) car: {self.car}\n"
    
    def is_on_square(self, x: int, y: int):
        if self.car.direction == Direction.HORIZONTAL:
            return y == self.y and x >= self.x and x < self.x + self.car.car_length
        else:
            return x == self.x and y >= self.y and y < self.y + self.car.car_length

@dataclass(slots=True)
class State:
    roads: list[RoadState]
    cars: list[CarState]
    turn: Owner
    # Don't store the actual cards, instead store how many of each card is still available in the deck
    # the index in the array corresponds to 
    cards: list[int]
    car_map: dict[(int,int), Car]
    
    def __init__(self, roads: list[RoadState], cars: list[CarState], turn: Owner, cards: list[int]) -> None:
        self.roads = roads
        self.cars = cars
        self.turn = turn
        self.cards = cards
        # Create a car map

    def generate_map(self):
        self.car_map = {}
        for car_state in self.cars:
            delta = (1,0) if car_state.car.direction == Direction.HORIZONTAL else (0,1)
            for i in range(car_state.car.car_length):
                self.car_map[(car_state.x + delta[0] * i, car_state.y + delta[1] * i)] = car_state.car

    def __repr__(self):
        return f"State: roads: {self.roads} cars: {self.cars} turn: {self.turn} cards: {self.cards}\n"
    
    def switch_turn(self):
        if self.turn == Owner.PLAYER1:
            self.turn = Owner.PLAYER2
        else:
            self.turn = Owner.PLAYER1

    # TODO maybe there is something more efficient than copy
    # Note: This doesn't switch whose turn it is
    # Return a new state, with the actions applied
    def apply_action(self, action: Action, switch_turn: bool = True):
        new_state = copyState(self)
        if action.shift != None:
            shift = action.shift
            road = shift.road
            # Make copies of the original state, but shifted
            new_state.roads = [RoadState(road_state.y_offset + shift.y_delta if road_state.road == road else road_state.y_offset, road_state.road) for road_state in self.roads]
            new_state.cars = [CarState(car_state.x, car_state.y + (action.shift.y_delta if road.from_x <= car_state.x and car_state.x <= road.to_x else 0), car_state.car) for car_state in new_state.cars]

        for move in action.moves:
            current_car_state = new_state.__get_and_remove_car_state(move.car)
            new_state.cars.append(
                CarState(
                    current_car_state.x + move.x_delta, 
                    current_car_state.y + move.y_delta,
                    current_car_state.car
                )
            )
            
        if switch_turn:
            new_state.switch_turn()
        new_state.generate_map()
        return new_state
    
    def minimized_state(self):
        cars = [(car_state.car.id, car_state.x, car_state.y) for car_state in self.cars]
        cars.sort()
        road = [road_state.y_offset for road_state in self.roads]
        return (tuple(cars), tuple(road), self.turn, tuple(self.cards))

    def __hash__(self):
        return hash(self.minimized_state())
    
    def __eq__(self, other):
        if isinstance(other, State):
            return self.minimized_state() == other.minimized_state()
        return False

    def __get_and_remove_car_state(self, car: Car) -> CarState:
        found_state = None
        for car_state in self.cars:
            if car_state.car == car:
                found_state = car_state
                break
        self.cars.remove(found_state)
        return found_state
        
    def get_player_cars(self) -> tuple[CarState, CarState]:
        player1_car = None
        player2_car = None
        for car in self.cars:
            if car.car.owner == Owner.PLAYER1:
                player1_car = car
            elif car.car.owner == Owner.PLAYER2:
                player2_car = car
        return player1_car, player2_car

    def get_legal_actions(self) -> list[Action]:
        actions = []
        
        # allow moving any NEUTRAL or PLAYER car
        for car in self.cars:
            if car.car.owner == self.turn or car.car.owner == Owner.NEUTRAL:
                for move in self.car_moves(car, 3):
                    actions.append(Action(None, [move]))

        actions = [*actions, *[Action(shift, []) for shift in self.all_shifts()]]

        return actions

    # slight rule change, 
    # the player when they reach the end of the board, 
    # not when they have driven over the edge
    def get_winner(self, map: Map):
        player1_car, player2_car = self.get_player_cars()

        if player1_car.x == map.player1_goal:
            return Owner.PLAYER1
        elif player2_car.x == map.player2_goal:
            return Owner.PLAYER2
        else:
            return None

    def is_draw(self):
        player1_car, player2_car = self.get_player_cars()
        return (player1_car.y == player2_car.y 
              and player1_car.x - player2_car.x + 2 == 0
              and player1_car.x not in [road_state.road.to_x - 1 for road_state in self.roads])

    def all_shifts(self) -> list[Shift]:
        shifts = []
        for road in self.unlocked_road_states():
            road_index = self.roads.index(road)
            left_neighbour = self.roads[road_index - 1] if road_index > 0 else None
            right_neighbour = self.roads[road_index + 1] if road_index < len(self.roads) - 1 else None

            max_down = 10
            max_up = 10

            if left_neighbour != None:
                max_down = min(max_down, abs(road.from_y() - left_neighbour.to_y()))
                max_up = min(max_up, abs(road.to_y() - left_neighbour.from_y()))
                
            if right_neighbour != None:
                max_down = min(max_down, abs(road.from_y() - right_neighbour.to_y()) )
                max_up = min(max_up, abs(road.to_y() - right_neighbour.from_y()))

            for delta in range(-max_down, max_up + 1):
                if delta != 0:
                    shifts.append(Shift(road.road, -delta))

        return shifts

    # TODO: Optimize
    def unlocked_road_states(self) -> list[RoadState]:
        unlocked = []

        # only horizontal cars can lock
        horizontal_car_states = [car for car in self.cars if car.car.direction == Direction.HORIZONTAL]
        moveable_roads = [road for road in self.roads if road.road.allow_movement]
        for road in moveable_roads:
            for car_state in horizontal_car_states:
                if ((car_state.x <= road.to_x() and car_state.x + car_state.car.car_length - 1 > road.to_x())
                    or 
                    (car_state.x < road.from_x() and car_state.x + car_state.car.car_length - 1 >= road.from_x())
                    ):
                    break
            else:
                # avoid adding the same road twice (break nested for loop)
                unlocked.append(road)

        return unlocked

    def car_is_blocked(self, x:int, y:int, car: Car):
        dir = (1, 0) if car.direction == Direction.HORIZONTAL else (0,1)
        for i in range(car.car_length):
            if self.is_blocked(x + dir[0] * i, y + dir[1] * i, car):
                return True
        return False

    def is_on_road(self, x: int, y: int):
        part_of_road = False
        for road_state in self.roads:
            if (x >= road_state.from_x() 
                and x <= road_state.to_x() 
                and y >= road_state.from_y() 
                and y <= road_state.to_y()):
                    part_of_road = True
        return part_of_road

    def is_blocked(self, x:int, y:int, except_car: Car):
        # Check if the position is part of any road
        if not self.is_on_road(x,y):
            return True

        # Check if another car is on the same tile
        # for car in self.cars:
        #     if car.is_on_square(x,y) and car.car != except_car:
        #         return True
        existingCar = self.car_map.get((x,y))
        if existingCar not in [None, except_car]:
            return True
            
        return False

    def find_car_state(self, car:Car):
        for car_state in self.cars:
            if car_state.car == car:
                return car_state

    # doesn't yet account for actions that will be allowed by moving another car
    def car_moves(self, car_state: CarState, move_limit:int) -> list[Move]:
        delta = (1,0) if car_state.car.direction == Direction.HORIZONTAL else (0,1)

        moves = []

        for i in range(1, move_limit + 1):
            if not self.car_is_blocked(
                delta[0] * i + car_state.x,
                delta[1] * i + car_state.y,
                car_state.car):
                moves.append(Move(car_state.car, delta[0] * i, delta[1] * i))
            else:
                break
        for i in range(-1, -move_limit -1, -1):
            if not self.car_is_blocked(
                delta[0] * i + car_state.x, 
                delta[1] * i + car_state.y, 
                car_state.car):
                moves.append(Move(car_state.car, delta[0] * i, delta[1] * i))
            else:
                break

        return moves

# Note: this is not declared as a member functions, due to typing limitations
def copyState(state:State) -> State:
    new_state = State(copy.copy(state.roads), copy.copy(state.cars), state.turn, copy.copy(state.cards))
    # create a somewhat shallow copy of the state, Cars and roads should not be recreated but RoadState and CarState might have to be recreated.
    # Otherwise reference existing RoadState and CarState unless they have changed in someway(This might be too annoying to deal with)
    return new_state

@dataclass(frozen=True, slots=True)
class Map:
    initial_state: State
    player1_goal: int
    player2_goal: int
    potential_roadblocks: int
