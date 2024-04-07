from players.player import Player

class BadGuy(Player):
    def play(self, matrix, full_history: list[list], history: dict) -> str:
        maxx = None
        index_max = None
        
        for i, row in enumerate(matrix[0]):
            min_row = min(row, key=lambda actions: actions[0])

            if (not maxx) or min_row > maxx:
                maxx = min_row
                index_max = i

        return index_max       