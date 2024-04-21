from typing import List

from src.players import GoodGuy, GameState, BadGuy, PlayEvent, PlayerWithHistory


class FuzzyEyeForEye(PlayerWithHistory):
    def __init__(self, fuzzy_metric) -> None:
        super().__init__()
        self.metric = fuzzy_metric
        self.opponent_plays: List[int] = []
        self.opponent_previous_matrix = None

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        super().update_internal_state(game_state, self_action, other_action)
        self.opponent_plays.append(other_action)
        self.opponent_previous_matrix = game_state.op_matrix

    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}

        if state.vector not in history_against_opponent:
            strategy = GoodGuy().action(state).strategy
            return PlayEvent(issuer_id=self.identifier, strategy=strategy)

        fuzzy_value = self.metric(self.opponent_previous_matrix, self.opponent_plays[-1])

        min_diff = 1000000000
        ret = -1
        for i in range(len(state.matrix)):
            cand = self.metric(state.matrix, i)
            if abs(fuzzy_value - cand) < min_diff:
                min_diff = fuzzy_value - cand
                ret = i
        return PlayEvent(issuer_id=self.identifier, strategy=ret)


class FuzzyDeterministicEyeForEye(PlayerWithHistory):
    def __init__(self, fuzzy_metric) -> None:
        super().__init__()
        self.metric = fuzzy_metric
        self.opponent_plays: List[int] = []
        self.opponent_previous_matrix = None

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        super().update_internal_state(game_state, self_action, other_action)
        self.opponent_plays.append(other_action)
        self.opponent_previous_matrix = game_state.op_matrix

    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}

        if state.vector not in history_against_opponent:
            strategy = GoodGuy().action(state).strategy
            return PlayEvent(issuer_id=self.identifier, strategy=strategy)

        fuzzy_value = self.metric(self.opponent_previous_matrix, self.opponent_plays[-1])

        if fuzzy_value > 0.7:
            strategy = GoodGuy().action(state).strategy
        else:
            strategy = BadGuy().action(state).strategy
        return PlayEvent(issuer_id=self.identifier, strategy=strategy)
