# src/ai.py
"""
Googley Fighter - Basic AI for Singleplayer
"""

class SimpleAI:
    """
    Simple AI that follows the opponent horizontally and occasionally jumps.
    """

    def __init__(self, fighter, target_fighter, speed=3):
        self.fighter = fighter          # the AI-controlled Fighter
        self.target = target_fighter    # the opponent Fighter
        self.speed = speed
        self.jump_cooldown = 0          # frames until next jump allowed

    def get_input(self):
        """
        Returns (dx, dy) movement values for the AI.
        dx: -1 left, 1 right, 0 no horizontal movement
        dy: -1 up (jump), 0 no vertical movement
        """
        dx = 0
        dy = 0

        # Horizontal movement: move toward the target
        if self.fighter.rect.x < self.target.rect.x - 5:
            dx = 1
        elif self.fighter.rect.x > self.target.rect.x + 5:
            dx = -1

        # Simple jump logic: jump occasionally if near player
        if self.jump_cooldown > 0:
            self.jump_cooldown -= 1
        else:
            distance_x = abs(self.fighter.rect.x - self.target.rect.x)
            if distance_x < 100 and self.fighter.rect.bottom >= 500:  # on ground
                dy = -1  # jump
                self.jump_cooldown = 60  # wait 1 second before next jump

        return dx, dy
