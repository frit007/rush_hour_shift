from logic.state import State, Map, CarState, RoadState
from logic.type import Owner, Direction

def road_is_blocking(car_state: CarState, state: State, road:RoadState):
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
        head_x = car_state.x+1
        path = range(car_state.x + 2, min(goal_x + 1, head_x + CAR_BLOCK_TILES + 1))
        third_tile_in_front = head_x+CAR_BLOCK_TILES
        
        opponent_row = player2_car.y
        opponent_path = range(player.map.player2_goal, player2_car.x - 1)
    else:
        car_state = player2_car
        goal_x = player.map.player2_goal
        remaining_tiles = car_state.x
        head_x = car_state.x
        
        path = range(car_state.x - 1, max(goal_x, head_x - CAR_BLOCK_TILES - 1), -1)
        third_tile_in_front = head_x-CAR_BLOCK_TILES

        opponent_row = player1_car.y
        opponent_path = range(player1_car.x + 2, player.map.player1_goal)

    # Penalty for blocking cars
    blocking_car_penalty = 0
    for x in path:
        car = state.car_map.get((x, car_state.y))
        if car != None:
            if car.direction == Direction.HORIZONTAL:
                # avoid horizontal cars on the same row
                blocking_car_penalty += 5
            blocking_car_penalty += 3

    # Penalty if blocked by road
    road_block_penalty = 0
    road_after_three_tiles = state.road_from_coordinate(third_tile_in_front)
    if (road_after_three_tiles != None
        and road_is_blocking(car_state, state, road_after_three_tiles)):
        road_block_penalty = 9

    # Bonus if moving blocking car, blocks opponent
    block_opponent_bonus = 0
    for x in opponent_path:
        car = state.car_map.get((x, opponent_row))
        if car != None:
            block_opponent_bonus += 1

    return (100 - (5*remaining_tiles) - blocking_car_penalty - road_block_penalty + block_opponent_bonus)

