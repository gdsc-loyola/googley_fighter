# src/sprite.py
import pygame
from config import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y
from sounds import DAMAGE_SOUND, DEATH_SOUND
from PIL import Image


class Fighter(pygame.sprite.Sprite):
    """Fighter with GIF animation, health, damage + attack cooldown system."""
    def __init__(self, x, y, gif_right=None, gif_left=None,
                 damage_right_gif=None, damage_left_gif=None,
                 color=(255, 0, 0), controls=None, speed=5):
        super().__init__()
        self.controls = controls
        self.speed = speed
        self.rect = pygame.Rect(x, y, 64, 64)

        # Health system
        self.max_health = 100
        self.health = self.max_health

        # Damage system
        self.damage_cooldown = 30
        self.damage_timer = 0
        self.is_damaged = False
        self.damage_frames_right = []
        self.damage_frames_left = []
        self.active_damage_frames = []
        self.damage_frame_index = 0
        self.damage_frame_delay = 5
        self.damage_frame_count = 0
        self.damage_anim_timer = 0

        # Attack system
        self.is_attacking = False
        self.attack_damage = 10
        self.attack_range = 40
        self.attack_cooldown = 120
        self.attack_timer = 0

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

        self.image = pygame.Surface((64, 64))
        self.image.fill(color)

        # Load GIFs
        if gif_right:
            self.frames_right = self.load_gif(gif_right, scale=(64, 64))
        if gif_left:
            self.frames_left = self.load_gif(gif_left, scale=(64, 64))
        if damage_right_gif:
            self.damage_frames_right = self.load_gif(damage_right_gif, scale=(64, 64))
        if damage_left_gif:
            self.damage_frames_left = self.load_gif(damage_left_gif, scale=(64, 64))

        self.direction = "right"

    def load_gif(self, path, scale=None):
        pil_image = Image.open(path)
        frames = []
        try:
            while True:
                frame = pil_image.convert("RGBA")
                if scale:
                    frame = frame.resize(scale, Image.NEAREST)
                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                surface = pygame.image.fromstring(data, size, mode)
                frames.append(surface)
                pil_image.seek(pil_image.tell() + 1)
        except EOFError:
            pass
        return frames

    def take_damage(self, amount, from_left=True):
        """Apply damage and trigger correct damage animation orientation."""
        if self.damage_timer == 0:
            self.health -= amount
            if self.health < 0:
                self.health = 0

            # Select damage frames depending on attack direction
            self.active_damage_frames = self.damage_frames_right if from_left else self.damage_frames_left

            # Start damage state
            self.is_damaged = True
            self.damage_timer = self.damage_cooldown
            self.damage_anim_timer = len(self.active_damage_frames) * self.damage_frame_delay if self.active_damage_frames else 30
            self.damage_frame_index = 0
            self.damage_frame_count = 0

            DAMAGE_SOUND.play()
            if self.health == 0:
                DEATH_SOUND.play()

    def attack(self, others):
        """Attack if not on cooldown."""
        if self.attack_timer > 0:
            return

        self.is_attacking = True
        self.attack_timer = self.attack_cooldown

        for other in others:
            if self.direction == "right":
                attack_rect = pygame.Rect(self.rect.right, self.rect.top, self.attack_range, self.rect.height)
                if attack_rect.colliderect(other.rect):
                    # I am to the left of other → hit comes from left
                    other.take_damage(self.attack_damage, from_left=True)
            else:
                attack_rect = pygame.Rect(self.rect.left - self.attack_range, self.rect.top, self.attack_range, self.rect.height)
                if attack_rect.colliderect(other.rect):
                    # I am to the right of other → hit comes from right
                    other.take_damage(self.attack_damage, from_left=False)

    def move(self, dx, dy, others):
        if dx > 0:
            self.direction = "right"
        elif dx < 0:
            self.direction = "left"

        self.rect.x += dx * self.speed

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

        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH

    def jump(self):
        if not self.is_jumping and self.rect.bottom >= GROUND_Y:
            self.is_jumping = True
            self.vertical_speed = self.jump_speed

    def animate(self):
        if self.is_damaged and self.active_damage_frames:
            self.damage_frame_count += 1
            if self.damage_frame_count >= self.damage_frame_delay:
                self.damage_frame_count = 0
                self.damage_frame_index = (self.damage_frame_index + 1) % len(self.active_damage_frames)
            self.image = self.active_damage_frames[self.damage_frame_index]
            return

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
            if dy < 0:
                self.jump()
                dy = 0
            self.move(dx, dy, others)
            if attack:
                self.attack(others)

        if self.damage_timer > 0:
            self.damage_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.damage_anim_timer > 0:
            self.damage_anim_timer -= 1
        else:
            self.is_damaged = False

        self.animate()


def create_fighters(player1_choice, player2_choice, player1_controls, player2_controls):
    def get_paths(name):
        return (
            f"assets/images/{name}/{name}_right.gif",
            f"assets/images/{name}/{name}_left.gif",
            f"assets/images/{name}/damage_right.gif",
            f"assets/images/{name}/damage_left.gif"
        )

    p1_right, p1_left, p1_damage_r, p1_damage_l = get_paths(player1_choice)
    p2_right, p2_left, p2_damage_r, p2_damage_l = get_paths(player2_choice)

    red_fighter = Fighter(
        x=100, y=GROUND_Y,
        gif_right=p1_right, gif_left=p1_left,
        damage_right_gif=p1_damage_r, damage_left_gif=p1_damage_l,
        controls=player1_controls
    )

    blue_fighter = Fighter(
        x=600, y=GROUND_Y,
        gif_right=p2_right, gif_left=p2_left,
        damage_right_gif=p2_damage_r, damage_left_gif=p2_damage_l,
        controls=player2_controls
    )

    fighters = pygame.sprite.Group()
    fighters.add(red_fighter, blue_fighter)
    return fighters, red_fighter, blue_fighter
