import pygame
import pygame_gui
import random

from config import *

class Battle:
    def __init__(self, game, enemy, party):
        self.game = game
        self.enemy = enemy
        self.party = party

        self.manager = self.game.manager
        self.manager.clear_and_reset()  # Clear previous UI

        self.battle_background = pygame.image.load('./img/pokemon_battle_bg.png')

        # Turn order setup
        self.battlers = [self.enemy] + self.party.members
        for battler in self.battlers:
            battler.initiative = battler.agl + random.randint(0, 49)
        self.turn_order = sorted(self.battlers, key=lambda b: b.initiative, reverse=True)

        self.current_turn_index = 0
        self.active_battler = self.turn_order[self.current_turn_index]
        self.running = True

        self.state = 'action_select' # action_select target_select or enemy_turn
        self.target = None

        # Build the UI
        self._build_ui()

        self.enemy_turn_timer = 0

        # Ensure enemy starts if they win initiative
        if self.active_battler == self.enemy:
            self.state = "enemy_turn"
            self.enemy_turn_timer = 1000

    def _build_ui(self):
        # Panel for battle menu
        box_height = 150
        self.menu_panel = pygame_gui.elements.UIPanel(
            relative_rect=pygame.Rect(0, SCREEN_HEIGHT - box_height, SCREEN_WIDTH, box_height),
            starting_height=1,
            manager=self.manager
        )

        # Enemy name label and health bar
        self.enemy_label = pygame_gui.elements.UILabel(
            relative_rect=pygame.Rect(20, 10, 100, 30),
            text=self.enemy.name,
            manager=self.manager,
            container=self.menu_panel
        )
        self.enemy_health_bar = pygame_gui.elements.UIScreenSpaceHealthBar(
            relative_rect=pygame.Rect(20, 40, 100, 20),
            manager=self.manager,
            container=self.menu_panel,
            sprite_to_monitor=self.enemy
        )

        # Party member labels & health bars
        self.party_labels = []
        self.party_health_bars = []
        for i, pokemon in enumerate(self.party.members):
            lbl = pygame_gui.elements.UILabel(
                relative_rect=pygame.Rect(250, 10 + i * 50, 100, 30),
                text=pokemon.name,
                manager=self.manager,
                container=self.menu_panel
            )
            self.party_labels.append(lbl)

            hp_bar = pygame_gui.elements.UIScreenSpaceHealthBar(
                relative_rect=pygame.Rect(250, 40 + i * 50, 100, 20),
                manager=self.manager,
                container=self.menu_panel,
                sprite_to_monitor=pokemon
            )
            self.party_health_bars.append(hp_bar)

        # Action buttons - 2x2 grid on right side
        button_width = 100
        button_height = 30
        spacing_x = 10
        spacing_y = 10

        start_x = SCREEN_WIDTH - (button_width * 2 + spacing_x) - 20
        start_y = box_height / 2 - button_height - spacing_y

        self.attack_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, start_y, button_width, button_height),
            text='Attack',
            manager=self.manager,
            container=self.menu_panel
        )
        self.item_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + button_width + spacing_x, start_y, button_width, button_height),
            text='Item',
            manager=self.manager,
            container=self.menu_panel
        )
        self.equip_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x, start_y + button_height + spacing_y, button_width, button_height),
            text='Equip',
            manager=self.manager,
            container=self.menu_panel
        )
        self.run_button = pygame_gui.elements.UIButton(
            relative_rect=pygame.Rect(start_x + button_width + spacing_x, start_y + button_height + spacing_y,
                                      button_width, button_height),
            text='Run',
            manager=self.manager,
            container=self.menu_panel
        )

        # Highlight the starting active battler
        self.update_name_highlight()

    def update_name_highlight(self):
        # Enemy highlight
        if self.active_battler == self.enemy:
            self.enemy_label.change_object_id('#highlighted_text')
        else:
            self.enemy_label.change_object_id('')

        # Party highlights
        for i, pokemon in enumerate(self.party.members):
            if self.active_battler == pokemon:
                self.party_labels[i].change_object_id('#highlighted_text')
            else:
                self.party_labels[i].change_object_id('')

    def next_turn(self):
        self.current_turn_index = (self.current_turn_index + 1) % len(self.turn_order)
        self.active_battler = self.turn_order[self.current_turn_index]
        self.update_name_highlight()  # Refresh highlight each turn
        if self.active_battler == self.enemy:
            self.state = "enemy_turn"
            self.pick_enemy_target()
            self.enemy_turn_timer = 1000
        else:
            self.state = "action_select"

    def pick_enemy_target(self):
        """Choose a target for the enemy and highlight them."""
        if not self.party.members:
            return

        weights = [0.5, 0.25, 0.125, 0.125]
        available_targets = self.party.members[:4]
        weights = weights[:len(available_targets)]
        total = sum(weights)
        norm_weights = [w / total for w in weights]

        target = random.choices(available_targets, weights=norm_weights, k=1)[0]
        self.target = target

        print(f"{self.enemy.name} prepares to attack {target.name}!")

        # Highlight the chosen target's label
        for i, pokemon in enumerate(self.party.members):
            if pokemon == target:
                self.party_labels[i].change_object_id('#red_highlighted_text')

    def start_target_select(self):
        """Switch to target selection UI for the player."""
        self.state = 'target_select'
        self.target = self.enemy

        # Highlight enemy name in red
        self.enemy_label.change_object_id('#red_highlighted_text')
        print(f"{self.active_battler.name} is targeting {self.enemy.name} - Press Enter to confirm.")

    def perform_attack(self):
        """Resolve an attack on the chosen target."""
        if not self.target:
            return

        num_attacks = self.active_battler.get_number_of_attacks()
        for i in range(num_attacks):
            #TODO: animate attacks
            hit_rate = 168
            hit = random.randint(0, 200) <= min(hit_rate + self.active_battler.acc, 255) - self.target.eva
            if hit:
                print(f"{self.active_battler.name} hit {self.target.name}!")
                dmg = self.active_battler.str / 2
                self.target.current_health -= dmg
            else:
                print(f"{self.active_battler.name} missed {self.target.name}!")

        # Clear highlights from all labels
        for lbl in self.party_labels:
            lbl.change_object_id('')
        self.enemy_label.change_object_id('')

        self.target = None

    def draw_battle_screen(self):
        self.update_health_bar_colors()
        # Draw background
        self.game.screen.blit(self.battle_background, (0, 0))

        # Draw enemy sprite
        enemy_image = pygame.transform.flip(self.enemy.image, True, False)
        self.game.screen.blit(enemy_image, (50, SCREEN_HEIGHT // 2 - 32))

        # Draw party sprites
        for i, pokemon in enumerate(self.party.members):
            y = 80 + i * 70
            self.game.screen.blit(pokemon.image, (SCREEN_WIDTH - 80, y))

        # Draw UI
        self.manager.draw_ui(self.game.screen)
        pygame.display.update()

    def update_health_bar_colors(self):
        """Change health bar color based on HP percentage."""

        def set_bar_color(bar):
            hp_percent = bar.health_percentage
            if hp_percent > 0.5:
                bar.change_object_id("#green_bar")
            elif hp_percent > 0.25:
                bar.change_object_id("#yellow_bar")
            else:
                bar.change_object_id("#red_bar")

        # Enemy bar
        set_bar_color(self.enemy_health_bar)

        # Party bars
        for i, pokemon in enumerate(self.party.members):
            set_bar_color(self.party_health_bars[i])

    def handle_button_press(self, button):
        if self.state == 'action_select':
            if button == self.attack_button:
                self.start_target_select()
            elif button == self.item_button:
                print(f"{self.active_battler.name} chose Item")
                self.next_turn()
            elif button == self.equip_button:
                print(f"{self.active_battler.name} chose Equip")
                self.next_turn()
            elif button == self.run_button:
                # if self.active_battler.lck > self.active_battler.lvl + 15:
                if True:
                    print(f"{self.active_battler.name} ran from battle")
                    self.running = False
                else:
                    print(f"{self.active_battler.name} failed to run from battle")
                    self.next_turn()
        else:
            self.next_turn()

    def run(self):
        while self.running:
            time_delta = self.game.clock.tick(FPS) / 1000.0
            ms_delta = time_delta * 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.running = False
                    self.running = False

                elif event.type == pygame.KEYDOWN and self.state == 'target_select':
                    if event.key == pygame.K_RETURN:
                        self.perform_attack()
                        self.next_turn()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_press(event.ui_element)

                self.manager.process_events(event)

            # Handle delayed enemy turn
            if self.state == "enemy_turn" and self.enemy_turn_timer > 0:
                self.enemy_turn_timer -= ms_delta
                if self.enemy_turn_timer <= 0:
                    self.perform_attack()
                    self.next_turn()

            self.manager.update(time_delta)
            self.draw_battle_screen()
