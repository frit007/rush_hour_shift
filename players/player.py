import math
from logic.state import State, Map
from logic.type import Owner, Direction

class Player:
    name: str
    owner: Owner
    map: Map
    
    def play(self, state: State, map: Map, history: set[State]):
        pass

    def heuristic(self, state: State, optimize_for: Owner = None):
        optimize_for = self.owner if optimize_for == None else optimize_for
        player1_car, player2_car = state.get_player_cars()

        car_block_potential = 90
        CAR_BLOCK_TILES = 5
        CAR_BLOCK_SCALE = 1
        CAR_BLOCK_PENALTIES = [3,2,2,1,1]

        if optimize_for == Owner.PLAYER1:
            player1_roadblocks = 0
            for road in state.roads:
                if (not(player1_car.y >= road.from_y() 
                    and player1_car.y <= road.to_y())
                    and player1_car.x <= road.from_x()):
                    
                    player1_roadblocks += road.width()

            player1_blocking = 0
            distance = CAR_BLOCK_SCALE * CAR_BLOCK_TILES
            for x in range(player1_car.x + 2, min(self.map.player1_goal + 1, player1_car.x + 2 + CAR_BLOCK_TILES)):
                distance -= CAR_BLOCK_SCALE
                car = state.car_map.get((x, player1_car.y))
                if car != None:
                    if car.direction == Direction.HORIZONTAL:
                        # avoid horizontal cars on the same row
                        player1_blocking += CAR_BLOCK_PENALTIES[distance] * 15
                    player1_blocking += CAR_BLOCK_PENALTIES[distance]

            # small penalty for being on the row as blocking cars. Give enough vision to avoid waiting for a car that never moves
            for x in range(player1_car.x + 2, self.map.player1_goal + 1):
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
            player2_roadblocks = 0
            for road in state.roads:
                if (not(player2_car.y >= road.from_y() 
                    and player2_car.y <= road.to_y())
                    and player2_car.x >= road.to_x()):
                    
                    player2_roadblocks += road.width()

            player2_blocking = 0
            distance = CAR_BLOCK_SCALE * CAR_BLOCK_TILES
            for x in range(player2_car.x - 1, max(self.map.player2_goal, player2_car.x - 1 - CAR_BLOCK_TILES), -1):
                distance -= CAR_BLOCK_SCALE
                car = state.car_map.get((x, player2_car.y))
                if car != None:
                    if car.direction == Direction.HORIZONTAL:
                        # avoid horizontal cars on the same row
                        player2_blocking += CAR_BLOCK_PENALTIES[distance] * 15
                    player2_blocking += CAR_BLOCK_PENALTIES[distance]

            for x in range(player2_car.x - 1, self.map.player2_goal, -1):
                car = state.car_map.get((x, player2_car.y))
                if car != None:
                    if car.direction == Direction.HORIZONTAL:
                        # avoid horizontal cars on the same row
                        player2_blocking += 2
                    player2_blocking += 1


            return (5 * abs(player2_car.x - self.map.player1_goal)
                   + math.floor(0.5 * (car_block_potential - player2_blocking))
                   + self.map.potential_roadblocks - player2_roadblocks)
