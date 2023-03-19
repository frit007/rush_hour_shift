import math
from logic.state import State, Map
from logic.type import Owner, Direction

def heuristic_a(self, state: State, optimize_for: Owner = None):
    optimize_for = self.owner if optimize_for == None else optimize_for
    player1_car, player2_car = state.get_player_cars()

    car_block_potential = 90
    CAR_BLOCK_TILES = 5
    CAR_BLOCK_SCALE = 1
    # Heavier penalties the closer you are to a blocking car
    CAR_BLOCK_PENALTIES = [3,2,2,1,1]

    if optimize_for == Owner.PLAYER1:
        # Penalty if blocked by road
        player1_roadblocks = 0
        for road in state.roads:
            if (not(player1_car.y >= road.from_y()
                and player1_car.y <= road.to_y())
                and player1_car.x <= road.from_x()):

                player1_roadblocks += road.width()


        # High short range penalty to avoid entering a road that is occupied by a car that cannot move once we enter the road.
        # Without this check we can get to situations the car will approaching car and effectively reach a stuck state, since it has reached a local optimum
        # | | | | | [ | | | ] | | | | |
        # |O|O|O|2|2[ | | | ] | | | | |
        # | | | | | [ [ [ [ ] | | | | |
        # Instead we want to encourage the car to never enter the same road as a blocking horizontal car
        # | | | | | [ | | | ] | | | | |
        # |O|O|O| | [2|2| | ] | | | | |
        # | | | | | [ [ [ [ ] | | | | |
        # And ideally shift the road so it can progress
        #           [ | | | ] | | | | |
        # | | | | | [2|2| | ] | | | | |
        # |O|O|O| | [ [ [ [ ] | | | | |
        # | | | | | 
        # However it won't find this shift, unless we allow seeing cars far away, since otherwise the shifted version has the same score as before(Therefore we also need the small high range penalty)
        player1_blocking = 0
        distance = CAR_BLOCK_SCALE * CAR_BLOCK_TILES
        for x in range(player1_car.x + 2, min(self.map.player1_goal + 2, player1_car.x + 2 + CAR_BLOCK_TILES)):
            distance -= CAR_BLOCK_SCALE
            car = state.car_map.get((x, player1_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player1_blocking += CAR_BLOCK_PENALTIES[distance] * 15
                player1_blocking += CAR_BLOCK_PENALTIES[distance]

        # Small high range penalty for being on the row as blocking cars. 
        for x in range(player1_car.x + 2, self.map.player1_goal + 2):
            car = state.car_map.get((x, player1_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player1_blocking += 2
                player1_blocking += 1

        return (5 * player1_car.x
                + math.floor(0.5 * (car_block_potential - player1_blocking))
                + self.map.potential_roadblocks - player1_roadblocks)
    else:
        # Penalty if blocked by road
        player2_roadblocks = 0
        for road in state.roads:
            if (not(player2_car.y >= road.from_y()
                and player2_car.y <= road.to_y())
                and player2_car.x >= road.to_x()):

                player2_roadblocks += road.width()

        # High short range penalty to avoid entering a road that is occupied by a car that cannot move once we enter the road.
        # Without this check we can get to situations the car will approaching car and effectively reach a stuck state, since it has reached a local optimum
        # | | | | | [ | | | ] | | | | |
        # |O|O|O|2|2[ | | | ] | | | | |
        # | | | | | [ [ [ [ ] | | | | |
        # Instead we want to encourage the car to never enter the same road as a blocking horizontal car
        # | | | | | [ | | | ] | | | | |
        # |O|O|O| | [2|2| | ] | | | | |
        # | | | | | [ [ [ [ ] | | | | |
        # And ideally shift the road so it can progress
        #           [ | | | ] | | | | |
        # | | | | | [2|2| | ] | | | | |
        # |O|O|O| | [ [ [ [ ] | | | | |
        # | | | | | 
        # However it won't find this shift, unless we allow seeing cars far away, since otherwise the shifted version has the same score as before(Therefore we also need the small high range penalty)
        player2_blocking = 0
        distance = CAR_BLOCK_SCALE * CAR_BLOCK_TILES
        for x in range(player2_car.x - 1, max(self.map.player2_goal - 1, player2_car.x - 1 - CAR_BLOCK_TILES), -1):
            distance -= CAR_BLOCK_SCALE
            car = state.car_map.get((x, player2_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player2_blocking += CAR_BLOCK_PENALTIES[distance] * 15
                player2_blocking += CAR_BLOCK_PENALTIES[distance]

        # Small high range penalty for being on the row as blocking cars. 
        for x in range(player2_car.x - 1, self.map.player2_goal - 1, -1):
            car = state.car_map.get((x, player2_car.y))
            if car != None:
                if car.direction == Direction.HORIZONTAL:
                    # avoid horizontal cars on the same row
                    player2_blocking += 2
                player2_blocking += 1


        return (5 * abs(player2_car.x - self.map.player1_goal)
               + math.floor(0.5 * (car_block_potential - player2_blocking))
               + self.map.potential_roadblocks - player2_roadblocks)

