import pygame
from PIL import Image
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
    background_path = "assets/images/background.png"
    background_surface = load_avif_as_surface(background_path)

    # Create game canvas and run
    game = GameCanvas(background_surface, None, None, None)
    game.run()


if __name__ == "__main__":

    main()
