# src/controls.py
"""
Controls module for Googley Fighter.
Defines input mappings for Player 1 and Player 2.
"""

import pygame


class Controls:
    """Base class for player controls."""
    def __init__(self, left, right, up, down, attack, fireball, speed=5):
        self.left = left
        self.right = right
        self.up = up
        self.down = down
        self.attack_key = attack
        self.fireball_key = fireball
        self.speed = speed

    def get_input(self, fighter=None):
        """Return (dx, dy, attack, fireball) based on pressed keys."""
        keys = pygame.key.get_pressed()
        dx = dy = 0
        attack = False
        fireball = False

        if keys[self.left]:
            dx -= 1
        if keys[self.right]:
            dx += 1
        if keys[self.up]:
            dy -= 1
        if keys[self.down]:
            dy += 1
        if keys[self.attack_key]:
            attack = True
        if keys[self.fireball_key]:
            fireball = True

        return dx, dy, attack, fireball


class Player1Controls(Controls):
    """WASD + Left Shift for Player 1."""
    def __init__(self):
        super().__init__(
            left=pygame.K_a,
            right=pygame.K_d,
            up=pygame.K_w,
            down=pygame.K_s,
            attack=pygame.K_SPACE,
            fireball=pygame.K_f,
            speed=5
        )


class Player2Controls(Controls):
    """Arrow Keys + Right Shift for Player 2."""
    def __init__(self):
        super().__init__(
            left=pygame.K_LEFT,
            right=pygame.K_RIGHT,
            up=pygame.K_UP,
            down=pygame.K_DOWN,
            attack=pygame.K_RSHIFT,
            fireball=pygame.K_h,
            speed=5
        )
