from players.player import Player

class GoodGuy(Player):
    def play(self, index_player, full_history: list[list], history: list) -> str:
        return 'C'