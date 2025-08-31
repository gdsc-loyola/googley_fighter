# src/sprite.py
import pygame
from . import config
from . import sounds
from . import fireball
from .config import SCREEN_WIDTH, SCREEN_HEIGHT, GROUND_Y
from .sounds import DAMAGE_SOUND, DEATH_SOUND
from .fireball import Fireball


class Fighter(pygame.sprite.Sprite):
    """Fighter with GIF animation, health, damage + attack cooldown system."""
    def __init__(self, x, y, gif_right=None, gif_left=None,
                 damage_right_gif=None, damage_left_gif=None,
                 color=(255, 0, 0), controls=None, speed=5):
        super().__init__()
        self.controls = controls
        self.speed = speed
        self.rect = pygame.Rect(x, y, 64, 64)
        self.fireballs = pygame.sprite.Group()

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
        self.stun_timer = 0

        # Fireball system
        self.is_shooting = False
        self.fireball_damage = 15
        self.fireball_cooldown = 300
        self.fireball_timer = 0

        # Jump system
        self.is_jumping = False
        self.jump_speed = -10
        self.gravity = 0.5
        self.vertical_speed = 0
        self.max_jump_height = GROUND_Y - 150

        # PNG frames
        self.frames_right = []
        self.frames_left = []
        self.current_frame = 0
        self.frame_delay = 5
        self.frame_count = 0

        self.image = pygame.Surface((64, 64))
        self.image.fill(color)

        # PNG sprite sheets
        if gif_right:
            self.frames_right = self.load_spritesheet(gif_right, scale=(64, 64))
        if gif_left:
            self.frames_left = self.load_spritesheet(gif_left, scale=(64, 64))
        if damage_right_gif:
            self.damage_frames_right = self.load_spritesheet(damage_right_gif, scale=(64, 64))
        if damage_left_gif:
            self.damage_frames_left = self.load_spritesheet(damage_left_gif, scale=(64, 64))

        # Set default image to first right frame if available
        if self.frames_right:
            self.image = self.frames_right[0]

        self.direction = "right"

    def load_spritesheet(self, path, frame_width=None, frame_height=None, scale=None):
        """Load a sprite sheet and slice into frames safely."""
        sheet = pygame.image.load(path).convert_alpha()
        frames = []
        sheet_width, sheet_height = sheet.get_size()

        # Auto-detect frame height if not given
        if frame_height is None:
            frame_height = sheet_height  # single row
        if frame_width is None:
            # Guess width by checking for common cases
            if sheet_width % sheet_height == 0:
                frame_width = sheet_height  # square frames
            else:
                frame_width = sheet_width  # single frame

        for y in range(0, sheet_height, frame_height):
            for x in range(0, sheet_width, frame_width):
                if x + frame_width > sheet_width or y + frame_height > sheet_height:
                    continue
                frame = sheet.subsurface(pygame.Rect(x, y, frame_width, frame_height))
                if scale:
                    frame = pygame.transform.scale(frame, scale)
                frames.append(frame)

        if not frames:
            print(f"[WARN] No frames loaded from {path}. "
                f"Tried {frame_width}x{frame_height} on {sheet_width}x{sheet_height}")
        else:
            print(f"[INFO] Loaded {len(frames)} frames from {path}")
        return frames

    def take_damage(self, amount, from_left=True):
        """Take damage and trigger damage animation if not on cooldown."""
        if self.damage_timer == 0:
            self.health -= amount
            if self.health < 0:
                self.health = 0

            # FIXED: play correct animation based on hit direction
            self.active_damage_frames = self.damage_frames_left if from_left else self.damage_frames_right

            self.is_damaged = True
            self.damage_timer = self.damage_cooldown
            self.damage_anim_timer = len(self.active_damage_frames) * self.damage_frame_delay if self.active_damage_frames else 30
            self.damage_frame_index = 0
            self.damage_frame_count = 0

            DAMAGE_SOUND.play()
            if self.health == 0:
                DEATH_SOUND.play()

            # --- Add stun here ---
            self.stun_timer = 1 * 60  # 1 second at 60 FPS

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

    def shoot_fireball(self):
        if self.fireball_timer > 0:
            return
        
        self.is_shooting = True
        self.fireball_timer = self.fireball_cooldown

        fb = Fireball(
            x=self.rect.centerx,
            y=self.rect.centery,
            direction=1 if self.direction == "right" else -1,
            owner=self,
            damage=self.fireball_damage
        )
        self.fireballs.add(fb)

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
        if self.stun_timer > 0:
            self.stun_timer -= 1
            # Still apply gravity/landing while stunned
            self.move(0, 0, others)  
        else:
            if self.controls:
                dx, dy, attack, fireballs = self.controls.get_input(self)
                if dy < 0:
                    self.jump()
                    dy = 0
                self.move(dx, dy, others)
                if attack:
                    self.attack(others)
                if fireballs:
                    self.shoot_fireball()

        if self.damage_timer > 0:
            self.damage_timer -= 1
        if self.attack_timer > 0:
            self.attack_timer -= 1
        if self.fireball_timer > 0:
            self.fireball_timer -= 1
        if self.damage_anim_timer > 0:
            self.damage_anim_timer -= 1
        else:
            self.is_damaged = False
        self.fireballs.update(others)

        self.animate()


def create_fighters(player1_choice, player2_choice, player1_controls, player2_controls):
    def get_paths(name):
        return (
            f"assets/images/{name}/{name}_right.png",
            f"assets/images/{name}/{name}_left.png",
            f"assets/images/{name}/damage_right.png",
            f"assets/images/{name}/damage_left.png"
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
