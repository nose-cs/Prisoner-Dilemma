from typing import List, Dict, Tuple

from src.generate_matrix import MatrixStructure
from src.players import Player
from src.players.player import GameState, PlayEvent

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


class Tournament:
    def __init__(self, players: List[Player], matrices: List[MatrixStructure]):
        self.players = players
        self.scores = [0] * len(players)
        self.matrices = matrices
        self.history: Dict[Tuple[int, int], History] = {}
        self.set_players_tournament_info()

    def play(self):
        """Play the tournament."""
        self._clear()
        num_players = len(self.players)

        for i in range(num_players):
            for j in range(i + 1, num_players):
                player1 = self.players[i]
                player2 = self.players[j]
                self._play_match(player1, player2)

    def _play_match(self, player1: Player, player2: Player):
        """
        Play a match between two players. A match consists of playing all the matrices in the tournament.
        :param player1: the first player.
        :param player2: the second player.
        """
        for matrix_structure in self.matrices:
            matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
            game_state_1 = GameState(matrix1, vector1, matrix2, vector2, player2.identifier)
            game_state_2 = GameState(matrix2, vector2, matrix1, vector1, player1.identifier)

            action1 = player1.action(game_state_1)
            action2 = player2.action(game_state_2)

            player1.update_internal_state(game_state_1, action1.strategy, action2.strategy)
            player2.update_internal_state(game_state_2, action2.strategy, action1.strategy)

            score1, score2 = matrix_structure.matrix1[action1.strategy][action2.strategy]
            self.scores[player1.identifier] += score1
            self.scores[player2.identifier] += score2

            self.update_history(action1, action2, vector1, vector2)

    def update_history(self, play_event1: PlayEvent, play_event2: PlayEvent, vector1: Vector, vector2: Vector):
        player1 = play_event1.issuer_id
        player2 = play_event2.issuer_id
        action1 = play_event1.strategy
        action2 = play_event2.strategy

        if (player1, player2) in self.history:
            history1 = self.history[(player1, player2)]
        else:
            history1 = {}

        if (player2, player1) in self.history:
            history2 = self.history[(player2, player1)]
        else:
            history2 = {}

        history1.setdefault(vector1, []).append(action1)
        history2.setdefault(vector2, []).append(action2)

    def set_players_tournament_info(self):
        for i, player in enumerate(self.players):
            player.identifier = i

    def _clear(self):
        """Clear the scores and history for all players."""
        self.history = {}
        self.scores = [0] * len(self.players)


def print_tournament_results(tournament: Tournament, index: int = 0):
    print("-" * 50 + "Tournament " + str(index + 1) + "-" * 50)

    player_name = lambda player: player.name if player.name else f"Player {player.identifier + 1}"

    print("Scores:" + "-" * 50)
    for player, score in zip(tournament.players, tournament.scores):
        print(f"{player_name(player)} ({player.__class__.__name__}): {score} score")

    print("Winner" + "-" * 50)

    winner_index = tournament.scores.index(max(tournament.scores))
    winner = tournament.players[winner_index]
    winner_score = tournament.scores[winner_index]
    print(f"{player_name(winner)} ({winner.__class__.__name__}): {winner_score} score")

    print("Loser" + "-" * 50)

    loser_index = tournament.scores.index(min(tournament.scores))
    loser = tournament.players[loser_index]
    loser_score = tournament.scores[loser_index]
    print(f"{player_name(loser)} ({loser.__class__.__name__}): {loser_score} score")
