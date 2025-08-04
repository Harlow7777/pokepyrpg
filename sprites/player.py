import math
import pygame

from battle import Battle
from config import *
from logger_config import logger

class Player(pygame.sprite.Sprite):
    def __init__(self, game, x, y):
        self.log = logger.getChild(__name__)

        self.game = game
        self._layer = PLAYER_LAYER
        self.groups = self.game.all_sprites
        pygame.sprite.Sprite.__init__(self, self.groups)

        sprite_width = 19
        sprite_height = 28
        self.x = x * sprite_width
        self.y = y * sprite_height
        self.width = sprite_width
        self.height = sprite_height

        self.x_change = 0
        self.y_change = 0

        self.facing = 'down'
        self.animation_loop = 1

        # draw sprite
        self.image = self.game.character_spritesheet.get_sprite(3, 2, self.width, self.height, WHITE)

        self.rect = self.image.get_rect()
        self.rect.centerx = SCREEN_WIDTH // 2
        self.rect.centery = SCREEN_HEIGHT // 2

        self.down_animations = [self.game.character_spritesheet.get_sprite(32, 52, self.width, self.height, WHITE),
                           self.game.character_spritesheet.get_sprite(10, 52, self.width, self.height, WHITE),
                           self.game.character_spritesheet.get_sprite(54, 52, self.width, self.height, WHITE)]

        self.up_animations = [self.game.character_spritesheet.get_sprite(31, 158, self.width, self.height, WHITE),
                         self.game.character_spritesheet.get_sprite(9, 158, self.width, self.height, WHITE),
                         self.game.character_spritesheet.get_sprite(53, 158, self.width, self.height, WHITE)]

        self.left_animations = [self.game.character_spritesheet.get_sprite(30, 87, self.width, self.height, WHITE),
                           self.game.character_spritesheet.get_sprite(9, 87, self.width, self.height, WHITE),
                           self.game.character_spritesheet.get_sprite(52, 87, self.width, self.height, WHITE)]

        self.right_animations = [self.game.character_spritesheet.get_sprite(32, 123, self.width, self.height, WHITE),
                            self.game.character_spritesheet.get_sprite(10, 123, self.width, self.height, WHITE),
                            self.game.character_spritesheet.get_sprite(53, 123, self.width, self.height, WHITE)]

    def update(self):
        old_x = self.rect.x
        old_y = self.rect.y

        self.movement()
        self.animate()
        self.collide_enemy()

        # Apply player movement
        self.rect.x += self.x_change
        self.collide_blocks('x')

        self.rect.y += self.y_change
        self.collide_blocks('y')

        # Determine if actual movement occurred
        moved_x = self.rect.x - old_x
        moved_y = self.rect.y - old_y

        # Move camera only if there was actual movement
        if moved_x != 0 or moved_y != 0:
            for sprite in self.game.all_sprites:
                sprite.rect.x -= moved_x
                sprite.rect.y -= moved_y

        self.x_change = 0
        self.y_change = 0

    def movement(self):
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT]:
            self.x_change -= PLAYER_SPEED
            self.facing = 'left'
        if keys[pygame.K_RIGHT]:
            self.x_change += PLAYER_SPEED
            self.facing = 'right'
        if keys[pygame.K_UP]:
            self.y_change -= PLAYER_SPEED
            self.facing = 'up'
        if keys[pygame.K_DOWN]:
            self.y_change += PLAYER_SPEED
            self.facing = 'down'

    def collide_enemy(self):
        if self.game.in_battle or self.game.post_battle_cooldown > 0:
            return

        hits = pygame.sprite.spritecollide(self, self.game.enemies, False)
        if hits:
            self.game.in_battle = True
            enemy = hits[0]

            # Run battle
            battle = Battle(self.game, enemy, self.game.party)
            result = battle.run()
            battle.cleanup()
            self.log.debug("Battle result " + str(result))
            if result == "victory":
                # Survived — go back to map and remove enemy sprite
                enemy.kill()
                self.game.in_battle = False
                self.game.draw()
                return
            elif result == "escape":
                self.game.in_battle = False
                self.game.post_battle_cooldown = 2000
                self.game.draw()
                return
            elif result == "defeat":
                # Player was defeated — trigger game over
                self.game.playing = False
                return

    def collide_blocks(self, direction):
        # check and handle collisions
        if direction == 'x':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                # player moving right
                if self.x_change > 0:
                    self.rect.x = hits[0].rect.left - self.rect.width
                # player moving left
                if self.x_change < 0:
                    self.rect.x = hits[0].rect.right
        if direction == 'y':
            hits = pygame.sprite.spritecollide(self, self.game.blocks, False)
            if hits:
                # player moving down
                if self.y_change > 0:
                    self.rect.y = hits[0].rect.top - self.rect.height
                # player moving up
                if self.y_change < 0:
                    self.rect.y = hits[0].rect.bottom

    def animate(self):
        if self.facing == 'down':
            if self.y_change == 0:
                self.image = self.down_animations[0]
            else:
                # animate sprite every 10 frames
                self.image = self.down_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'up':
            if self.y_change == 0:
                self.image = self.up_animations[0]
            else:
                # animate sprite every 10 frames
                self.image = self.up_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'left':
            if self.x_change == 0:
                self.image = self.left_animations[0]
            else:
                # animate sprite every 10 frames
                self.image = self.left_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1
        if self.facing == 'right':
            if self.x_change == 0:
                self.image = self.right_animations[0]
            else:
                # animate sprite every 10 frames by adding 0.1 and rounding the index when accessing the animation frame
                self.image = self.right_animations[math.floor(self.animation_loop)]
                self.animation_loop += 0.1
                if self.animation_loop >= 3:
                    self.animation_loop = 1