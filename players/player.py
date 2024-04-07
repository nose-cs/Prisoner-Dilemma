class Player:
    def __init__(self) -> None:
        self.score = 0

    def sum_score(self, matrix, action: int, score: int):
        self.score += score

    def clear(self):
        self.score = 0

    def play(self, matrix, full_history: list[list], history: dict) -> str:
        pass