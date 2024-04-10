import random

from src.players import Player


class Random(Player):
    def play(self, matrix, history: dict) -> int:
        return random.choice(range(len(matrix[0])))
