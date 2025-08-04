class Job:
    def __init__(self, name, hp, exp, vit, str_, acc, eva, agl, int_, lck, acc_growth, mdef, mdef_growth):
        self.name = name
        self.hp = hp
        self.exp = exp
        self.vit = vit
        self.str = str_
        self.acc = acc
        self.eva = eva
        self.agl = agl
        self.int = int_
        self.lck = lck
        self.acc_growth = acc_growth
        self.mdef = mdef
        self.mdef_growth = mdef_growth

    def get_base_stats(self):
        return {
            "HP": self.hp,
            "EXP": self.exp,
            "VIT": self.vit,
            "STR": self.str,
            "ACC": self.acc,
            "EVA": self.eva,
            "AGL": self.agl,
            "INT": self.int,
            "LCK": self.lck,
            "ACC_GROWTH": self.acc_growth,
            "MDEF": self.mdef,
            "MDEF_GROWTH": self.mdef_growth
        }
