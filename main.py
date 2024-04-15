from src.game import Tournament
from src.generate_matrix import prisoner_dilemma_matrix
from src.players import BadGuy, EyeForEye, AdaptiveEyeForEye, GoodGuy


def print_matrices(matrices):
    print("-" * 50 + "Matrices:" + "-" * 50)
    for index, matrix in enumerate(matrices):
        print("Matrix " + str(index) + ":")
        print(matrix[0])
        print()


def prisoner_dilemma_score(score, rounds):
    return score #- 5 * rounds


def print_tournament_results(tournament: Tournament, index: int):
    print("-" * 50 + "Tournament " + str(index) + "-" * 50)

    rounds = len(tournament.matrices) * (len(tournament.players) - 1)
    player_score = lambda player: prisoner_dilemma_score(player.score, rounds)

    print("Scores:" + "-" * 50)
    for i, player in enumerate(tournament.players):
        print(f"Player {i + 1} ({player.__class__.__name__}): {player_score(player)} score")

    winner = tournament.get_winner()
    print("Winner:" + "-" * 50)
    print(f"Player {tournament.players.index(winner) + 1} ({winner.__class__.__name__}): {player_score(winner)} score")

    loser = tournament.get_loser()
    print("Loser:" + "-" * 50)
    print(f"Player {tournament.players.index(loser) + 1} ({loser.__class__.__name__}): {player_score(loser)} score")


players = [
    # GeneticGuy(),
    # Random(),
    # GoodGuy(),
    # SimpleMetaHeuristicGuy(),
    BadGuy(),
    EyeForEye(),
    EyeForEye(),
    EyeForEye(),
    AdaptiveEyeForEye(),
AdaptiveEyeForEye()
]

matrices = [prisoner_dilemma_matrix() for _ in range(1000)]

print_matrices(matrices)

tournament = Tournament(players, matrices)

for i in range(1):
    tournament.play()
    print_tournament_results(tournament, i + 1)
