from src.players import GoodGuy, Player, GameState, BadGuy


class FuzzyEyeForEye(Player):
    def __init__(self, fuzzy_metric) -> None:
        super().__init__()
        self.metric = fuzzy_metric

    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history:
            return GoodGuy().play(game_state)
        fuzzy_value = self.metric(game_state.previous_matrix[1], game_state.plays[-1][1])
        min_diff = 1000000000
        ret = -1
        for i in range(len(game_state.matrix)):
            cand = self.metric(game_state.matrix, i)
            if abs(fuzzy_value - cand) < min_diff:
                min_diff = fuzzy_value - cand
                ret = i
        return ret


class FuzzyDeterministicEyeForEye(Player):
    def __init__(self, fuzzy_metric) -> None:
        super().__init__()
        self.metric = fuzzy_metric

    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history:
            return GoodGuy().play(game_state)
        fuzzy_value = self.metric(game_state.previous_matrix[1], game_state.plays[-1][1])
        return GoodGuy().play(game_state) if fuzzy_value > 0.7 else BadGuy().play(game_state)
