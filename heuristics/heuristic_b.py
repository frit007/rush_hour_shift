from logic.state import State, Map, CarState, RoadState
from logic.type import Owner, Direction

def road_is_blocking(car_state: CarState, state: State, road:RoadState):
    # print("Car y: " + str(car_state.y) + " Road2: " + str(road))
    if (not(car_state.y >= road.from_y() and car_state.y <= road.to_y())): 
        return True      
        
def heuristic_b(player, state: State, optimize_for: Owner = None):
    optimize_for = player.owner if optimize_for == None else optimize_for
    player1_car, player2_car = state.get_player_cars()
    CAR_BLOCK_TILES = 6 #number of tiles to look at ahead

    car_length = 2
    tiles_x = 14
    if optimize_for == Owner.PLAYER1:
        car_state = player1_car
        goal_x = player.map.player1_goal
        remaining_tiles = tiles_x-car_length-car_state.x
        passed_tiles = tiles_x-car_length-remaining_tiles
        head_x = car_state.x+1
        path = range(car_state.x + 2, min(goal_x + 1, head_x + CAR_BLOCK_TILES + 1))
        third_tile_in_front = head_x+CAR_BLOCK_TILES
        
        opponent_row = player2_car.y
        opponent_path = range(player.map.player2_goal, player2_car.x - 1)
    else:
        car_state = player2_car
        goal_x = player.map.player2_goal
        remaining_tiles = car_state.x
        passed_tiles = tiles_x-car_length-remaining_tiles
        head_x = car_state.x
        
        path = range(car_state.x - 1, max(goal_x, head_x - CAR_BLOCK_TILES - 1), -1)
        third_tile_in_front = head_x-CAR_BLOCK_TILES

        opponent_row = player1_car.y
        opponent_path = range(player1_car.x + 2, player.map.player1_goal)


    blocking_car_penalty = 0
    # print("path " + str(path))
    for x in path:
        #distance -= 2
        # print("x: " + str(x)+", " + str(car_state.y))
        car = state.car_map.get((x, car_state.y))
        if car != None:
            # print("FOUND CAR " + str(car.direction))
            if car.direction == Direction.HORIZONTAL:
                # avoid horizontal cars on the same row
                blocking_car_penalty += 2
            blocking_car_penalty += 1

    road_block_penalty = 0
    road_after_three_tiles = state.road_from_coordinate(third_tile_in_front)
    if (road_after_three_tiles != None
        and road_is_blocking(car_state, state, road_after_three_tiles)):
        road_block_penalty = 5

    block_opponent_bonus = 0
    for x in opponent_path:
        car = state.car_map.get((x, opponent_row))
        if car != None:
            block_opponent_bonus += 1

    #print("remaining_tiles " + str(2*remaining_tiles))
    #print("blocking_car_penalty " + str(blocking_car_penalty))
    #print("road_block_penalty " + str(road_block_penalty))
    #print("final: " + str((50 - 3*remaining_tiles - blocking_car_penalty - road_block_penalty)))
    return (100 - (3*remaining_tiles) - blocking_car_penalty - road_block_penalty + block_opponent_bonus)

