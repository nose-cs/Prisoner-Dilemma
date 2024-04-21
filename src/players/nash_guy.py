from src.players import Player, GameState


class NashGuy(Player):
    def __init__(self, num_rounds_for_collection=1) -> None:
        super().__init__()

        self.probs = {}
        self.num_rounds_for_collection = num_rounds_for_collection
        self.count_collection_rounds = 0

    def learn(self, game_state: GameState, mine_action: int, other_action: int, opponent_history, reward: float):
        matrix, vector = game_state.matrix, game_state.vector

        self.probs[id(opponent_history)][vector][mine_action][1][other_action] += 1
        self.probs[id(opponent_history)][vector][mine_action] = (
            self.probs[id(opponent_history)][vector][mine_action][0] + 1,
            self.probs[id(opponent_history)][vector][mine_action][1])

    def sum_score(self, game_state: GameState, mine_action: int, other_action: int, opponent_history, score: float):
        super().sum_score(game_state, mine_action, other_action, opponent_history, score)
        self.learn(game_state, mine_action, other_action, opponent_history, score)

    def play(self, game_state: GameState) -> int:
        max_play = None
        max_expected = None

        opponent = self.probs.setdefault(id(game_state.history), {})
        plays = opponent.setdefault(game_state.vector, {})

        for i, row in enumerate(game_state.matrix):
            expected = 0
            total, counts = plays.setdefault(i, (0, {}))

            for j in range(len(row)):
                counts.setdefault(j, 0)

            if self.count_collection_rounds < self.num_rounds_for_collection:
                if i == len(game_state.matrix) - 1:
                    self.count_collection_rounds += 1

                return i

            for j, gains in enumerate(row):
                expected += gains[0] * (counts[j] / total)

            if (not max_expected) or expected > max_expected:
                max_expected = expected

                max_play = i

        return max_play

    def clear(self):
        self.probs = {}
        self.count_collection_rounds = 0
        return super().clear()
