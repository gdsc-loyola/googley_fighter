import pygame

class Fireball(pygame.sprite.Sprite):
    def __init__(self, x, y, direction, owner, speed=10, damage=15):
        super().__init__()
        self.image = pygame.Surface((32, 16), pygame.SRCALPHA)
        pygame.draw.ellipse(self.image, (255, 140, 0), [0, 0, 32, 16])
        self.rect = self.image.get_rect(center=(x, y))
        self.direction = direction 
        self.speed = speed
        self.owner = owner
        self.damage = damage

    def update(self, fighters_group):
        self.rect.x += self.speed * self.direction
        if self.rect.right < 0 or self.rect.left > 900:
            self.kill()
        for fighter in fighters_group:
            if fighter != self.owner and self.rect.colliderect(fighter.rect):
                fighter.take_damage(self.damage, from_left=(self.direction < 0))
                self.kill()