from players.player import Player

class EyeForEye(Player):
    def play(self, index_player, full_history: list[list], history: list) -> str:
        if not history or history[-1] == 'C':
            return 'C'
        return 'T'
    
class AdaptiveEyeForEye(Player):
    def __init__(self, window = 5) -> None:
        super().__init__()
        self.window = window

    def play(self, index_player, full_history: list[list], history: list) -> str:
        if len(history) < self.window:
            return 'C'
        
        last_plays = history[-self.window:]
        prop_c = last_plays.count('C') / self.window

        if prop_c > 0.5:
            return 'C'
        else:
            return 'T'