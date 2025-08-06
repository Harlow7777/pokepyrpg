import sys
import pygame

from game import Game
from config import *

def run_game():
    pygame.init()
    pygame.display.set_caption("Pokepy RPG")

    running = True
    while running:
        g = Game()

        g.intro_screen()

        g.audio.play_music('audio/music/Main Theme.mp3', fadeout_ms=FADEOUT_MS)

        g.new()

        while g.running:
            g.main()
            g.game_over()

        if g.quit:
            running = g.running

    pygame.quit()
    sys.exit()

if __name__ == "__main__":
    run_game()
