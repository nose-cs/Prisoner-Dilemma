from src.players import Player, GameState

class NashGuy(Player):
    def __init__(self) -> None:
        super().__init__()

        self.probs = {}

    def sum_score(self, matrix, mine_action: int, other_action: int, oponent_history, score: int):
        super().sum_score(matrix, mine_action, other_action, oponent_history, score)

        matrix, vector = matrix

        self.probs[id(oponent_history)][vector][mine_action][1][other_action] += 1
        self.probs[id(oponent_history)][vector][mine_action] = (self.probs[id(oponent_history)][vector][mine_action][0] + 1, self.probs[id(oponent_history)][vector][mine_action][1])

    def play(self, game_state: GameState) -> int:
        max_play = None
        max_expected = None

        oponent = self.probs.setdefault(id(game_state.history), {})
        plays = oponent.setdefault(game_state.vector, {})

        for i, row in enumerate(game_state.matrix):
            expected = 0
            total, counts = plays.setdefault(i, (0, {}))

            for j in range(len(row)):
                counts.setdefault(j, 0)

            if total == 0:
                return i

            for j, gains in enumerate(row):
                expected += gains[0] * (counts[j] / total)

            if (not max_expected) or expected > max_expected:
                max_expected = expected
                max_play = i

        return max_play
    
    def clear(self):
        self.probs = {}
        return super().clear()