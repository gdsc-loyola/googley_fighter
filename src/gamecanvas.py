import pygame
import sys
import config
from PIL import Image
from sounds import BACKGROUND_SOUND
from sprite import create_fighters
from controls import Player1Controls, Player2Controls
from ai import AIControls
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
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

        # Fonts
        self.font = pygame.font.SysFont('Arial', 18, bold=True)
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
                elif event.key == pygame.K_SPACE and not self.game_over:
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
        # --- Use fighter.health instead of self.red_health/blue_health ---

        # Player 1 Health Bar (Top-Left)
        red_health_ratio = self.red_fighter.health / self.max_health
        red_bar_rect = pygame.Rect(
            self.health_bar_margin,
            self.health_bar_margin + 20,
            int(self.health_bar_width * red_health_ratio),
            self.health_bar_height
        )
        pygame.draw.rect(self.screen, (255, 0, 0), red_bar_rect)
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
        pygame.draw.rect(self.screen, (255, 0, 0), blue_bar_rect)
        pygame.draw.rect(
            self.screen, (255, 255, 255),
            pygame.Rect(SCREEN_WIDTH - self.health_bar_margin - self.health_bar_width, self.health_bar_margin + 20,
                        self.health_bar_width, self.health_bar_height), 2
        )

        # Labels
        label1 = self.font.render("PLAYER 1", True, self.label_color)
        label2 = self.font.render("PLAYER 2", True, self.label_color)
        self.screen.blit(label1, (self.health_bar_margin, self.health_bar_margin))
        self.screen.blit(label2, (SCREEN_WIDTH - self.health_bar_margin - label2.get_width(), self.health_bar_margin))

    def draw_cooldown_bars(self):
        """Draw attack cooldown bars for both fighters."""
        bar_width = 100
        bar_height = 8
        margin = 5

        # --- Player 1 Cooldown (under health bar, left) ---
        if self.red_fighter.attack_cooldown > 0:
            ratio = 1 - (self.red_fighter.attack_timer / self.red_fighter.attack_cooldown)
        else:
            ratio = 1
        color = (0, 255, 0) if ratio >= 1 else (255, 0, 0)  # green if ready, red if cooling down
        cooldown_rect = pygame.Rect(
            self.health_bar_margin,
            self.health_bar_margin + 20 + self.health_bar_height + margin,
            int(bar_width * ratio),
            bar_height
        )
        pygame.draw.rect(self.screen, color, cooldown_rect)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         pygame.Rect(self.health_bar_margin,
                                     self.health_bar_margin + 20 + self.health_bar_height + margin,
                                     bar_width, bar_height), 2)

        # --- Player 2 Cooldown (under health bar, right) ---
        if self.blue_fighter.attack_cooldown > 0:
            ratio = 1 - (self.blue_fighter.attack_timer / self.blue_fighter.attack_cooldown)
        else:
            ratio = 1
        color = (0, 255, 0) if ratio >= 1 else (255, 0, 0)
        cooldown_rect = pygame.Rect(
            SCREEN_WIDTH - self.health_bar_margin - bar_width,
            self.health_bar_margin + 20 + self.health_bar_height + margin,
            int(bar_width * ratio),
            bar_height
        )
        pygame.draw.rect(self.screen, color, cooldown_rect)
        pygame.draw.rect(self.screen, (255, 255, 255),
                         pygame.Rect(SCREEN_WIDTH - self.health_bar_margin - bar_width,
                                     self.health_bar_margin + 20 + self.health_bar_height + margin,
                                     bar_width, bar_height), 2)

    def draw_timer(self):
        remaining = max(0, int(self.time_remaining))
        minutes = remaining // 60
        seconds = remaining % 60
        time_text = f"{minutes:01}:{seconds:02}"
        timer_surface = self.font.render(time_text, True, (255, 255, 255))
        x = SCREEN_WIDTH // 2 - timer_surface.get_width() // 2
        y = self.health_bar_margin
        self.screen.blit(timer_surface, (x, y))

    def render(self):
        self.screen.blit(self.background, (0, 0))

        if self.state == "menu":
            self.start_menu()

        elif self.state == "playing":
            self.fighters.draw(self.screen)
            self.draw_health_bars()
            self.draw_cooldown_bars()
            self.draw_timer()

            # Show "FIGHT" for 0.5 sec at the start
        if self.fight_start_time:
            elapsed = (pygame.time.get_ticks() - self.fight_start_time) / 1000  # in seconds
            if elapsed < 0.5:
                fight_font = pygame.font.SysFont('Arial', 84, bold=True)
                fight_surface = fight_font.render("FIGHT!", True, (255, 255, 255))
                x = SCREEN_WIDTH // 2 - fight_surface.get_width() // 2
                y = SCREEN_HEIGHT // 2 - fight_surface.get_height() // 2
                self.screen.blit(fight_surface, (x, y))

        # Draw pause and game over messages
        if getattr(self, 'paused', False):
            pause_font = pygame.font.SysFont('Arial', 84, bold=True)
            pause_surface = pause_font.render("PAUSED", True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - pause_surface.get_width() // 2
            y = SCREEN_HEIGHT // 2 - pause_surface.get_height() // 2
            self.screen.blit(pause_surface, (x, y))

        # Draw Game Over message
        if self.game_over:
            over_font = pygame.font.SysFont('Arial', 84, bold=True)
            over_surface = over_font.render("GAME OVER", True, (255, 255, 255))
            x = SCREEN_WIDTH // 2 - over_surface.get_width() // 2
            y = SCREEN_HEIGHT // 2 - over_surface.get_height() // 2
            self.screen.blit(over_surface, (x, y))

            # Show "Press R to play again"
            hint_font = pygame.font.SysFont('Arial', 36, bold=True)
            hint_surface = hint_font.render("Press R to play again", True, (255, 255, 255))
            hx = SCREEN_WIDTH // 2 - hint_surface.get_width() // 2
            hy = y + over_surface.get_height() + 20
            self.screen.blit(hint_surface, (hx, hy))

        pygame.display.flip()

    def start_menu(self):
        menu_running = True
        button_font = pygame.font.SysFont("Arial", 36, bold=True)
        button_color = (50, 50, 50)
        button_hover = (100, 100, 100)
        button_width, button_height = 300, 60

        sp_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2 - 80, button_width, button_height)
        mp_button_rect = pygame.Rect(SCREEN_WIDTH//2 - button_width//2, SCREEN_HEIGHT//2 + 20, button_width, button_height)

        while menu_running:
            self.handle_events()
            mouse_pos = pygame.mouse.get_pos()
            mouse_click = pygame.mouse.get_pressed()[0]

            self.screen.blit(self.background, (0, 0))

            # Singleplayer button
            color = button_hover if sp_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, color, sp_button_rect)
            sp_text = button_font.render("Singleplayer", True, (255, 255, 255))
            self.screen.blit(sp_text, (sp_button_rect.centerx - sp_text.get_width()//2,
                                    sp_button_rect.centery - sp_text.get_height()//2))

            # Multiplayer button
            color = button_hover if mp_button_rect.collidepoint(mouse_pos) else button_color
            pygame.draw.rect(self.screen, color, mp_button_rect)
            mp_text = button_font.render("Multiplayer", True, (255, 255, 255))
            self.screen.blit(mp_text, (mp_button_rect.centerx - mp_text.get_width()//2,
                                    mp_button_rect.centery - mp_text.get_height()//2))

            if mouse_click:
                if sp_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "singleplayer"
                    self.state = "character_select"
                    BACKGROUND_SOUND.play(loops=-1)
                    menu_running = False
                elif mp_button_rect.collidepoint(mouse_pos):
                    self.selected_mode = "multiplayer"
                    self.state = "character_select"
                    BACKGROUND_SOUND.play(loops=-1)
                    menu_running = False

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
        font = pygame.font.SysFont("Arial", 36, bold=True)

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

        # 🔹 Load animated frames for previews
        previews = {
            "Googley": self.load_gif_frames("assets/images/googley/idle.gif", scale=(64, 64)),
            "Steve": self.load_gif_frames("assets/images/steve/idle.gif", scale=(64, 64)),
            "Alex": self.load_gif_frames("assets/images/alex/idle.gif", scale=(64, 64)),
        }

        # 🔹 Track animation state
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

            # Caption
            if self.selected_mode == "multiplayer" and turn == 2:
                caption = font.render("Player 2, choose your character", True, (255, 255, 255))
            else:
                caption = font.render("Player 1, choose your character", True, (255, 255, 255))

            self.screen.blit(caption, (SCREEN_WIDTH // 2 - caption.get_width() // 2, 100))

            # 🔹 Update animation every frame_delay ms
            frame_timer += self.clock.get_time()
            if frame_timer >= frame_delay:
                for char in characters:
                    frame_index[char] = (frame_index[char] + 1) % len(previews[char])
                frame_timer = 0

            # Draw character boxes
            for i, box in enumerate(boxes):
                color = (100, 100, 100) if box.collidepoint(mouse_pos) else (50, 50, 50)
                pygame.draw.rect(self.screen, color, box)
                pygame.draw.rect(self.screen, (255, 255, 255), box, 3)

                # 🔹 Draw animated frame
                char = characters[i]
                preview_img = previews[char][frame_index[char]]
                self.screen.blit(
                    preview_img,
                    (box.centerx - preview_img.get_width() // 2,
                    box.centery - preview_img.get_height() // 2),
                )

                # Label
                label_surface = self.font.render(char, True, (255, 255, 255))
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

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
