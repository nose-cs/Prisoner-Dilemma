from players.player import Player
import random

class Random(Player):
    def play(self, full_history: list[list], history: list) -> str:
        return random.choice(['C', 'T'])