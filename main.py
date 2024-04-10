from src.game import play_tournament
from src.generate_matrix import generate_matrix
from src.players import GeneticGuy

matrices = []

geneticguy2 = GeneticGuy()
geneticguy = GeneticGuy()

for i in range(50):
    matrices.append(generate_matrix())

players = [geneticguy2,
           geneticguy]

for i in range(1):
    play_tournament(players, matrices)

for i, player in enumerate(players):
    print(f"Player {i + 1} ({player.__class__.__name__}): {player.score} score")
