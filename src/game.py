from typing import List, Dict, Tuple

from src.generate_matrix import MatrixStructure
from src.players import Player
from src.players.player import GameState

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


class Tournament:
    """
    A class to represent a Tournament.

    Attributes
    ----------
    players (List[Player]): the list of players in the tournament.
    matrices (List[MatrixStructure]): the list of matrices to play each match.
    history (Dict[Tuple[int, int], History]): the history of each match.
    """

    def __init__(self, players: List[Player], matrices: List[MatrixStructure]):
        self.players = players
        self.matrices = matrices
        self.history: Dict[Tuple[int, int], History] = {}

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
        """
        Play a match between two players. A match consists of playing all the matrices in the tournament.
        :param player1: the first player.
        :param player2: the second player.
        :param history_key: the key to store the history of the match.
        """
        history1 = self.history.get(history_key, {})
        history2 = self.history.get((history_key[1], history_key[0]), {})
        plays = []
        last_matrix = None

        for matrix_structure in self.matrices:
            matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
            game_state_1 = GameState(matrix1, vector1, matrix2, vector2, history2, plays, last_matrix)
            game_state_2 = GameState(matrix2, vector2, matrix1, vector1, history1, plays, last_matrix)

            action1, action2, scores = self._play_round(matrix_structure.matrix1, player1, player2, game_state_1,
                                                        game_state_2)
            score1, score2 = scores

            plays.append((action1, action2))

            matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
            player1.sum_score(game_state_1, action1, action2, history2, score1)
            player2.sum_score(game_state_2, action2, action1, history1, score2)

            last_matrix = (matrix1, matrix2)

            history1.setdefault(vector1, []).append(action1)
            history2.setdefault(vector2, []).append(action2)

        self.history[history_key] = history1
        self.history[(history_key[1], history_key[0])] = history2

    @staticmethod
    def _play_round(matrix: Matrix, player1: Player, player2: Player, game_state_1: GameState, game_state_2: GameState) -> Tuple[
        int, int, Tuple[float, float]]:
        """
        Play a round between two players.
        :param matrix: the matrix to play the round, for each player (the same if the matrix is symmetric,
            the transpose if not).
        :param player1: the first player.
        :param player2: the second player.
        :param game_state_1: the game state for the first player.
        :param game_state_2: the game state for the second player.
        :return: the actions of the players and the scores of the round for each player.
        """
        action1 = player1.play(game_state_1)
        action2 = player2.play(game_state_2)

        return action1, action2, matrix[action1][action2]

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
