from enum import Enum


class ShinyHunterType(Enum):
    stationary = "stationary"
    starter = "starter"        # 🆕 unser neuer Hunter-Typ

    def __str__(self):
        return self.value
