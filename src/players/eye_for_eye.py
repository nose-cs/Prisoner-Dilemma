from src.players import GoodGuy, Player, GameState, BadGuy


class EyeForEye(Player):
    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history:
            return GoodGuy().play(game_state)
        return game_state.history[game_state.vector][-1]


class AdaptiveEyeForEye(Player):
    def __init__(self, window=5) -> None:
        super().__init__()
        self.window = window

    def play(self, game_state: GameState) -> int:
        if game_state.vector not in game_state.history or len(game_state.history[game_state.vector]) < self.window:
            return GoodGuy().play(game_state)

        last_plays = game_state.history[game_state.vector][-self.window:]

        count = {}

        for play in last_plays:
            if play not in count:
                count[play] = 1
            else:
                count[play] += 1

        return sorted(count.items(), key=lambda pc: pc[1])[0][0]

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
        return GoodGuy().play(GameState) if fuzzy_value > 0.7 else BadGuy().play(GameState)
        