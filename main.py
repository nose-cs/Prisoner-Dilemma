from src.game import Tournament
from src.generate_matrix import get_random_matrices
from src.generate_players import assign_names
from src.players import BadGuy, AdaptiveEyeForEye, GoodGuy, EyeForEye, Random, SimpleMetaHeuristicGuy, GeneticGuy


def print_tournament_results(tournament: Tournament, index: int):
    print("-" * 50 + "Tournament " + str(index) + "-" * 50)

    rounds = len(tournament.matrices) * (len(tournament.players) - 1)

    print("Scores:" + "-" * 50)
    for i, player in enumerate(tournament.players):
        print(f"Player {i + 1} ({player.__class__.__name__}): {player.score} score")

    winner = tournament.get_winner()
    print("Winner:" + "-" * 50)
    print(f"Player {tournament.players.index(winner) + 1} ({winner.__class__.__name__}): {winner.score} score")

    loser = tournament.get_loser()
    print("Loser:" + "-" * 50)
    print(f"Player {tournament.players.index(loser) + 1} ({loser.__class__.__name__}): {loser.score} score")


players = [
    GeneticGuy(),
    Random(),
    GoodGuy(),
    SimpleMetaHeuristicGuy(),
    BadGuy(),
    GoodGuy(),
    GoodGuy(),
    EyeForEye(),
    EyeForEye(),
    EyeForEye(),
    AdaptiveEyeForEye(),
    AdaptiveEyeForEye()
]

players = assign_names(players)

matrices = [element for element in get_random_matrices(2)]

tournament = Tournament(players, matrices, tell_story=True)

for i in range(1):
    tournament.play()
    print_tournament_results(tournament, i + 1)
