from players.player import Player
import random

class Random(Player):
    def play(self, matrix, full_history: list[list], history: dict) -> str:
        return random.choice(range(len(matrix[0])))