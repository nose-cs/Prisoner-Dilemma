from src.players import Player

class NashGuy(Player):
    def __init__(self) -> None:
        super().__init__()

        self.probs = {}

    def sum_score(self, matrix, mine_action: int, other_action: int, score: int):
        super().sum_score(matrix, mine_action, other_action, score)

        matrix, vector = matrix