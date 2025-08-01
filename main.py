import sys
import pygame

from pokemon.party import Party
from pokemon.pokemon import Pokemon
from pokemon.definedjobs import JobEnum

from sprites import *
from config import *
from battle import Battle

class Game:
    def __init__(self):
        pygame.init()
        pygame.display.set_caption("Pokepy RPG")

        self.screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
        self.clock = pygame.time.Clock() # frame rate
        self.running = True
        self.font = pygame.font.Font('ARCADECLASSIC.TTF', 32)

        self.character_spritesheet = Spritesheet('img/character_spritesheet.png')
        self.terrain_spritesheet = Spritesheet('img/terrain.png')
        self.enemy_spritesheet = Spritesheet('img/enemy.png')

        self.intro_background = pygame.image.load('./img/introbackground.png')
        self.gameover_background = pygame.image.load('./img/gameover.png')

        #Generate jobs
        self.jobs = []

        self.in_battle = False
        self.post_battle_cooldown = 0

    def create_tilemap(self):
        for row_index, row in enumerate(tilemap):
            for col_index, column in enumerate(row):
                Ground(self, col_index, row_index)
                if column == 'B':
                    Block(self, col_index, row_index)
                if column == 'E':
                    Enemy(self, 'Enemy', col_index, row_index)
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
        self.party.add_pokemon(Pokemon('bulbasaur', 28, 30, 35, 33, JobEnum.WARRIOR.value, None, None))
        self.party.add_pokemon(Pokemon('charmander', 318, 29, 38, 42, JobEnum.THIEF.value, None, None))

    def events(self):
        # game loop events(key presses, etc.)
        for event in pygame.event.get():
            # if game window is closed
            if event.type == pygame.QUIT:
                self.playing = False
                self.running = False

    def update(self):
        # game loop updates
        self.all_sprites.update()
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

    def encounter(self, enemy):
        battle = Battle(self, enemy, self.party)
        battle.run()
        self.in_battle = False
        self.post_battle_cooldown = 2000

    def show_item_menu(self):
        # similar loop for navigating item inventory
        pass

    def show_battle_menu(self):
        # similar loop for selecting abilities or attacks
        pass

    def game_over(self):
        text = self.font.render('Game Over', False, WHITE)
        text_rect = text.get_rect(center=(SCREEN_WIDTH/2, SCREEN_HEIGHT/2))

        restart_button = Button(10, SCREEN_HEIGHT - 60, 120, 50, WHITE, BLACK, 'Restart', self.font)

        # clear screen of sprites
        for sprite in self.all_sprites:
            sprite.kill()

        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if restart_button.is_pressed(mouse_pos, mouse_pressed):
                self.new()
                self.main()

            self.screen.blit(self.gameover_background, (0, 0))
            self.screen.blit(text, text_rect)
            self.screen.blit(restart_button.image, restart_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

    def intro_screen(self):
        intro = True

        title = self.font.render('Pokepy RPG', False, BLACK)
        title_rect = title.get_rect(x=10, y=10)

        play_button = Button(10, 50, 100, 50, WHITE, BLACK, 'Play', self.font)

        while intro:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    intro = False
                    self.running = False

            mouse_pos = pygame.mouse.get_pos()
            mouse_pressed = pygame.mouse.get_pressed()

            if play_button.is_pressed(mouse_pos, mouse_pressed):
                intro = False

            self.screen.blit(self.intro_background, (0, 0))
            self.screen.blit(title, title_rect)
            self.screen.blit(play_button.image, play_button.rect)
            self.clock.tick(FPS)
            pygame.display.update()

g = Game()
g.intro_screen()
g.new()
while g.running:
    g.main()
    g.game_over()

pygame.quit()
sys.exit()