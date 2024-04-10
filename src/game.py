from typing import List

from src.players import Player


def play_round(matrix_vector, player1: Player, player2: Player, history1, history2):
    action1 = player1.play(matrix_vector, history2)
    action2 = player2.play(matrix_vector, history1)

    return action1, action2, matrix_vector[0][action1][action2]


def play_tournament(players: List[Player], matrices):
    for player in players:
        player.clear()

    history = [[{} for j in range(len(players))] for i in range(len(players))]

    for matrix, vector in matrices:
        for i in range(len(players)):
            for j in range(i + 1, len(players)):
                player1 = players[i]
                player2 = players[j]

                action1, action2, scores = play_round((matrix, vector), player1, player2, history[i][j], history[j][i])

                player1.sum_score((matrix, vector), action1, scores[0])
                player2.sum_score((matrix, vector), action2, scores[1])

                if vector in history[i][j]:
                    history[i][j][vector].append(action1)
                else:
                    history[i][j][vector] = [action1]

                if vector in history[j][i]:
                    history[j][i][vector].append(action2)
                else:
                    history[j][i][vector] = [action2]
