import random

from src.players import Player, GameState


class Random(Player):
    def play(self, game_state: GameState) -> int:
        matrix_len = len(game_state.matrix)
        return random.choice(range(matrix_len))
