import random

from src.players import Player, GameState


class Random(Player):
    def play(self, game_state: GameState) -> int:
        matrix_len = len(game_state.matrix)
        return random.choice(range(matrix_len))


class BadGuy(Player):
    def play(self, game_state: GameState) -> int:
        maxx = None
        index_max = None

        for i, row in enumerate(game_state.matrix):
            min_row = min(row, key=lambda actions: actions[0])

            if (not maxx) or min_row > maxx:
                maxx = min_row
                index_max = i

        return index_max


class GoodGuy(Player):
    def play(self, game_state: GameState) -> int:
        max = None
        index_max = None

        for i, row in enumerate(game_state.matrix):
            average = 0

            for actions in row:
                average += (actions[0] + actions[1]) / 2

            if (not max) or average > max:
                max = average
                index_max = i

        return index_max


class EyeForEye(Player):
    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history:
            return GoodGuy().play(game_state)
        return game_state.history[game_state.vector][-1]


class AdaptiveEyeForEye(Player):
    def __init__(self, window=5) -> None:
        super().__init__()
        self.window = window

    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history or len(game_state.history[game_state.vector]) < self.window:
            return GoodGuy().play(game_state)

        last_plays = game_state.history[game_state.vector][-self.window:]

        count = {}

        for play in last_plays:
            if play not in count:
                count[play] = 1
            else:
                count[play] += 1

        return sorted(count.items(), key=lambda pc: pc[1])[0][0]
