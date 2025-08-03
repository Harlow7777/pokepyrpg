from enum import Enum
from pokemon.job import Job

class JobEnum(Enum):
    WARRIOR = Job(
        "Warrior",
        35, 10, 10, 18, 61, 8, 1, 10, 3, 15, 2
    )
    MONK = Job(
        "Monk",
        33, 20, 13, 13, 55, 5, 1, 5, 3, 10, 1
    )
    THIEF = Job(
        "Thief",
        30, 5, 5, 30, 73, 15, 1, 5, 5, 13, 2
    )
    MAGE = Job(
        "Mage",
        25, 1, 3, 13, 58, 5, 20, 10, 2, 23, 4
    )
