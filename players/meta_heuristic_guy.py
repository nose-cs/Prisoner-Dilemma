from players.player import Player
import random

class SimpleMetaHeuristicGuy(Player):
    def __init__(self) -> None:
        super().__init__()
        self.memory = {'C': 0, 'T': 0}

    def sum_years(self, action: str, years: int):
        super().sum_years(action, years)
        self.memory[action] += years
    
    def play(self, full_history: list[list], history: list) -> str:
        if random.random() < 0.1:  # Exploration
            return random.choice(['C', 'T'])
        else:  # Exploitation
            return 'C' if self.memory['C'] < self.memory['T'] else 'T'