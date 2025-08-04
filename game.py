import inspect

import pygame
import pygame_gui

from logger_config import logger
from pokemon.definedenemies import EnemyEnum
from pokemon.party import Party
from pokemon.pokemon import Pokemon
from pokemon.definedjobs import JobEnum

from sprites import *
from config import *

class Game:
    def __init__(self):
        self.log = logger.getChild(__name__)

        pygame.init()
        pygame.display.set_caption("Pokepy RPG")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock() # frame rate
        self.running = True
        self.quit = False
        self.font = pygame.font.Font('ARCADECLASSIC.TTF', 32)

        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="ui_style.json")

        self.character_spritesheet = Spritesheet('img/character_spritesheet.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')

        self.intro_background = pygame.image.load('./img/introbackground.png')
        self.gameover_background = pygame.image.load('./img/gameover.png')

        #Generate jobs
        self.jobs = []

        self.in_battle = False
        self.post_battle_cooldown = 0

    def play_music(self, track_path, loop=True, fadeout_ms=0, volume=1.0):
        """
        Play a music track with optional fadeout, loop, and volume control.
        Will not reload the same track if it's already playing.
        """
        self.log.debug("Playing " + str(track_path))
        # Avoid reloading the same track
        if getattr(self, "_current_track", None) == track_path:
            self.log.error("_current_track equals the track_path")
            return

        # Save the current track as the "previous" before switching
        if hasattr(self, "_current_track") and self._current_track != track_path:
            self._previous_track = self._current_track

        # If fadeout is requested, do it and schedule the new track
        if fadeout_ms > 0 and pygame.mixer.music.get_busy():
            self.log.debug("Fading out previous track")
            pygame.mixer.music.fadeout(fadeout_ms)

            # Store track info so we can start it later in update_music()
            self._pending_track = (track_path, loop, volume)
            self._fade_complete_time = pygame.time.get_ticks() + fadeout_ms
            return

        # Otherwise, just start immediately
        self._start_music(track_path, loop, volume)

    def _start_music(self, track_path, loop, volume):
        """Helper to actually load and play a track."""
        pygame.mixer.music.load(track_path)
        pygame.mixer.music.set_volume(volume)
        pygame.mixer.music.play(-1 if loop else 0)
        self._current_track = track_path
        self._pending_track = None
        self._fade_complete_time = None

    def update_music(self):
        """Call this in your main game loop to handle delayed music changes."""
        if hasattr(self, "_pending_track") and self._pending_track:
            if pygame.time.get_ticks() >= self._fade_complete_time:
                track_path, loop, volume = self._pending_track
                self._start_music(track_path, loop, volume)

    def resume_previous_music(self, fadeout_ms=0):
        """Resume the previous track if available."""
        if hasattr(self, "_previous_track"):
            print("Resuming _previous_track " + str(self._previous_track))
            self.play_music(self._previous_track, fadeout_ms=fadeout_ms)

    def create_tilemap(self):
        for row_index, row in enumerate(tilemap):
            for col_index, column in enumerate(row):
                Ground(self, col_index, row_index)
                if column == 'B':
                    Block(self, col_index, row_index)
                if column == 'E':
                    # TODO: implement randomized enemy generation
                    Enemy(self, 'Goblin', EnemyEnum.Goblin.value, col_index, row_index)
                if column == 'P':
                    Player(self, col_index, row_index)

    def new(self):
        # New game start
        self.playing = True

        self.all_sprites = pygame.sprite.LayeredUpdates()
        self.blocks = pygame.sprite.LayeredUpdates()
        self.enemies = pygame.sprite.LayeredUpdates()
        self.attacks = pygame.sprite.LayeredUpdates()

        self.create_tilemap()

        self.party = Party()
        self.party.add_pokemon(Pokemon('Bulbasaur', 28, 30, 35, 33, JobEnum.WARRIOR.value, None, None))
        self.party.add_pokemon(Pokemon('Charmander', 318, 29, 38, 42, JobEnum.THIEF.value, None, None))

        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="ui_style.json")

    def events(self):
        # game loop events(key presses, etc.)
        for event in pygame.event.get():
            # if game window is closed
            if event.type == pygame.QUIT:
                self.quit_game()

    def update(self):
        # game loop updates
        self.all_sprites.update()
        self.update_music()
        if self.post_battle_cooldown > 0:
            self.post_battle_cooldown -= self.clock.get_time()

    def draw(self):
        # game loop draw
        self.screen.fill(BLACK) # clear screen
        self.all_sprites.draw(self.screen)
        self.clock.tick(FPS)
        pygame.display.update()

    def main(self):
        # game loop
        while self.playing:
            self.events()
            self.update()
            self.draw()

    def quit_game(self):
        self.log.info("Quitting from " + str(inspect.stack()[1].function))
        self.running = False
        self.playing = False
        self.quit = True

    def game_over(self):
        self.manager.clear_and_reset()

        text = self.font.render('Game Over', False, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))

        restart_button_rect = pygame.Rect(0, 0, 200, 50)
        restart_button_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        restart_button = pygame_gui.elements.UIButton(
            relative_rect=restart_button_rect,
            text='Restart',
            manager=self.manager
        )

        self.waiting = True
        while self.waiting and self.running:
            time_delta = self.clock.tick(FPS) / 1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.quit_game()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == restart_button:
                        self.waiting = False
                        self.running = False

                self.manager.process_events(event)

            self.manager.update(time_delta)
            self.screen.blit(self.gameover_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.manager.draw_ui(self.screen)
            pygame.display.update()

    def intro_screen(self):
        self.play_music('audio/music/Prelude.mp3')

        intro = True
        self.manager.clear_and_reset()

        title = self.font.render('Pokepy RPG', False, BLACK)
        title_rect = title.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/4))

        play_button_rect = pygame.Rect(0, 0, 200 ,50)
        play_button_rect.center = (SCREEN_WIDTH / 2, SCREEN_HEIGHT / 2 + 50)
        play_button = pygame_gui.elements.UIButton(relative_rect=play_button_rect,
                                                    text='Play',
                                                    manager=self.manager)

        while intro:
            time_delta = self.clock.tick(FPS)/1000.0

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.quit_game()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    if event.ui_element == play_button:
                        intro = False

                self.manager.process_events(event)

            self.manager.update(time_delta)

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.manager.draw_ui(self.screen)
            pygame.display.update()