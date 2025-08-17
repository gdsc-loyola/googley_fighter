import pygame
import sys
from config import SCREEN_WIDTH, SCREEN_HEIGHT, FPS
from config import RED_SPAWN, BLUE_SPAWN


class GameCanvas:
    def __init__(self, background_surface, fighters_group, red_fighter, blue_fighter):
        self.background = background_surface
        self.fighters = fighters_group
        self.red_fighter = red_fighter
        self.blue_fighter = blue_fighter

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

        # Reset positions
        self.red_fighter.rect.topleft = RED_SPAWN
        self.blue_fighter.rect.topleft = BLUE_SPAWN

        # Switch to the game state
        self.state = "menu"
        self.game_over = False
        self.paused = False

    def handle_events(self):
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False
            elif event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.running = False
                elif event.key == pygame.K_SPACE and self.state == "playing":
                    self.paused = not getattr(self, 'paused', False)
                elif event.key == pygame.K_r and self.game_over:
                    self.reset_game()

    def update(self):
        if not self.paused and not self.game_over:
            # Update fighters (they handle taking damage internally)
            self.red_fighter.update([self.blue_fighter])
            self.blue_fighter.update([self.red_fighter])

            # Check health
            if self.red_fighter.health <= 0 or self.blue_fighter.health <= 0:
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
            self.draw_timer()

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

        selected_mode = None

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
                    selected_mode = "singleplayer"
                    self.state = "playing"
                    menu_running = False
                elif mp_button_rect.collidepoint(mouse_pos):
                    selected_mode = "multiplayer"
                    self.state = "playing"
                    menu_running = False

            pygame.display.flip()
            self.clock.tick(FPS)

        return selected_mode

    def run(self):
        self.paused = False

        while self.running:
            self.handle_events()

            if not self.paused and not self.game_over and self.state == "playing":
                self.update()

            self.render()
            self.clock.tick(FPS)

        pygame.quit()
        sys.exit()
