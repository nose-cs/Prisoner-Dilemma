import random
from typing import List

from src.players import Player, PlayerWithHistory, GameState, PlayEvent


class RandomGuy(Player):
    def action(self, state: GameState) -> PlayEvent:
        matrix_len = len(state.matrix)
        return PlayEvent(issuer_id=self.identifier, strategy=random.choice(range(matrix_len)))


class BadGuy(Player):
    def action(self, state: GameState) -> PlayEvent:
        maxx = None
        index_max = None

        for i, row in enumerate(state.matrix):
            min_row = min(row, key=lambda actions: actions[0])

            if (not maxx) or min_row > maxx:
                maxx = min_row
                index_max = i

        return PlayEvent(issuer_id=self.identifier, strategy=index_max)


class GoodGuy(Player):
    def action(self, state: GameState) -> PlayEvent:
        max = None
        index_max = None

        for i, row in enumerate(state.matrix):
            average = 0

            for actions in row:
                average += (actions[0] + actions[1]) / 2

            if (not max) or average > max:
                max = average
                index_max = i

        return PlayEvent(issuer_id=self.identifier, strategy=index_max)


class EyeForEye(PlayerWithHistory):
    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        if state.vector not in history_against_opponent:
            strategy = GoodGuy().action(state).strategy
        else:
            strategy = history_against_opponent[state.vector][-1]
        return PlayEvent(issuer_id=self.identifier, strategy=strategy)


class AdaptiveEyeForEye(PlayerWithHistory):
    def __init__(self, window=5) -> None:
        super().__init__()
        self.window = window

    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        if state.vector not in history_against_opponent or len(
                history_against_opponent[state.vector]) < self.window:
            strategy = GoodGuy().action(state).strategy
            return PlayEvent(issuer_id=self.identifier, strategy=strategy)

        last_plays: List[int] = history_against_opponent[state.vector][-self.window:]

        count = {}

        for play in last_plays:
            if play not in count:
                count[play] = 1
            else:
                count[play] += 1

        most_common = sorted(count.items(), key=lambda pc: pc[1])[0][0]

        return PlayEvent(issuer_id=self.identifier, strategy=most_common)
