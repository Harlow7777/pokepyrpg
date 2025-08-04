import pygame
import pygame_gui
import random

from config import *

class Battle:
    def __init__(self, game, enemy, party):
        self.game = game
        self.enemy = enemy
        self.party = party

        self.manager = pygame_gui.UIManager(
            (SCREEN_WIDTH, SCREEN_HEIGHT),
            theme_path='ui_style.json'
        )
        self.manager.clear_and_reset()

        self.battle_background = pygame.image.load('./img/pokemon_battle_bg.png')

        # Turn order setup
        self.battlers = [self.enemy] + self.party.members
        for battler in self.battlers:
            battler.initiative = battler.agl + random.randint(0, 49)
        self.turn_order = sorted(self.battlers, key=lambda b: b.initiative, reverse=True)

        self.damage_popups = []  # stores damage/miss popups
        self.hit_effects = {} # {battler_obj: {"timer": ms_remaining, "blink": bool}}
        self.attack_animations = {}  # {battler_obj: {"timer": ms_remaining, "forward": bool}}

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
            self.pick_enemy_target()
            self.enemy_turn_timer = 1000

        self.update_button_states()

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

    def update_name_highlight(self):
        # Clear all highlights first
        self.enemy_label.change_object_id('')
        for lbl in self.party_labels:
            lbl.change_object_id('')
        # Highlight active battler if alive
        if self.active_battler == self.enemy and self.enemy.current_health > 0:
            self.enemy_label.change_object_id('#highlighted_text')
        else:
            for i, pokemon in enumerate(self.party.members):
                if self.active_battler == pokemon and pokemon.current_health > 0:
                    self.party_labels[i].change_object_id('#highlighted_text')

        # Flash target
        if self.target:
            flash_on = (pygame.time.get_ticks() // 250) % 2 == 0  # toggle every 250ms
            obj_id = '#red_highlighted_text' if flash_on else ''
            if self.enemy == self.target:
                self.enemy_label.change_object_id(obj_id)
            for i, pokemon in enumerate(self.party.members):
                if pokemon == self.target:
                    self.party_labels[i].change_object_id(obj_id)

    def next_turn(self):
        # Store current battler
        current_battler = self.active_battler

        # Remove KO'd battlers from turn order
        self.turn_order = [b for b in self.turn_order if b.current_health > 0]

        # Find the new index of the current battler (if still alive)
        if current_battler in self.turn_order:
            current_index = self.turn_order.index(current_battler)
            self.current_turn_index = (current_index + 1) % len(self.turn_order)
        else:
            # If current battler died (unlikely for enemy's own turn), just reset index
            self.current_turn_index = 0

        self.active_battler = self.turn_order[self.current_turn_index]

        if self.active_battler == self.enemy:
            self.state = "enemy_turn"
            self.pick_enemy_target()
            self.enemy_turn_timer = 1000
        else:
            self.state = "action_select"

        self.update_button_states()

    def pick_enemy_target(self):
        """Choose a target for the enemy and highlight them."""
        valid_targets = [p for p in self.party.members if p.current_health > 0]
        if not valid_targets:
            return

        weights = [0.5, 0.25, 0.125, 0.125]
        weights = weights[:len(valid_targets)]
        total = sum(weights)
        norm_weights = [w / total for w in weights]

        target = random.choices(valid_targets, weights=norm_weights, k=1)[0]
        self.target = target

        print(f"{self.enemy.name} prepares to attack {target.name}!")

    def start_target_select(self):
        """Switch to target selection UI for the player."""
        self.state = 'target_select'
        self.update_button_states()

        if self.enemy.current_health > 0:
            self.target = self.enemy
            print(f"{self.active_battler.name} is targeting {self.enemy.name} - Press Enter to confirm.")
        else:
            print("No valid targets.")
            self.next_turn()

    def perform_attack(self):
        """Resolve an attack on the chosen target."""
        if not self.target or self.target.current_health <= 0:
            print("Invalid target.")
            self.target = None
            return

        num_attacks = self.active_battler.get_number_of_attacks()

        for i in range(num_attacks):
            # Trigger slide animation for the attacker
            self.attack_animations[self.active_battler] = {
                "timer": 200,  # total animation duration (ms)
                "forward": True  # currently moving forward
            }

            # Calculate accuracy
            hit_rate = 168
            acc_check = random.randint(0, 200)
            hit = acc_check <= min(hit_rate + self.active_battler.acc, 255) - self.target.eva
            crit = acc_check == 0 or acc_check < self.active_battler.crit
            if hit:
                print(f"{self.active_battler.name} hit {self.target.name}!")

                # Trigger shake/blink effect
                self.hit_effects[self.target] = {
                    "timer": 600 if crit else 300,  # ms
                    "blink": True,
                    "shake": 8 if crit else 4,  # px
                    "blink_speed": 30 if crit else 50  # ms toggle
                }

                # Calculate damage
                dmg = self.active_battler.str / 2
                if crit:
                    dmg *= 2
                self.target.current_health -= dmg
                self.target.current_health = max(0, self.target.current_health)
                popup_text = str(int(dmg))
                popup_color = (255, 255, 0) if crit else (255, 0, 0)  # yellow for crits, red otherwise
            else:
                print(f"{self.active_battler.name} missed {self.target.name}!")
                popup_text = "Miss!"
                popup_color = (200, 200, 200)

            # Determine popup position based on target sprite
            if self.target == self.enemy:
                pos_x = 50 + self.enemy.image.get_width() // 2
                pos_y = SCREEN_HEIGHT // 2 - 32
            else:
                target_index = self.party.members.index(self.target)
                pos_x = SCREEN_WIDTH - 80 + self.target.image.get_width() // 2
                pos_y = (80 + target_index * 70) - 10

            # Store popup
            self.damage_popups.append({
                "text": popup_text,
                "color": popup_color,
                "x": pos_x,
                "y": pos_y,
                "alpha": 255,
                "lifetime": 1000,  # milliseconds
                "scale": 1.5,
                "crit": crit
            })

        self.target = None
        self.next_turn()

    def draw_battle_screen(self):
        self.update_health_bar_colors()
        # Draw background
        self.game.screen.blit(self.battle_background, (0, 0))

        # Draw enemy sprite with effects
        enemy_x, enemy_y = 50, SCREEN_HEIGHT // 2 - 32
        if self.enemy in self.attack_animations:
            if self.attack_animations[self.enemy]["forward"]:
                enemy_x += 10  # slide forward
            else:
                enemy_x -= 0  # could add slight recoil if wanted

        if self.enemy in self.hit_effects:
            effect = self.hit_effects[self.enemy]
            enemy_x += random.randint(-effect["shake"], effect["shake"])
            enemy_y += random.randint(-effect["shake"], effect["shake"])
            if int(pygame.time.get_ticks() / effect["blink_speed"]) % 2 == 0:
                self.game.screen.blit(pygame.transform.flip(self.enemy.image, True, False), (enemy_x, enemy_y))
        else:
            self.game.screen.blit(pygame.transform.flip(self.enemy.image, True, False), (enemy_x, enemy_y))

        # Draw party sprites with effects
        for i, pokemon in enumerate(self.party.members):
            y = 80 + i * 70
            x = SCREEN_WIDTH - 80
            sprite = pokemon.image
            if pokemon.current_health <= 0:
                # Convert to greyscale
                arr = pygame.surfarray.pixels3d(sprite)
                avg = arr.mean(axis=2, dtype=int)
                arr[:, :, 0] = avg
                arr[:, :, 1] = avg
                arr[:, :, 2] = avg
                del arr  # unlock surface

            if pokemon in self.attack_animations:
                if self.attack_animations[pokemon]["forward"]:
                    x -= 10  # slide toward enemy
                else:
                    x += 0
            if pokemon in self.hit_effects:
                effect = self.hit_effects[pokemon]
                x += random.randint(-effect["shake"], effect["shake"])
                y += random.randint(-effect["shake"], effect["shake"])
                if int(pygame.time.get_ticks() / effect["blink_speed"]) % 2 == 0:
                    self.game.screen.blit(pokemon.image, (x, y))
            else:
                self.game.screen.blit(pokemon.image, (x, y))

        # Draw damage popups
        for popup in self.damage_popups:
            font_size = 48 if popup["crit"] else 32
            font = pygame.font.Font(None, int(font_size * popup["scale"]))  # scale font size
            if popup["crit"]:
                font.set_bold(True)

            text_surf = font.render(popup["text"], True, popup["color"])
            text_surf.set_alpha(popup["alpha"])
            rect = text_surf.get_rect(center=(popup["x"], popup["y"]))
            self.game.screen.blit(text_surf, rect)

        # Draw UI
        self.manager.draw_ui(self.game.screen)
        pygame.display.update()

    def update_health_bar_colors(self):
        """Change health bar color based on HP percentage."""

        def set_bar_color(bar, hp, label):
            if hp <= 0:
                # KO: grey out sprite and label
                bar.change_object_id('#gray_bar')
                label.change_object_id('#gray_text')
            else:
                hp_percent = bar.health_percentage
                if hp_percent > 0.5:
                    bar.change_object_id('#green_bar')
                elif hp_percent > 0.25:
                    bar.change_object_id('#yellow_bar')
                else:
                    bar.change_object_id('#red_bar')

        # Enemy bar
        set_bar_color(self.enemy_health_bar, self.enemy.current_health, self.enemy_label)

        # Party bars
        for i, pokemon in enumerate(self.party.members):
            set_bar_color(self.party_health_bars[i], pokemon.current_health, self.party_labels[i])

    def update_button_states(self):
        """Enable action buttons only if it's the player's action_select phase."""
        is_enabled = (self.state == 'action_select')
        self.attack_button.enable() if is_enabled else self.attack_button.disable()
        self.item_button.enable() if is_enabled else self.item_button.disable()
        self.equip_button.enable() if is_enabled else self.equip_button.disable()
        self.run_button.enable() if is_enabled else self.run_button.disable()

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

    def display_defeat_message(self):
        # Clear lingering popups and effects
        self.damage_popups.clear()
        self.hit_effects.clear()
        self.attack_animations.clear()
        self.draw_battle_screen()

        # Create grey overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)  # transparency (0=transparent, 255=solid)
        overlay.fill((50, 50, 50))  # grey color
        self.game.screen.blit(overlay, (0, 0))

        font = pygame.font.Font('ARCADECLASSIC.TTF', 72)
        text_surf = font.render("Defeat", True, (255, 0, 0))
        rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2))
        self.game.screen.blit(text_surf, rect)

        pygame.display.update()
        pygame.time.delay(2000)  # wait 2 seconds before ending

    def display_victory_message(self):
        # Clear lingering popups and effects
        self.damage_popups.clear()
        self.hit_effects.clear()
        self.attack_animations.clear()
        self.draw_battle_screen()

        # Create grey overlay
        overlay = pygame.Surface((SCREEN_WIDTH, SCREEN_HEIGHT))
        overlay.set_alpha(180)  # transparency
        overlay.fill((50, 50, 50))
        self.game.screen.blit(overlay, (0, 0))

        font = pygame.font.Font('ARCADECLASSIC.TTF', 72)
        text_surf = font.render("Victory!", True, (255, 215, 0))  # gold color
        rect = text_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 - 40))
        self.game.screen.blit(text_surf, rect)

        # Award EXP to surviving party members
        exp_texts = []
        exp_amount = getattr(self.enemy, "exp")
        for p in self.party.members:
            if p.current_health > 0:
                p.exp += exp_amount
                exp_texts.append(f"{p.name} gained {exp_amount} EXP")
                print(f"{p.name} gained {exp_amount} EXP")
            else:
                print(f"{p.name} is KO'd and gained no EXP")

        small_font = pygame.font.Font('ARCADECLASSIC.TTF', 28)
        for i, line in enumerate(exp_texts):
            exp_surf = small_font.render(line, True, (255, 255, 255))
            exp_rect = exp_surf.get_rect(center=(SCREEN_WIDTH // 2, SCREEN_HEIGHT // 2 + 40 + i * 40))
            self.game.screen.blit(exp_surf, exp_rect)

        pygame.display.update()
        pygame.time.delay(2000)  # wait before returning

        self.running = False
        self.game.in_battle = False

    def run(self):
        while self.running:
            time_delta = self.game.clock.tick(FPS) / 1000.0
            ms_delta = time_delta * 1000

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.game.quit_game()

                elif event.type == pygame.KEYDOWN and self.state == 'target_select':
                    if event.key == pygame.K_RETURN:
                        self.perform_attack()

                if event.type == pygame_gui.UI_BUTTON_PRESSED:
                    self.handle_button_press(event.ui_element)

                self.manager.process_events(event)

            # Handle delayed enemy turn
            if self.state == "enemy_turn" and self.enemy_turn_timer > 0:
                self.enemy_turn_timer -= ms_delta
                if self.enemy_turn_timer <= 0:
                    self.perform_attack()

            # Update damage popups
            for popup in self.damage_popups[:]:
                popup["y"] -= 0.5  # move up slowly
                popup["lifetime"] -= time_delta * 1000
                popup["alpha"] = max(0, int(255 * (popup["lifetime"] / 1000)))

                # Bounce effect: shrink scale toward 1.0
                if popup["scale"] > 1.0:
                    popup["scale"] -= 0.05
                    if popup["scale"] < 1.0:
                        popup["scale"] = 1.0

                if popup["lifetime"] <= 0:
                    self.damage_popups.remove(popup)

            # Update hit effects
            for battler in list(self.hit_effects.keys()):
                self.hit_effects[battler]["timer"] -= time_delta * 1000
                if self.hit_effects[battler]["timer"] <= 0:
                    del self.hit_effects[battler]

            # Update attack animations
            for battler in list(self.attack_animations.keys()):
                anim = self.attack_animations[battler]
                anim["timer"] -= time_delta * 1000
                if anim["timer"] <= 100:
                    anim["forward"] = False  # move back after halfway
                if anim["timer"] <= 0:
                    del self.attack_animations[battler]

            self.manager.update(time_delta)
            self.update_name_highlight()
            self.draw_battle_screen()
            self.update_button_states()

            # Check defeat condition
            if all(p.current_health <= 0 for p in self.party.members):
                self.display_defeat_message()
                return 'defeat'

            # Check victory condition
            if self.enemy.current_health <= 0:
                self.display_victory_message()
                return 'victory'

        return 'escaped'

    def cleanup(self):
        """Ensure no lingering UI elements or battle state."""
        self.manager.clear_and_reset()
        self.damage_popups.clear()
        self.hit_effects.clear()
        self.attack_animations.clear()