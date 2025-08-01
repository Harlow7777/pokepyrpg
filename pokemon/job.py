class Job:
    def __init__(self, name, hp, vit, str_, agl, int_, lck, hit, hit_growth, mdef, mdef_growth):
        self.name = name
        self.hp = hp
        self.vit = vit
        self.str = str_
        self.agl = agl
        self.int = int_
        self.lck = lck
        self.hit = hit
        self.hit_growth = hit_growth
        self.mdef = mdef,
        self.mdef_growth = mdef_growth

    def get_base_stats(self):
        return {
            "HP": self.hp,
            "VIT": self.vit,
            "STR": self.str,
            "AGL": self.agl,
            "INT": self.int,
            "LCK": self.lck,
            "HIT": self.hit,
            "HIT_GROWTH": self.hit_growth,
            "MDEF": self.mdef,
            "MDEF_GROWTH": self.mdef_growth
        }
