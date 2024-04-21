from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


@dataclass
class GameState:
    matrix: Matrix
    vector: Vector
    op_matrix: Matrix
    op_vector: Vector
    opponent_id: int


@dataclass
class Event:
    issuer_id: int


class Agent(ABC):
    @abstractmethod
    def action(self, state: GameState) -> Event:
        pass


# ======================================================================================================================

@dataclass
class PlayEvent(Event):
    strategy: int


class Player(Agent):
    def __init__(self) -> None:
        self.name = None
        self.identifier = None

    @abstractmethod
    def action(self, state: GameState) -> PlayEvent:
        pass

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        pass

    def assign_name(self, name: str):
        self.name = name


# ======================================================================================================================

class PlayerWithHistory(Player, ABC):
    def __init__(self):
        super().__init__()
        self.history: Dict[int, History] = {}

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        history_against_opponent = self.history.setdefault(game_state.opponent_id, {})
        history_against_opponent.setdefault(game_state.vector, [])
        history_against_opponent[game_state.vector].append(other_action)


# ======================================================================================================================


class LearningPlayer(PlayerWithHistory, ABC):
    def __init__(self):
        super().__init__()

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        super().update_internal_state(game_state, self_action, other_action)
        self.learn(game_state, self_action, other_action)

    def learn(self, game_state: GameState, self_action: int, other_action: int):
        pass
