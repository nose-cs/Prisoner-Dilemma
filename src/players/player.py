from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Dict, Tuple

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple
History = Dict[Vector, List[int]]


@dataclass
class GameState:
    """
    Represents the current state of the game.

    Attributes:
        matrix: The matrix for the current round.
        vector: The vector that represents the matrix.
        op_matrix: The matrix of the opponent for the current round.
        op_vector: The vector that represents the matrix of the opponent.
        opponent_id: The id of the opponent.
    """
    matrix: Matrix
    vector: Vector
    op_matrix: Matrix
    op_vector: Vector
    opponent_id: int


@dataclass
class Event:
    """
    Represents an event that occurs in the game.
    """
    issuer_id: int


class Agent(ABC):
    """
    Represents an agent in the game.
    """

    @abstractmethod
    def action(self, state: GameState) -> Event:
        """
        Returns the action that the agent will take given the current state of the game.
        :param state: The current state of the game.
        :return: The action that the agent will take.
        """
        pass


# ======================================================================================================================

@dataclass
class PlayEvent(Event):
    """
    Represents a play event in the game.

    Attributes:
        issuer_id: The id of the player that issued the event.
        strategy: The strategy that the player will play.
    """
    strategy: int


class Player(Agent, ABC):
    """
    Represents a player in the game.

    Attributes:
        name: The name of the player.
        identifier: The id of the player.
    """

    def __init__(self) -> None:
        self.name = None
        self.identifier = None

    @abstractmethod
    def action(self, state: GameState) -> PlayEvent:
        pass

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        """
        Updates the internal state of the player.
        :param game_state: The current state of the game.
        :param self_action: The action that the player took.
        :param other_action: The action that the opponent took.
        """
        pass

    def assign_name(self, name: str):
        self.name = name


# ======================================================================================================================

class PlayerWithHistory(Player, ABC):
    """
    Represents a player that keeps track of the history of his matches.

    Attributes:
        history: A dictionary that keeps track of the history of the matches.
    """

    def __init__(self):
        super().__init__()
        self.history: Dict[int, History] = {}

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        history_against_opponent = self.history.setdefault(game_state.opponent_id, {})
        history_against_opponent.setdefault(game_state.vector, [])
        history_against_opponent[game_state.vector].append(other_action)


# ======================================================================================================================


class LearningPlayer(PlayerWithHistory, ABC):
    """
    Represents a player that learns from his matches.
    """

    def __init__(self):
        super().__init__()

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        super().update_internal_state(game_state, self_action, other_action)
        self.learn(game_state, self_action, other_action)

    def learn(self, game_state: GameState, self_action: int, other_action: int):
        pass
