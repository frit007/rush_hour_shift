# import the pygame module
import pygame
import os
from type import *
from loader import load_map

# Cards based on # https://www.ultraboardgames.com/rush-hour-shift/game-rules.php
cards = [
    Card(4, False, 0),
    Card(3, False, 0),
    Card(0, False, 1),
    Card(0, True, 0),
    Card(2, False, 1)
]

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

image = pygame.image.load(os.path.join("data/images", "Ambulance.png"))
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
