import os
import string
import random
import pygame

from state import *
from type import *
from ui import TILE_SIZE

dir = os.path.split(os.path.realpath(__file__))[0]

## Images ##

img_dir = os.path.join(dir, 'data/images')

def load_image(name: str, width: int, height: int) -> pygame.image:
    img = pygame.image.load(os.path.join(img_dir, name))
    return pygame.transform.scale(img, (width, height))

player1 = load_image('Player1Car.png', TILE_SIZE, TILE_SIZE * 2)
player2 = load_image('Player2Car.png', TILE_SIZE, TILE_SIZE * 2)

audi_red = load_image('Audi_Red.png', TILE_SIZE, TILE_SIZE * 2)
audi_purple = load_image('Audi_Purple.png', TILE_SIZE, TILE_SIZE * 2)
police = load_image('Police.png', TILE_SIZE, TILE_SIZE * 2)
taxi = load_image('Taxi.png', TILE_SIZE, TILE_SIZE * 2)

ambulance = load_image('Ambulance.png', TILE_SIZE, TILE_SIZE * 3)
car = load_image('Car.png', TILE_SIZE, TILE_SIZE * 3)
mini_truck = load_image('Mini_Truck.png', TILE_SIZE, TILE_SIZE * 3)
mini_van = load_image('Mini_Van.png', TILE_SIZE, TILE_SIZE * 3)

car_images = {2 : [audi_red, audi_purple, police, taxi], 
              3 : [ambulance, car, mini_truck, mini_van]}

## Maps ##

horizontal_markers = ['O', '1', '2']
vertical_markers = ['X']
road_divider = ['[']
dividers = [*road_divider, '|', ']']
valid_markers = [*horizontal_markers, *vertical_markers]

def followTrail(lines : list[str], i : int, x : int, y : int, 
                chr : str) -> tuple[tuple[int, int], tuple[int, int]]:
    start = (x, y)

    if chr in vertical_markers or chr in road_divider:
        while y + 1 < len(lines) and lines[y + 1][i] in chr:
            y += 1
            lines[y][i] = ' '

    if chr in horizontal_markers or chr in road_divider:
        while i + 2 < len(lines[y]) and lines[y][i + 2] in chr:
            i += 2
            x += 1
            lines[y][i] = ' '

    return start, (x, y)


def read_map(lines : list[str]) -> State:
    map = State([], [], Owner.PLAYER1, [])
    car_id = 0
    for i in range(len(lines)):
        lines[i] = list(lines[i].replace("\n",""))

    for y in range(len(lines)):
        x = 0
        for i in range(0, len(lines[y]) - 1, 2):
            divider, marker = lines[y][i:i+2]

            if marker in valid_markers:
                (x0, y0), (x1, y1) = followTrail(lines, i + 1, x, y, marker)

                if marker in horizontal_markers:
                        length = x1 - x0 + 1
                        rotation = 90
                        match marker:
                            case '1':
                                image = player1
                                owner = Owner.PLAYER1
                                rotation = 270
                            case '2':
                                image = player2
                                owner = Owner.PLAYER2
                            case _:
                                image = random.choice(car_images[length])
                                owner = Owner.NEUTRAL

                        car = Car(car_id, pygame.transform.rotate(image, rotation), length, Direction.HORIZONTAL, owner)
                        
                elif marker in vertical_markers:
                    length = y1 - y0 + 1
                    image = random.choice(car_images[length])
                    car = Car(car_id, image, length, Direction.VERTICAL, Owner.NEUTRAL)

                map.cars.append(CarState(x0, y0, car))
                car_id = car_id + 1

            if divider in road_divider:
                (x0, y0), (x1, y1) = followTrail(lines, i, x, y, divider)

                map.roads.append(RoadState(0, Road(0, x0 - 1, y0, y1, True)))
                map.roads.append(RoadState(0, Road(x0, x1, y0, y1, False)))
                x_max = len([ch for ch in lines[y] if ch not in dividers]) - 1
                map.roads.append(RoadState(0, Road(x1 + 1, x_max, y0, y1, True)))

            x += 1

    return map

def parse_number(name: str):
    digits = ''.join(ch for ch in name if ch in string.digits)
    return int(digits)

def load_maps() -> list[State]:
    map_dir = os.path.join(dir, 'data/maps')
    map_files = sorted(os.listdir(map_dir), key = parse_number)
    maps = []

    for file in map_files:
        with open(os.path.join(map_dir, file), 'r', encoding='utf-8') as f:
            lines = f.readlines()
        map = read_map(lines)
        maps.append((file.replace('.map', ''), map))

    return maps
