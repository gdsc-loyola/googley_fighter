# src/sounds.py
import pygame
import os

# Initialize the sound mixer
pygame.mixer.init()

# Load sounds
BACKGROUND_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "background.mp3"))
DAMAGE_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "damage.mp3"))
DEATH_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "death.mp3"))
BUTTON_SOUND = pygame.mixer.Sound(os.path.join("assets", "sounds", "button.mp3"))