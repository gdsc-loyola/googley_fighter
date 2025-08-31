# src/sounds.py
import pygame
import os

# Initialize the sound mixer
pygame.mixer.init()

# Load sounds
BACKGROUND_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "background.ogg"))
DAMAGE_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "damage.ogg"))
DEATH_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "death.ogg"))
BUTTON_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "button.ogg"))