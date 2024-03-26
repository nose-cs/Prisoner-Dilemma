from players.player import Player
import random

class Random(Player):
    def play(self, index_player, full_history: list[list], history: list) -> str:
        return random.choice(['C', 'T'])