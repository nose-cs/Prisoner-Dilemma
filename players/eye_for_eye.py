from players.player import Player

class EyeForEye(Player):
    def play(self, full_history: list[list], history: list) -> str:
        if not history or history[-1] == 'C':
            return 'C'
        return 'T'