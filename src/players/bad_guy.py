from src.players import Player, GameState


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
