from players.player import Player

class GoodGuy(Player):
    def play(self, full_history: list[list], history: list) -> str:
        return 'C'