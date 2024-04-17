from players.player import Player

class GoodGuy(Player):
    def play(self, matrix, full_history: list[list], history: dict) -> str:
        max = None
        index_max = None

        for i, row in enumerate(matrix[0]):
            sum = -1000000

            for actions in row:
                sum += actions[0] + actions[1]

            if (not max) or sum > max:
                max = sum
                index_max = i

        return index_max