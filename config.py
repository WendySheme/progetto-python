"""
Game constants and configuration settings
"""

# Screen settings
SCREEN_WIDTH = 800
SCREEN_HEIGHT = 600
FPS = 60

# Colors
WHITE = (255, 255, 255)
BLACK = (0, 0, 0)
RED = (255, 0, 0)
GREEN = (0, 255, 0)
BLUE = (0, 0, 255)
YELLOW = (255, 255, 0)
GRAY = (128, 128, 128)
DARK_GRAY = (64, 64, 64)
LIGHT_BLUE = (100, 149, 237)

# Player settings
PLAYER_WIDTH = 70
PLAYER_HEIGHT = 80
PLAYER_SPEED = 5
JUMP_STRENGTH = 15
GRAVITY = 0.8
MAX_FALL_SPEED = 20

# Enemy settings
ENEMY_WIDTH = 40
ENEMY_HEIGHT = 40
ENEMY_SPEED = 2

# Boss settings
BOSS_WIDTH = 80
BOSS_HEIGHT = 100
BOSS_SPEED = 3
BOSS_HEALTH = 5

# Platform settings
PLATFORM_HEIGHT = 20

# Game settings
STARTING_LIVES = 3
POINTS_PER_COIN = 10
POINTS_PER_ENEMY = 50
POINTS_PER_BOSS = 500

# Level settings
NUM_LEVELS = 3

# Background settings
BG_HORIZONTAL_OFFSET = -30  # Positive = shift right, Negative = shift left, 0 = center
PLATFORM_HORIZONTAL_OFFSET = -5 # Should match BG_HORIZONTAL_OFFSET to keep platforms aligned