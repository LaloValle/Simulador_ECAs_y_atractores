import pygame
from numpy import array

#=============
#   Colors
#=============
DARK_BLACK = (28,29,32)
LIGHT_BLACK_1 = (40,44,52)
LIGHT_BLACK_2 = (53,61,76)
# Gray pair
WHITE = (192,203,221)
GRAY = (162,170,185)
# Blue pair
BLUE = (17,192,186)
LIGHT_BLUE = (168,234,232)
# LIGHT_BLUE = (79,189,186)
# Yellow pair
YELLOW = (234,194,76)
LIGHT_YELLOW = (234,213,150)
# Red pair
RED = (206,71,96)
LIGHT_RED = (234,159,175)
# Green pair
GREEN = (0,161,157)
LIGHT_GREEN = (79,189,186)

COLORS_LIST = [DARK_BLACK,LIGHT_BLACK_1,LIGHT_BLACK_2,WHITE,GRAY,BLUE,LIGHT_BLUE,YELLOW,LIGHT_YELLOW,RED,LIGHT_RED,GREEN,LIGHT_GREEN]
HEX_COLORS_LIST = [
    '#D2FDFF', # Light Cyan
    '#CE4760', # Brick Red
    '#4C956C', # Middle Green
    '#eeebd3', # White
    '#058ED9', # Green Blue Crayola
    '#6a4c93', # Royal Purple
    ]
COLOUR_ATTRACTOR = '#F7C548'

#==================================================
# Bits mask for number of neighbourhood in the ECA
#==================================================
BITS_MASKS = [
    1, # 0 Neighbourhood
    2, # 1 Neighbourhood
    4, # 2 Neighbourhood
    8, # 3 Neighbourhood
    16, # 4 Neighbourhood
    32, # 5 Neighbourhood
    64, # 6 Neighbourhood
    128, # 7 Neighbourhood
 ]
#========================================================
# Wighted matrix for binary to decimal conversion in ECA
#========================================================
MATRIX_BIN_TO_DEC = array([4, 2, 1])

#============
#   Fonts
#============
pygame.font.init()
FONT = pygame.font.SysFont('Silka',15,False,False)
SMALL_FONT = pygame.font.SysFont('Silka',12,False,False)
MEDIUM_FONT = pygame.font.SysFont('Silka',25,False,False)
BIG_FONT = pygame.font.SysFont('Sikla',50,False,False)