import pygame
import random

from config import *
from sprites.button import Button

class Battle:
    def __init__(self, game, enemy, party):
        self.game = game
        self.enemy = enemy
        self.party = party

        self.battle_background = pygame.image.load('./img/pokemon_battle_bg.png')

        self.battlers = [self.enemy] + self.party.members

        # calculate initiative for each battler
        for battler in self.battlers:
            battler.initiative = battler.agl + random.randint(0, 49)
        self.turn_order = sorted(self.battlers, key=lambda b: b.initiative, reverse=True)
        print("Turn order: ")
        for battler in self.turn_order:
            print(str(battler.name))

        self.current_turn_index = 0
        self.active_battler = self.turn_order[self.current_turn_index]
        self.selected_index = 0

        self.screen = game.screen
        self.font = game.font
        self.state = 'main'  # or 'submenu'

        self.options = ['Attack', 'Item', 'Equip', 'Run']
        self.submenu_index = 0

        self.running = True
        self.in_submenu = False

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        self.active_battler = self.turn_order[self.current_turn_index]
        self.submenu_index = 0  # Reset selection
        self.in_submenu = False

    def draw_battle_screen(self):
        self.screen.blit(self.battle_background, (0, 0))

        # Draw enemy sprite on left
        enemy_image = pygame.transform.flip(self.enemy.image, True, False)
        self.screen.blit(enemy_image, (50, SCREEN_HEIGHT // 2 - 32))

        # Draw party sprites on right stacked vertically
        for i, pokemon in enumerate(self.party.members):
            y = 80 + i * 70
            self.screen.blit(pokemon.image, (SCREEN_WIDTH - 80, y))

        # Draw textbox
        box_height = 150
        box_y = SCREEN_HEIGHT - box_height
        pygame.draw.rect(self.screen, (30, 30, 30), (0, box_y, SCREEN_WIDTH, box_height))

        # Enemy name
        enemy_name_text = self.font.render(self.enemy.name, True, WHITE)
        self.screen.blit(enemy_name_text, (20, box_y + 20))

        # Party member names
        for i, pokemon in enumerate(self.party.members):
            name_color = (255, 255, 0) if i == self.current_turn_index else WHITE
            name_text = self.font.render(pokemon.name, True, name_color)
            self.screen.blit(name_text, (SCREEN_WIDTH // 3 + 40, box_y + 20 + i * 30))

        # Draw submenu if active
        if self.state == 'submenu':
            for i, option in enumerate(self.options):
                color = (0, 255, 0) if i == self.submenu_index else WHITE
                text = self.font.render(option, True, color)
                self.screen.blit(text, (SCREEN_WIDTH // 3 + 300, box_y + 20 + i * 30))

        pygame.display.update()

    def handle_input(self, event):
        if self.state == 'main':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.selected_index = (self.selected_index + 1) % len(self.turn_order)
                elif event.key == pygame.K_UP:
                    self.selected_index = (self.selected_index - 1) % len(self.turn_order)
                elif event.key == pygame.K_RETURN:
                    self.state = 'submenu'
        elif self.state == 'submenu':
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_DOWN:
                    self.submenu_index = (self.submenu_index + 1) % len(self.options)
                elif event.key == pygame.K_UP:
                    self.submenu_index = (self.submenu_index - 1) % len(self.options)
                elif event.key == pygame.K_RETURN:
                    selected = self.options[self.submenu_index]
                    print(f"{self.turn_order[self.selected_index].name} chose {selected}")
                    # Reset state for now
                    self.state = 'main'
                    self.handle_selection()

    def handle_selection(self):
        selected_option = self.options[self.submenu_index]

        if selected_option == 'Run':
            self.running = False  # Exit battle
        else:
            # You can expand each case later
            print(f"{self.active_battler.name} selected {selected_option}")

        self.next_turn()

    def run(self):
        while self.running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                self.handle_input(event)

            self.draw_battle_screen()
            self.game.clock.tick(FPS)