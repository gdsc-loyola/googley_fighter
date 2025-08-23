# src/config.py

# Screen settings
SCREEN_WIDTH = 900
SCREEN_HEIGHT = 600
FPS = 60
GROUND_Y = 472

# Fighter spawn positions
RED_SPAWN = (200, SCREEN_HEIGHT - 200)
BLUE_SPAWN = (SCREEN_WIDTH - 300, SCREEN_HEIGHT - 200)

# AI Bot Settings
AI_ATTACK_RANGE = 50       # Pixels, how close AI needs to be to attack
AI_ATTACK_COOLDOWN = 45    # Frames between attacks (1 sec at 60 FPS)
