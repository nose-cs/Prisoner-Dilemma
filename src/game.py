from typing import List, Dict, Tuple

from src.generate_matrix import MatrixStructure
from src.players import Player
from src.players.player import GameState
from src.storyteller import StoryTeller

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


# ambiente
# inaccesible porque no se conoce completamente el estado
# no determinista pues el proximo estado no depende solo de la acción actual, sino además de la acción del oponente
# no es episódico
# estático porque no cambia en el tiempo a menos que el agente realice una acción sobre él
# discreto

class Tournament:
    """
    A class to represent a Tournament.

    Attributes:
    - players (List[Player]): List of players participating in the tournament.
    - matrices (List[Tuple[Matrix, Vector]]): List of matrices for the tournament.
    - history (Dict[Tuple[int, int], Dict[Vector, List[int]]]): History of previous actions.
    """

    def __init__(self, players: List[Player], matrices: List[MatrixStructure], tell_story=False):
        self.players = players
        self.matrices = matrices
        self.history: Dict[Tuple[int, int], History] = {}
        self.storyteller = StoryTeller() if tell_story else None

    def play(self):
        """Play the tournament."""
        self._clear()
        num_players = len(self.players)

        for i in range(num_players):
            for j in range(i + 1, num_players):
                player1 = self.players[i]
                player2 = self.players[j]
                history_key = (i, j)

                self._play_match(player1, player2, history_key)

    def _play_match(self, player1: Player, player2: Player, history_key: Tuple[int, int]):
        """Play a match between two players."""
        history1 = self.history.get(history_key, {})
        history2 = self.history.get((history_key[1], history_key[0]), {})

        for matrix_structure in self.matrices:
            action1, action2, scores = self._play_round(matrix_structure, player1, player2,
                                                        history1, history2)
            score1, score2 = scores

            matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
            player1.sum_score((matrix1, vector1), action1, action2, history2, score1)
            player2.sum_score((matrix2, vector2), action2, action1, history1, score2)

            history1.setdefault(vector1, []).append(action1)
            history2.setdefault(vector2, []).append(action2)

        self.history[history_key] = history1
        self.history[(history_key[1], history_key[0])] = history2

    def _play_round(self, matrix_structure, player1: Player, player2: Player, history1, history2):
        matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
        game_state_1 = GameState(matrix1, vector1, history2)
        game_state_2 = GameState(matrix2, vector2, history1)
        action1 = player1.play(game_state_1)
        action2 = player2.play(game_state_2)

        # if self.storyteller:
        #     story = self.storyteller.tell_round_story(matrix_structure.matrix_title, player1, player2, action1, action2)
        #     print(story)

        return action1, action2, matrix1[action1][action2]

    def _clear(self):
        """Clear the scores and history for all players."""
        for player in self.players:
            player.clear()
        self.history = {}

    def get_scores(self):
        return [player.score for player in self.players]

    def get_winner(self):
        return max(self.players, key=lambda x: x.score)

    def get_loser(self):
        return min(self.players, key=lambda x: x.score)
