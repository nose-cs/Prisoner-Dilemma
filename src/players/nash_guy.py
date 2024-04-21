from src.players import LearningPlayer, GameState, PlayEvent


class NashGuy(LearningPlayer):
    def __init__(self, num_rounds_for_collection=1) -> None:
        super().__init__()
        self.probs = {}
        self.num_rounds_for_collection = num_rounds_for_collection
        self.count_collection_rounds = 0

    def learn(self, game_state: GameState, mine_action: int, other_action: int):
        vector = game_state.vector
        opponent_id = game_state.opponent_id

        self.probs[opponent_id][vector][mine_action][1][other_action] += 1
        self.probs[opponent_id][vector][mine_action] = (
            self.probs[opponent_id][vector][mine_action][0] + 1,
            self.probs[opponent_id][vector][mine_action][1])

    def action(self, game_state: GameState) -> PlayEvent:
        max_play = None
        max_expected = None
        opponent_id = game_state.opponent_id

        opponent = self.probs.setdefault(opponent_id, {})
        plays = opponent.setdefault(game_state.vector, {})

        for i, row in enumerate(game_state.matrix):
            expected = 0
            total, counts = plays.setdefault(i, (0, {}))

            for j in range(len(row)):
                counts.setdefault(j, 0)

            if self.count_collection_rounds < self.num_rounds_for_collection:
                if i == len(game_state.matrix) - 1:
                    self.count_collection_rounds += 1
                return PlayEvent(issuer_id=self.identifier, strategy=i)

            for j, gains in enumerate(row):
                expected += gains[0] * (counts[j] / total)

            if (not max_expected) or expected > max_expected:
                max_expected = expected

                max_play = i

        return PlayEvent(issuer_id=self.identifier, strategy=max_play)
