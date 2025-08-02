from config import *
from sprites import *

class Pokemon:
    def __init__(self, name, x, y, width, height, job, weapon, armor):
        self.name = name
        self.job = job            # Instance of Job
        self.weapon = weapon      # Instance of Weapon
        self.armor = armor        # Instance of Armor

        self.base_stats = job.get_base_stats()  # Dict of base stats
        self.stats = self.base_stats
        self.agl = self.stats['AGL']
        self.current_health = self.stats['HP']
        self.health_capacity = self.stats['HP']

        self.width = width
        self.height = height
        self.enemy_spritesheet = Spritesheet('img/pokemon_spritesheet.png')
        self.image = self.enemy_spritesheet.get_sprite(x, y, self.width, self.height, BLACK)

