from players.player import Player

class BadGuy(Player):
    def play(self, index_player, full_history: list[list], history: list) -> str:
        return 'T'