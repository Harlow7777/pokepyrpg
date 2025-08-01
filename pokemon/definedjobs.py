from enum import Enum
from pokemon.job import Job

class JobEnum(Enum):
    WARRIOR = Job(
        "Warrior",
        35, 10, 20, 5, 1, 5, 10, 3, 15, 3
    )
    MONK = Job(
        "Monk",
        33, 20, 5, 5, 5, 5, 5, 3, 10, 4
    )
    THIEF = Job(
        "Thief",
        30, 5, 5, 10, 5, 15, 5, 2, 15, 2
    )
    MAGE = Job(
        "Mage",
        25, 1, 1, 10, 20, 10, 5, 1, 20, 2
    )
