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
        self.acc = self.stats['ACC']
        self.eva = self.stats['EVA']
        self.lck = self.stats['LCK']
        self.str = self.stats['STR']
        self.exp = 0
        self.lvl = 1
        self.crit = 0 if self.job.name != 'Monk' else self.lvl * 2 # determined by weapon
        self.current_health = self.stats['HP']
        self.health_capacity = self.stats['HP']

        self.width = width
        self.height = height
        self.enemy_spritesheet = Spritesheet('img/pokemon_spritesheet.png')
        self.image = self.enemy_spritesheet.get_sprite(x, y, self.width, self.height, BLACK)

    def get_number_of_attacks(self):
        num_attacks = max(self.acc // 32, 1)
        if self.job.name == 'Monk':
            num_attacks *= 2
        return num_attacks

