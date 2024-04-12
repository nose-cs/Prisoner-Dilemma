from abc import ABC, abstractmethod
from typing import List, Dict, Tuple

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


class GameState:
    def __init__(self, matrix, vector, history):
        self.matrix: Matrix = matrix
        self.vector: Vector = vector
        self.history: History = history


class Player(ABC):
    def __init__(self) -> None:
        self.score = 0

    def sum_score(self, matrix, action: int, score: int):
        self.score += score

    def clear(self):
        self.score = 0

    @abstractmethod
    def play(self, game_state: GameState) -> int:
        pass
