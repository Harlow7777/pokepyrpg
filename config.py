SCREEN_WIDTH = 640
SCREEN_HEIGHT = 480
TILESIZE = 32
FPS = 60

PLAYER_LAYER = 4
ENEMY_LAYER = 3
BLOCK_LAYER = 2
GROUND_LAYER = 1

PLAYER_SPEED = 3
ENEMY_SPEED = 2

RED = (255, 0, 0)
BLUE = (0, 0, 255)
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)

# 480/32 = 15 rows, 640/32 = 20 columns
# B for block represents walls
# P represents player
# . represents open tile
tilemap = [
    'BBBBBBBBBBBBBBBBBBBB',
    'B...E..............B',
    'B..................B',
    'B...BBB............B',
    'B..................B',
    'B..................B',
    'B..................B',
    'B...........P......B',
    'B.....BBB..........B',
    'B.......B......E...B',
    'B.......B..........B',
    'B..................B',
    'B..................B',
    'B..................B',
    'BBBBBBBBBBBBBBBBBBBB'
]