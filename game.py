import inspect

import pygame
import pygame_gui

from logger_config import logger
from pokemon.definedenemies import EnemyEnum
from pokemon.party import Party
from pokemon.pokemon import Pokemon
from pokemon.definedjobs import JobEnum
from audio.audio_manager import AudioManager

from sprites import *
from config import *

class Game:
    def __init__(self):
        self.log = logger.getChild(__name__)

        pygame.init()
        pygame.display.set_caption("Pokepy RPG")

        self.audio = AudioManager()

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.background = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock() # frame rate
        self.running = True
        self.paused = False
        self.pause_menu = None
        self.quit = False
        self.font = pygame.font.Font('C&CRedAlert.ttf', 72)

        self.manager = pygame_gui.UIManager((SCREEN_WIDTH, SCREEN_HEIGHT), theme_path="ui_style.json")

        self.character_spritesheet = Spritesheet('img/character_spritesheet.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')

        self.intro_background = pygame.image.load('img/introbackground.png')
        self.gameover_background = pygame.image.load('img/gameover.png')

        #Generate jobs
        self.jobs = []

        self.in_battle = False
        self.post_battle_cooldown = 0

    def toggle_pause_menu(self):
        if not self.paused:
            self.log.debug("Pausing game")
            self.audio.play_music('audio/music/Menu Screen.mp3')
            self.paused = True

            self.pause_menu = pygame_gui.elements.UIPanel(
                relative_rect=pygame.Rect((0, 0), (SCREEN_WIDTH, SCREEN_HEIGHT)),
                manager=self.manager,
                object_id="#pause_menu"
            )

            menu_options = ["Items", "Equip", "Save", "Back"]
            for idx, label in enumerate(menu_options):
                pygame_gui.elements.UIButton(
                    relative_rect=pygame.Rect((30, 30 + idx * 45), (150, 40)),
                    text=label,
                    manager=self.manager,
                    container=self.pause_menu,
                    object_id="#menu_button"
                )

            # Constants for layout
            panel_width = 400
            panel_height = 100
            panel_padding = 5
            start_x = 220
            start_y = 5

            # Loop through each member of the party
            for index, member in enumerate(self.party.members):
                offset_y = start_y + index * (panel_height + panel_padding)

                # Create a panel for each party member
                member_panel = pygame_gui.elements.UIPanel(
                    relative_rect=pygame.Rect((start_x, offset_y), (panel_width, panel_height)),
                    manager=self.manager,
                    container=self.pause_menu,
                    object_id=f"#member_panel_{index}"
                )

                # --- Sprite: UIImage on the left ---
                sprite_y = (panel_height - member.height) // 2  # Center vertically

                pygame_gui.elements.UIImage(
                    relative_rect=pygame.Rect((50, sprite_y), (member.width, member.height)),
                    image_surface=member.image,
                    manager=self.manager,
                    container=member_panel
                )

                # --- Stats: UILabel on the right ---
                stats_text = (
                    f"Name: {member.name}\n"
                    f"Job: {member.job.name}\n"
                    f"Level: {member.lvl}\n"
                    f"HP: {member.current_health} / {member.health_capacity}\n"
                )

                text_box_x = member.width + 100  # adjust to give space beside sprite
                text_box_width = panel_width

                pygame_gui.elements.UITextBox(
                    html_text=stats_text.replace("\n", "<br>"),
                    relative_rect=pygame.Rect((text_box_x, 0), (text_box_width, panel_height)),
                    manager=self.manager,
                    container=member_panel,
                    object_id="#stats_text"
                )
        else:
            self.log.debug("Unpausing game")
            self.audio.resume_previous_music()
            self.paused = False
            if self.pause_menu:
                self.pause_menu.kill()
                self.pause_menu = None

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

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    self.toggle_pause_menu()

            if event.type == pygame_gui.UI_BUTTON_PRESSED:
                if self.paused and event.ui_element.text == "Resume":
                    self.toggle_pause_menu()

            self.manager.process_events(event)

    def update(self):
        # game loop updates
        time_delta = self.clock.tick(FPS) / 1000.0
        self.manager.update(time_delta)

        if not self.paused:
            self.all_sprites.update()
            self.audio.update_music()
            if self.post_battle_cooldown > 0:
                self.post_battle_cooldown -= self.clock.get_time()

    def draw(self):
        # game loop draw
        self.screen.fill(BLACK) # clear screen
        self.all_sprites.draw(self.screen)
        self.manager.draw_ui(self.screen)
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
        self.audio.play_music('audio/music/Prelude.mp3')

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