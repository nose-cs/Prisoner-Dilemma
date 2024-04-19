from src.game import Tournament
from src.generate_matrix import get_matrices
from src.generate_players import assign_names
from src.players import BadGuy, FuzzyEyeForEye, metrics, Random, EyeForEye


def print_tournament_results(tournament: Tournament, index: int):
    print("-" * 50 + "Tournament " + str(index) + "-" * 50)

    player_name = lambda p, i: player.name if player.name else f"Player {i + 1}"

    print("Scores:" + "-" * 50)
    for i, player in enumerate(tournament.players):
        print(f"{player_name(player, i)} ({player.__class__.__name__}): {player.score} score")

    winner = tournament.get_winner()
    print("Winner:" + "-" * 50)
    print(
        f"{player_name(winner, tournament.players.index(winner))} ({winner.__class__.__name__}): {winner.score} score")

    loser = tournament.get_loser()
    print("Loser:" + "-" * 50)
    print(f"{player_name(loser, tournament.players.index(loser))} ({loser.__class__.__name__}): {loser.score} score")


players = [
    Random(),
    Random(),
    Random(),
    Random(),
    EyeForEye(),
    EyeForEye(),
    EyeForEye(),
    EyeForEye(),
    BadGuy(),
    BadGuy(),
    FuzzyEyeForEye(metrics.FuzzyFunctions.envy),
    FuzzyEyeForEye(metrics.FuzzyFunctions.sub_joint),
    FuzzyEyeForEye(metrics.FuzzyFunctions.dif_sum_rows)
]

players = assign_names(players)

matrices = [element for element in
            get_matrices(["Resolución de disputas en el sector de bienes raíces", "Dilema del prisionero", ])]

tournament = Tournament(players, matrices, tell_story=True)

for i in range(1):
    tournament.play()
    print_tournament_results(tournament, i + 1)
