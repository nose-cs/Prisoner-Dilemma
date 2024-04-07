from players.player import Player
from players.good_guy import GoodGuy

class EyeForEye(Player):
    def play(self, matrix, full_history: list[list], history: dict) -> str:
        if matrix[1] not in history:
            return GoodGuy().play(matrix, full_history, history)
        return history[matrix[1]][-1]
    
class AdaptiveEyeForEye(Player):
    def __init__(self, window = 5) -> None:
        super().__init__()
        self.window = window

    def play(self, matrix, full_history: list[list], history: list) -> str:
        if matrix[1] not in history or len(history[matrix[1]]) < self.window:
            return GoodGuy().play(matrix, full_history, history)
        
        last_plays = history[matrix[1]][-self.window:]
        
        count = {}

        for play in last_plays:
            if play not in count:
                count[play] = 1
            else:
                count[play] += 1

        return sorted(count.items(), key=lambda pc: pc[1])[0][0]