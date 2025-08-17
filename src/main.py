import pygame
from PIL import Image
from sprite import create_fighters
from controls import Player1Controls, Player2Controls
from gamecanvas import GameCanvas
from config import SCREEN_WIDTH, SCREEN_HEIGHT

def load_avif_as_surface(path):
    from PIL import Image
    image = Image.open(path)
    image = image.resize((SCREEN_WIDTH, SCREEN_HEIGHT))
    return pygame.image.fromstring(image.tobytes(), image.size, image.mode)


def main():
    pygame.init()

    # Load background
    background_path = "assets/images/background.avif"
    background_surface = load_avif_as_surface(background_path)

    # Initialize fighters
    player1_controls = Player1Controls()
    player2_controls = Player2Controls()
    fighters, red_fighter, blue_fighter = create_fighters(player1_controls, player2_controls)

    # Create game canvas and run
    game = GameCanvas(background_surface, fighters, red_fighter, blue_fighter)
    game.run()


if __name__ == "__main__":
    main()
