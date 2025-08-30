import os
import pygame
import sys
import config
from PIL import Image
from sounds import BACKGROUND_SOUND, BUTTON_SOUND
from sprite import create_fighters
from controls import Player1Controls, Player2Controls
from ai import AIControls
from fireball import Fireball
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS, GROUND_Y
from config import RED_SPAWN, BLUE_SPAWN


class GameCanvas:
    def __init__(self, background_surface, fighters_group, red_fighter, blue_fighter):
        self.background = background_surface
        self.fighters = fighters_group
        self.red_fighter = red_fighter
        self.blue_fighter = blue_fighter
        self.fight_start_time = None
        self.selected_mode = None

        # Initialize PyGame display
        font_path = os.path.join("assets", "fonts", "Minecraft.ttf")
        font_title_path = os.path.join("assets", "fonts", "MinecraftBold.otf")
        self.font =pygame.font.Font(font_path)
        self.font_title = pygame.font.Font(font_title_path)
        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        pygame.display.set_caption("Googley Fighter")
        self.clock = pygame.time.Clock()
        self.running = True

        # Health
        self.max_health = 100

        # Health bar settings
        self.health_bar_width = 200
        self.health_bar_height = 20
        self.health_bar_margin = 20

        # Timer settings
        self.time_remaining = 60  # seconds
        self.total_time = 60  # seconds
        self.start_ticks = pygame.time.get_ticks()  # starting time

        # Fonts: load Minecraft.ttf
        font_path = os.path.join("assets", "fonts", "Minecraft.ttf")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_path}")
    
        font_title_path = os.path.join("assets", "fonts", "MinecraftBold.otf")
        if not os.path.exists(font_path):
            raise FileNotFoundError(f"Font file not found: {font_title_path}")

        # Predefine commonly used fonts
        self.font_tiny = pygame.font.Font(font_path, 12)
        self.font_small = pygame.font.Font(font_path, 24)
        self.font_medium = pygame.font.Font(font_path, 36)
        self.font_title = pygame.font.Font(font_title_path, 72)
        
        self.label_color = (255, 255, 255)  # white for player labels
        self.state = "menu" # initial state
        self.game_over = False

    def reset_game(self):
        """Reset the game state after Game Over."""
        self.red_fighter.health = self.max_health
        self.blue_fighter.health = self.max_health
        self.red_fighter.damage_timer = 0
        self.blue_fighter.damage_timer = 0
        self.time_remaining = self.total_time
        self.fight_start_time = None

        # Reset positions
        self.red_fighter.rect.topleft = RED_SPAWN
        self.blue_fighter.rect.topleft = BLUE_SPAWN

        if self.selected_mode == "singleplayer":
            self.blue_fighter.controls = AIControls(self.blue_fighter, self.red_fighter, config)
        else:
            self.blue_fighter.controls = Player2Controls()

        # Switch to the game state
        self.state = "menu"
        self.game_over = False
        self.paused = False
        BACKGROUND_SOUND.stop()

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_p and not self.game_over:
                    self.paused = not getattr(self, 'paused', False)
                    if self.paused:
                        BACKGROUND_SOUND.stop()
                    else:
                        BACKGROUND_SOUND.play(loops=-1)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        if not self.paused and not self.game_over:
            # Update fighters (they handle taking damage internally)
            self.red_fighter.update([self.blue_fighter])
            self.blue_fighter.update([self.red_fighter])

            # Check health
            if self.red_fighter.health <= 0 or self.blue_fighter.health <= 0:
                if not self.game_over:
                    BACKGROUND_SOUND.stop()
                self.game_over = True

            # Decrease countdown timer
            self.time_remaining = max(0, self.time_remaining - 1 / FPS)

    def draw_health_bars(self):
        # Player 1 Health Bar (Top-Left)
        red_health_ratio = self.red_fighter.health / self.max_health
        red_bar_rect = pygame.Rect(
            self.health_bar_margin,
            self.health_bar_margin + 20,
            int(self.health_bar_width * red_health_ratio),
            self.health_bar_height
        )
        pygame.draw.rect(self.screen, (234, 67, 53), red_bar_rect)
        pygame.draw.rect(
            self.screen, (255, 255, 255),
            pygame.Rect(self.health_bar_margin, self.health_bar_margin + 20,
                        self.health_bar_width, self.health_bar_height), 2
        )

        # Player 2 Health Bar (Top-Right)
        blue_health_ratio = self.blue_fighter.health / self.max_health
        blue_bar_rect = pygame.Rect(
            SCREEN_WIDTH - self.health_bar_margin - int(self.health_bar_width * blue_health_ratio),
            self.health_bar_margin + 20,
            int(self.health_bar_width * blue_health_ratio),
            self.health_bar_height
        )
        pygame.draw.rect(self.screen, (66, 133, 244), blue_bar_rect)
        pygame.draw.rect(
            self.screen, (255, 255, 255),
            pygame.Rect(SCREEN_WIDTH - self.health_bar_margin - self.health_bar_width, self.health_bar_margin + 20,
                        self.health_bar_width, self.health_bar_height), 2
        )

        # Labels
        label1 = self.font_small.render("PLAYER 1", True, (234, 67, 53))
        label2 = self.font_small.render("PLAYER 2", True, (66, 133, 244))
        self.screen.blit(label1, (self.health_bar_margin, self.health_bar_margin))
        self.screen.blit(label2, (SCREEN_WIDTH - self.health_bar_margin - label2.get_width(), self.health_bar_margin))

    def draw_cooldown_bars(self):
        """Draw attack cooldown bars for both fighters (Hit + Shoot)."""
        bar_width = 100
        bar_height = 8
        margin = 5
        vertical_offset = 20  # shift bars + labels down

        # Helper function to draw one cooldown bar
        def draw_bar(x, y, ratio, full_color, label_text, align_right=False):
            color = full_color if ratio >= 1 else (234, 67, 53)
            label = self.font_tiny.render(label_text, True, self.label_color)

            if align_right:
                label_x = x + bar_width - label.get_width()
            else:
                label_x = x

            self.screen.blit(label, (label_x, y - label.get_height() - 2))

            cooldown_rect = pygame.Rect(x, y, int(bar_width * ratio), bar_height)
            pygame.draw.rect(self.screen, color, cooldown_rect)
            pygame.draw.rect(self.screen, (255, 255, 255),
                            pygame.Rect(x, y, bar_width, bar_height), 2)

        # =====================
        # Player 1 (left side)
        # =====================
        base_x = self.health_bar_margin
        base_y = self.health_bar_margin + 20 + self.health_bar_height + margin + vertical_offset

        # Hit bar
        ratio = 1 - (self.red_fighter.attack_timer / self.red_fighter.attack_cooldown) if self.red_fighter.attack_cooldown > 0 else 1
        draw_bar(base_x, base_y, ratio, (52, 168, 83), "Hit", align_right=False)

        # Shoot bar (10px lower than before)
        ratio = 1 - (self.red_fighter.fireball_timer / self.red_fighter.fireball_cooldown) if self.red_fighter.fireball_cooldown > 0 else 1
        draw_bar(base_x, base_y + bar_height + margin + 15, ratio, (255, 165, 0), "Shoot", align_right=False)

        # =====================
        # Player 2 (right side)
        # =====================
        base_x = SCREEN_WIDTH - self.health_bar_margin - bar_width
        base_y = self.health_bar_margin + 20 + self.health_bar_height + margin + vertical_offset

        # Hit bar
        ratio = 1 - (self.blue_fighter.attack_timer / self.blue_fighter.attack_cooldown) if self.blue_fighter.attack_cooldown > 0 else 1
        draw_bar(base_x, base_y, ratio, (52, 168, 83), "Hit", align_right=True)

        # Shoot bar (10px lower than before)
        ratio = 1 - (self.blue_fighter.fireball_timer / self.blue_fighter.fireball_cooldown) if self.blue_fighter.fireball_cooldown > 0 else 1
        draw_bar(base_x, base_y + bar_height + margin + 15, ratio, (255, 165, 0), "Shoot", align_right=True)

    def draw_timer(self):
        remaining = max(0, int(self.time_remaining))
        minutes = remaining // 60
        seconds = remaining % 60
        time_text = f"{minutes:01}:{seconds:02}"
        timer_surface = self.font_small.render(time_text, True, (255, 255, 255))
        x = SCREEN_WIDTH // 2 - timer_surface.get_width() // 2
        y = self.health_bar_margin
        self.screen.blit(timer_surface, (x, y))

    def draw_fighter_labels(self):
        """Draw floating labels under each fighter sprite that follow them."""
        # Player 1 label (red fighter)
        red_label = self.font_tiny.render("PLAYER 1", True, (234, 67, 53))
        red_x = self.red_fighter.rect.centerx - red_label.get_width() // 2
        red_y = self.red_fighter.rect.bottom + 5  # 5px below sprite
        self.screen.blit(red_label, (red_x, red_y))

        # Player 2 label (blue fighter)
        blue_label = self.font_tiny.render("PLAYER 2", True, (0, 0, 255))
        blue_x = self.blue_fighter.rect.centerx - blue_label.get_width() // 2
        blue_y = self.blue_fighter.rect.bottom + 5
        self.screen.blit(blue_label, (blue_x, blue_y))

    def render(self):
        self.screen.blit(self.background, (0, 0))

        if self.state == "menu":
            self.start_menu()

        elif self.state == "playing":
            self.fighters.draw(self.screen)
            for fighter in [self.red_fighter, self.blue_fighter]:
                fighter.fireballs.draw(self.screen)
            self.draw_health_bars()
            self.draw_cooldown_bars()
            self.draw_timer()
            self.draw_fighter_labels()

        # Show "FIGHT" for 0.5 sec at the start
        if self.fight_start_time:
            elapsed = (pygame.time.get_ticks() - self.fight_start_time) / 1000
            if elapsed < 0.5:
                fight_surface = self.font_title.render("FIGHT!", True, (255, 255, 255))
                self.screen.blit(fight_surface, (SCREEN_WIDTH // 2 - fight_surface.get_width() // 2,
                                                 SCREEN_HEIGHT // 2 - fight_surface.get_height() // 2))

        # Draw pause and game over messages
        if self.paused:
            # PAUSED message
            pause_surface = self.font_title.render("PAUSED", True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - pause_surface.get_width() // 2
            y = SCREEN_HEIGHT // 4 - pause_surface.get_height() // 2
            self.screen.blit(pause_surface, (x, y))

            # --- Pause menu buttons ---
            button_color = (50, 50, 50, 180)
            button_hover = (100, 100, 100, 220)
            button_width, button_height = 250, 60
            spacing = 20

            buttons = {
                "CONTINUE": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2,
                                        y + pause_surface.get_height() + 40,
                                        button_width, button_height),
                "RESTART": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2,
                                    y + pause_surface.get_height() + 40 + (button_height + spacing),
                                    button_width, button_height),
                "MENU": pygame.Rect(SCREEN_WIDTH // 2 - button_width // 2,
                                    y + pause_surface.get_height() + 40 + 2 * (button_height + spacing),
                                    button_width, button_height)
            }

            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]

            for label, rect in buttons.items():
                # Transparent button surface
                temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                color = button_hover if rect.collidepoint(mouse_pos) else button_color
                temp_surf.fill(color)
                self.screen.blit(temp_surf, rect.topleft)

                # Draw button text using custom font
                text_surf = self.font_medium.render(label, True, (255, 255, 255))
                self.screen.blit(text_surf, (rect.centerx - text_surf.get_width() // 2,
                                            rect.centery - text_surf.get_height() // 2))

                # Handle button clicks
                if mouse_click and rect.collidepoint(mouse_pos):
                    BUTTON_SOUND.play()
                    if label == "CONTINUE":
                        self.paused = False
                        BACKGROUND_SOUND.play(loops=-1)
                    elif label == "RESTART":
                        self.reset_game()
                        self.state = "playing"
                        self.start_fight()
                    elif label == "MENU":
                        self.reset_game()
                        self.state = "menu"

        # --- Game Over message ---
        if self.game_over:
            # GAME OVER title
            over_surface = self.font_title.render("GAME OVER", True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - over_surface.get_width() // 2
            y = SCREEN_HEIGHT // 3 - over_surface.get_height() // 2
            self.screen.blit(over_surface, (x, y))

            # Press R hint
            hint_surface = self.font_medium.render("Press R to play again", True, (255, 255, 255))
            hx = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
            hy = y + over_surface.get_height() + 20
            self.screen.blit(hint_surface, (hx, hy))

        pygame.display.flip()

    def start_menu(self):
        menu_running = True
        button_color = (50, 50, 50, 180)
        button_hover = (100, 100, 100, 220)
        button_width, button_height = 300, 60

        sp_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2 - 70, button_width, button_height)
        mp_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2, button_width, button_height)
        inst_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2 + 70, button_width, button_height)
        quit_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2 + 140, button_width, button_height)

        if not pygame.mixer.get_busy():
            BACKGROUND_SOUND.play(loops=-1)

        # Load GIF frames for menu characters
        googley_frames = self.load_gif_frames("assets/images/googley/googley_right.gif", scale=(64, 64))
        alex_frames = self.load_gif_frames("assets/images/alex/alex_right.gif", scale=(64, 64))
        steve_frames = self.load_gif_frames("assets/images/steve/steve_right.gif", scale=(64, 64))
        frame_index = {"Googley": 0, "Alex": 0, "Steve": 0}
        frame_timer = 0
        frame_delay = 150  # ms per frame

        positions = {
            "Googley": [SCREEN_WIDTH//4, config.GROUND_Y],
            "Alex": [SCREEN_WIDTH*3//4, config.GROUND_Y],
            "Steve": [SCREEN_WIDTH//2, config.GROUND_Y]
        }
        velocities = {
            "Googley": [1, 0],
            "Alex": [-0.8, 0],
            "Steve": [1.2, 0]
        }

        while menu_running:
            self.handle_events()
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]

            self.screen.blit(self.background, (0, 0))

            # --- Draw title using .ttf ---
            title_surface = self.font_title.render("GOOGLEY FIGHTER", True, (255, 255, 255))
            title_x = SCREEN_WIDTH // 2 - title_surface.get_width() // 2
            title_y = 100
            subtitle_surface = self.font_medium.render("RecWeek 2025 Edition", True, (255, 255, 255))
            subtitle_x = SCREEN_WIDTH // 2 - subtitle_surface.get_width() // 2
            subtitle_y = 175
            self.screen.blit(title_surface, (title_x, title_y))
            self.screen.blit(subtitle_surface, (subtitle_x, subtitle_y))

            # --- Animate menu GIFs first (sprites in the back) ---
            frame_timer += self.clock.get_time()
            if frame_timer >= frame_delay:
                for char in frame_index:
                    frames = {"Googley": googley_frames, "Alex": alex_frames, "Steve": steve_frames}[char]
                    frame_index[char] = (frame_index[char] + 1) % len(frames)
                frame_timer = 0

            for char, pos in positions.items():
                vel = velocities[char]
                pos[0] += vel[0]

                frame = {"Googley": googley_frames, "Alex": alex_frames, "Steve": steve_frames}[char][frame_index[char]]
                w, h = frame.get_width(), frame.get_height()
                pos[1] = config.GROUND_Y - h//2

                if pos[0] - w//2 <= 0 or pos[0] + w//2 >= SCREEN_WIDTH:
                    vel[0] *= -1

                img_to_draw = pygame.transform.flip(frame, vel[0] < 0, False)
                self.screen.blit(img_to_draw, (pos[0] - w//2, pos[1] - h//2))

            # --- Draw buttons AFTER sprites (buttons in front) ---
            for rect, text in [(sp_button_rect, "Singleplayer"),
                            (mp_button_rect, "Multiplayer"),
                            (inst_button_rect, "Instructions"),
                            (quit_button_rect, "Quit")]:
                temp_surf = pygame.Surface((rect.width, rect.height), pygame.SRCALPHA)
                if rect == quit_button_rect and rect.collidepoint(mouse_pos):
                    color = (234, 67, 53, 220)  # red hover color for quit
                else:
                    color = button_hover if rect.collidepoint(mouse_pos) else button_color
                
                temp_surf.fill(color)
                self.screen.blit(temp_surf, rect.topleft)

                text_surf = self.font_medium.render(text, True, (255, 255, 255))
                self.screen.blit(text_surf, (rect.centerx - text_surf.get_width()//2,
                                            rect.centery - text_surf.get_height()//2))

            # --- Handle button clicks ---
            if mouse_click:
                if sp_button_rect.collidepoint(mouse_pos):
                    BUTTON_SOUND.play()
                    self.selected_mode = "singleplayer"
                    self.state = "character_select"
                    menu_running = False
                elif mp_button_rect.collidepoint(mouse_pos):
                    BUTTON_SOUND.play()
                    self.selected_mode = "multiplayer"
                    self.state = "character_select"
                    BACKGROUND_SOUND.play(loops=-1)
                    menu_running = False
                elif inst_button_rect.collidepoint(mouse_pos):
                    self.state = "instructions"
                    menu_running = False
                elif quit_button_rect.collidepoint(mouse_pos):
                    pygame.quit()
                    sys.exit()

            pygame.display.flip()
            self.clock.tick(FPS)

    def instructions(self):
        running = True
        lines = [
            "INSTRUCTIONS",
            "Player 1: WASD to move, SPACE to attack, F to shoot",
            "Player 2: Arrow keys to move, R_SHIFT to attack, H to shoot",
            "Press P to pause the game",
            "Reduce opponent health to 0 to win",
            "",
            "Click anywhere on the screen to return to the menu",
        ]

        while running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONDOWN or (event.type == pygame.KEYDOWN and event.key == pygame.K_ESCAPE):
                    self.state = "menu"
                    running = False

            self.screen.blit(self.background, (0, 0))

            # Render instruction lines
            for i, line in enumerate(lines):
                if i == 0:  # Title
                    text_surf = self.font_title.render(line, True, (255, 255, 255))
                    y_pos = 125
                else:
                    text_surf = self.font_small.render(line, True, (255, 255, 255))
                    y_pos = 175 + i * 40
                x_pos = SCREEN_WIDTH // 2 - text_surf.get_width() // 2
                self.screen.blit(text_surf, (x_pos, y_pos))

            pygame.display.flip()
            self.clock.tick(FPS)

    def load_gif_frames(self, path, scale=None):
        """Load GIF frames as a list of PyGame surfaces."""
        pil_img = Image.open(path)
        frames = []
        palette = pil_img.getpalette()  # store palette for reuse

        try:
            while True:
                frame = pil_img.convert("RGBA")  # ensure proper format
                if scale:
                    frame = frame.resize(scale, Image.NEAREST)

                # Only apply palette if image mode is "P"
                if pil_img.mode == "P" and palette:
                    pil_img.putpalette(palette)

                mode = frame.mode
                size = frame.size
                data = frame.tobytes()
                surface = pygame.image.fromstring(data, size, mode)
                frames.append(surface)
                pil_img.seek(pil_img.tell() + 1)
        except EOFError:
            pass

        return frames

    def start_fight(self):
        """Initialize fighters after character selection."""
        player1_controls = Player1Controls()

        if self.selected_mode == "singleplayer":
            player2_controls = Player2Controls()  # still give dummy, AI replaces below
        else:
            player2_controls = Player2Controls()

        # Create fighters
        self.fighters, self.red_fighter, self.blue_fighter = create_fighters(
            self.player1_choice,
            self.player2_choice,
            player1_controls,
            player2_controls
        )

        # Apply AI if singleplayer
        if self.selected_mode == "singleplayer":
            self.blue_fighter.controls = AIControls(self.blue_fighter, self.red_fighter, config)

        self.state = "playing"
        self.fight_start_time = pygame.time.get_ticks()
        BACKGROUND_SOUND.play(loops=-1)

    def character_select(self):
        """Show character selection screen for singleplayer or multiplayer."""
        choosing = True

        box_size = 120
        spacing = 150
        num_boxes = 3
        total_width = num_boxes * box_size + (num_boxes - 1) * spacing
        start_x = (SCREEN_WIDTH - total_width) // 2
        y = SCREEN_HEIGHT // 2 - box_size // 2

        boxes = [
            pygame.Rect(start_x + i * (box_size + spacing), y, box_size, box_size)
            for i in range(num_boxes)
        ]

        characters = ["Googley", "Steve", "Alex"]

        # Load animated frames for previews
        previews = {
            "Googley": self.load_gif_frames("assets/images/googley/idle.gif", scale=(64, 64)),
            "Steve": self.load_gif_frames("assets/images/steve/idle.gif", scale=(64, 64)),
            "Alex": self.load_gif_frames("assets/images/alex/idle.gif", scale=(64, 64)),
        }

        # Track animation state
        frame_index = {char: 0 for char in characters}
        frame_timer = 0
        frame_delay = 150  # ms per frame (adjust for speed)

        turn = 1  # 1 = player1 choosing, 2 = player2 choosing (multiplayer only)

        while choosing:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()

                if event.type == pygame.MOUSEBUTTONDOWN and event.button == 1:
                    BUTTON_SOUND.play()
                    for i, box in enumerate(boxes):
                        if box.collidepoint(event.pos):
                            if self.selected_mode == "singleplayer":
                                self.player1_choice = characters[i]
                                self.player2_choice = "Googley"  # default AI opponent
                                choosing = False
                            elif self.selected_mode == "multiplayer":
                                if turn == 1:
                                    self.player1_choice = characters[i]
                                    turn = 2
                                else:
                                    if characters[i] == self.player1_choice:
                                        continue
                                    self.player2_choice = characters[i]
                                    choosing = False

            self.handle_events()
            mouse_pos = pygame.mouse.get_pos()

            self.screen.blit(self.background, (0, 0))

            # Caption using large font
            if self.selected_mode == "multiplayer" and turn == 2:
                caption_surface = self.font_medium.render("Player 2, choose your character", True, (255, 255, 255))
            else:
                caption_surface = self.font_medium.render("Player 1, choose your character", True, (255, 255, 255))

            self.screen.blit(caption_surface, (SCREEN_WIDTH // 2 - caption_surface.get_width() // 2, 160))

            # Update animation every frame_delay ms
            frame_timer += self.clock.get_time()
            if frame_timer >= frame_delay:
                for char in characters:
                    frame_index[char] = (frame_index[char] + 1) % len(previews[char])
                frame_timer = 0

            # Draw character boxes with transparency (no borders)
            for i, box in enumerate(boxes):
                temp_surf = pygame.Surface((box.width, box.height), pygame.SRCALPHA)
                hover = box.collidepoint(mouse_pos)
                color = (100, 100, 100, 180) if hover else (50, 50, 50, 150)
                temp_surf.fill(color)
                self.screen.blit(temp_surf, box.topleft)

                # Draw animated frame
                char = characters[i]
                preview_img = previews[char][frame_index[char]]
                self.screen.blit(
                    preview_img,
                    (box.centerx - preview_img.get_width() // 2,
                    box.centery - preview_img.get_height() // 2)
                )

                # Draw character label using medium font
                label_surface = self.font_medium.render(char, True, (255, 255, 255))
                self.screen.blit(label_surface, (box.centerx - label_surface.get_width() // 2, box.bottom + 10))

            pygame.display.flip()
            self.clock.tick(FPS)

        # After selection, start fight
        self.start_fight()

    def run(self):
        self.paused = False

        while self.running:
            self.handle_events()

            if self.state == "menu":
                self.start_menu()
            elif self.state == "character_select":
                self.character_select()
            elif not self.paused and not self.game_over and self.state == "playing":
                self.update()
            elif self.state == "instructions":
                self.instructions()

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()