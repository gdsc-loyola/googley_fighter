# src/sprite.py
"""
Googley Fighter - Fighter Sprite Handling
"""

import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT
from config import GROUND_Y
from PIL import Image


class Fighter(pygame.sprite.Sprite):
    """Fighter with optional GIF animation + health/damage system."""
    def __init__(self, x, y, gif_right=None, gif_left=None, color=(255, 0, 0), controls=None, speed=5):
        super().__init__()
        self.controls = controls
        self.speed = speed
        self.rect = pygame.Rect(x, y, 32, 32)

        # Health system
        self.max_health = 100
        self.health = self.max_health
        self.damage_cooldown = 30   # frames before next damage
        self.damage_timer = 0

        # Attack system
        self.is_attacking = False
        self.attack_damage = 10
        self.attack_range = 40  # distance for attack to connect

        # Jump system
        self.is_jumping = False
        self.jump_speed = -10
        self.gravity = 0.5
        self.vertical_speed = 0
        self.max_jump_height = GROUND_Y - 150

        # GIF frames
        self.frames_right = []
        self.frames_left = []
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_count = 0

        self.image = pygame.Surface((32, 32))
        self.image.fill(color)

        # Load GIFs
        if gif_right:
            self.frames_right = self.load_gif(gif_right)
        if gif_left:
            self.frames_left = self.load_gif(gif_left)

        self.direction = "right"  # default direction

    def jump(self):
        """Start a jump if not already jumping."""
        if not self.is_jumping and self.rect.bottom >= GROUND_Y:
            self.is_jumping = True
            self.vertical_speed = self.jump_speed

    def load_gif(self, path):
        pil_image = Image.open(path)
        frames = []
        try:
            while True:
                frame = pil_image.convert("RGBA")
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                surface = pygame.image.fromstring(data, size, mode)
                frames.append(surface)
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass
        return frames

    def take_damage(self, amount):
        """Apply damage to the fighter."""
        if self.damage_timer == 0:  # only if cooldown expired
            self.health -= amount
            if self.health < 0:
                self.health = 0
            self.damage_timer = self.damage_cooldown

    def attack(self, others):
        """Perform an attack against nearby fighters."""
        for other in others:
            if self.direction == "right":
                attack_rect = pygame.Rect(self.rect.right, self.rect.top, self.attack_range, self.rect.height)
            else:
                attack_rect = pygame.Rect(self.rect.left - self.attack_range, self.rect.top, self.attack_range, self.rect.height)

            if attack_rect.colliderect(other.rect):
                other.take_damage(self.attack_damage)

    def move(self, dx, dy, others):
        # Update direction based on horizontal input
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"

        # Horizontal movement
        self.rect.x += dx * self.speed

        # Vertical movement (jump + gravity)
        if self.is_jumping:
            self.vertical_speed += self.gravity
            self.rect.y += self.vertical_speed
            if self.rect.top < self.max_jump_height:
                self.rect.top = self.max_jump_height
                self.vertical_speed = 0
            if self.rect.bottom > GROUND_Y:
                self.rect.bottom = GROUND_Y
                self.is_jumping = False
                self.vertical_speed = 0
        else:
            if self.rect.bottom < GROUND_Y:
                self.vertical_speed += self.gravity
                self.rect.y += self.vertical_speed
            else:
                self.rect.bottom = GROUND_Y
                self.vertical_speed = 0

        # Horizontal boundaries
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def animate(self):
        """Cycle through frames for GIF animation."""
        frames = self.frames_right if self.direction == "right" else self.frames_left
        if not frames:
            return
        self.frame_count += 1
        if self.frame_count >= self.frame_delay:
            self.frame_count = 0
            self.current_frame = (self.current_frame + 1) % len(frames)
            self.image = frames[self.current_frame]

    def update(self, others):
        if self.controls:
            dx, dy, attack = self.controls.get_input(self)
            if dy < 0:  # jump input
                self.jump()
                dy = 0
            self.move(dx, dy, others)

            # Handle attack input
            if attack:
                self.attack(others)

        # Tick down damage cooldown
        if self.damage_timer > 0:
            self.damage_timer -= 1

        self.animate()


def create_fighters(player1_controls, player2_controls):
    """
    Create two fighters with animated GIFs:
    - Red Fighter (Player 1)
    - Blue Fighter (Player 2)
    """
    red_fighter = Fighter(
        x=100,
        y=GROUND_Y,
        gif_right="assets/images/googley_right.gif",
        gif_left="assets/images/googley_left.gif",
        controls=player1_controls
    )

    blue_fighter = Fighter(
        x=600,
        y=GROUND_Y,
        gif_right="assets/images/googley_right.gif",
        gif_left="assets/images/googley_left.gif",
        controls=player2_controls
    )

    fighters = pygame.sprite.Group()
    fighters.add(red_fighter, blue_fighter)
    return fighters, red_fighter, blue_fighter
