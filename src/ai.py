# src/ai.py
import random
from config import AI_ATTACK_RANGE, AI_ATTACK_COOLDOWN


class AIControls:
    """Fake controls to drive a Fighter using AI logic (slower but not too weak)."""

    def __init__(self, fighter, target, config):
        self.fighter = fighter
        self.target = target
        self.config = config
        self.attack_cooldown = 0
        self.fireball_cooldown_timer = 0
        self.move_cooldown = 0   # delay between movement updates

    def get_input(self, fighter):
        """
        Returns (dx, dy, attack, fireball) like player controls.
        dx: -1 (left), 0 (idle), +1 (right)
        dy: -1 for jump
        attack: True/False
        fireball: True/False
        """
        if self.attack_cooldown > 0:
            self.attack_cooldown -= 1
        if self.fireball_cooldown_timer > 0:
            self.fireball_cooldown_timer -= 1
        if self.move_cooldown > 0:
            self.move_cooldown -= 1

        dx, dy, attack, fireball = 0, 0, False, False

        # Distance between AI and player
        dx_to_player = self.target.rect.centerx - self.fighter.rect.centerx
        distance = abs(dx_to_player)

        # Health ratio for decision making
        health_ratio = self.fighter.health / self.fighter.max_health

        # Only update movement every few frames
        if self.move_cooldown == 0:
            # Evade if low health
            if health_ratio < 0.3 and distance < AI_ATTACK_RANGE:
                # Move away from player
                dx = -1 if dx_to_player > 0 else 1
            else:
                # Normal behavior: approach player if too far
                if distance > AI_ATTACK_RANGE:
                    dx = 1 if dx_to_player > 0 else -1
                else:
                    dx = 0

            # Attack logic more aggressive if health is low
            attack_chance = 0.2 if health_ratio < 0.3 else 0.05
            if self.attack_cooldown == 0 and random.random() < attack_chance:
                attack = True
                self.attack_cooldown = max(10, AI_ATTACK_COOLDOWN // 2 if health_ratio < 0.3 else AI_ATTACK_COOLDOWN)

            # Fireball logic
            fireball_chance = 0.1 if distance > AI_ATTACK_RANGE else 0.03
            if self.fireball_cooldown_timer == 0 and random.random() < fireball_chance:
                fireball = True
                self.fireball_cooldown_timer = max(10, AI_ATTACK_COOLDOWN // 2 if health_ratio < 0.3 else AI_ATTACK_COOLDOWN)

            # Reset move cooldown
            self.move_cooldown = 4

        # Small chance to jump randomly, higher if low health
        if random.random() < (0.01 if health_ratio < 0.3 else 0.002):
            dy = -1

        return dx, dy, attack, fireball
