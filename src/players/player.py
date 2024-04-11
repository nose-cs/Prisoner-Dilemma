from abc import ABC, abstractmethod


class Player(ABC):
    def __init__(self) -> None:
        self.score = 0

    def sum_score(self, matrix, action: int, score: int):
        self.score += score

    def clear(self):
        self.score = 0

    @abstractmethod
    def play(self, matrix, history: dict) -> int:
        pass
