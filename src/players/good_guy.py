from src.players import Player


class GoodGuy(Player):
    def play(self, matrix, history: dict) -> int:
        max = None
        index_max = None

        for i, row in enumerate(matrix[0]):
            average = 0

            for actions in row:
                average += (actions[0] + actions[1]) / 2

            if (not max) or average > max:
                max = average
                index_max = i

        return index_max
