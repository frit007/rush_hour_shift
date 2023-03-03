from type import *
import copy 

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

class State:
    roads: list[RoadState]
    cars: list[CarState]
    turn: Owner
    # Don't store the actual cards, instead store how many of each card is still available in the deck
    # the index in the array corresponds to 
    cards: list[int]
    def __init__(self, roads: list[RoadState], cars: list[RoadState], turn: Owner, cards: list[int]) -> None:
        self.roads = roads
        self.cars = cars
        self.turn = turn
        self.cards = cards
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
    def apply_action(self, action: Action):
        new_state = copyState(self)
        if action.shift != None:
            shift = action.shift
            road = shift.road
            # Make copies of the original state, but shifted
            new_state.roads = [RoadState(road_state.y_offset + shift.y_delta if road_state.road == road else road_state.y_offset, road_state.road) for road_state in self.roads]
            new_state.cars = [CarState(car_state.x, car_state.y + (action.shift.y_delta if road.from_x() <= car_state.x and car_state.x <= road.to_x() else 0), car_state.car) for car_state in new_state.cars]

        for move in action.moves:
            current_car_state = new_state.__get_and_remove_car_state(move.car)
            new_state.cars.append(
                CarState(
                    current_car_state.x + move.x_delta, 
                    current_car_state.y + move.y_delta,
                    current_car_state.car
                )
            )
        return new_state

    def __get_and_remove_car_state(self, car: Car) -> CarState:
        found_state = None
        for car_state in self.cars:
            if car_state.car == car:
                found_state = car_state
                break
        self.cars.remove(found_state)
        return found_state

    def get_legal_actions(self) -> list[Action]:
        pass

    # slight rule change, 
    # the player when they reach the end of the board, 
    # not when they have driven over the edge
    def get_winner(self):
        for car_state in self.cars:
            if car_state.car.owner == Owner.PLAYER1 and car_state.x == 12:
                return Owner.PLAYER1
            if car_state.car.owner == Owner.PLAYER2 and car_state.x == 0:
                return Owner.PLAYER2
        return None

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


    def is_blocked(self, x:int, y:int, except_car :Car):
        # Check if the position is part of any road
        part_of_road = False
        for road_state in self.roads:
            if (x >= road_state.from_x() 
                and x <= road_state.to_x() 
                and y >= road_state.from_y() 
                and y <= road_state.to_y()):
                    part_of_road = True
        if not part_of_road:
            return True

        # Check if another car is on the same tile
        for car in self.cars:
            if car.is_on_square(x,y) and car.car != except_car:
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