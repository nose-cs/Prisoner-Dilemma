from src.players import GoodGuy, Player, GameState


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
