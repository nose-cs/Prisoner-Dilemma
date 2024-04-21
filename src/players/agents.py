from __future__ import annotations

import random
from abc import abstractmethod, ABC
from dataclasses import dataclass
from typing import List, Tuple, Dict

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.generate_matrix import MatrixStructure
from src.generate_matrix import get_matrix_len, get_vector_len, generate_matrix

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


class Agent(ABC):
    @abstractmethod
    def action(self, state: GameState) -> Event:
        pass


@dataclass
class GameState:
    matrix: Matrix
    vector: Vector
    op_matrix: Matrix
    op_vector: Vector
    opponent_id: int


@dataclass
class Event:
    issuer_id: int


# ======================================================================================================================

@dataclass
class PlayEvent(Event):
    strategy: int


class Player(Agent):
    def __init__(self) -> None:
        self.name = None
        self.identifier = None

    @abstractmethod
    def action(self, state: GameState) -> PlayEvent:
        pass

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        pass

    def assign_name(self, name: str):
        self.name = name


# ======================================================================================================================

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


# =====================================================================================================================
class PlayerWithHistory(Player, ABC):
    def __init__(self):
        super().__init__()
        self.history: Dict[int, History] = {}

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        history_against_opponent = self.history.setdefault(game_state.opponent_id, {})
        history_against_opponent.setdefault(game_state.vector, [])
        history_against_opponent[game_state.vector].append(other_action)


class EyeForEye(PlayerWithHistory):
    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}
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
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}
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


# ======================================================================================================================

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
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}

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
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}

        if state.vector not in history_against_opponent:
            strategy = GoodGuy().action(state).strategy
            return PlayEvent(issuer_id=self.identifier, strategy=strategy)

        fuzzy_value = self.metric(self.opponent_previous_matrix, self.opponent_plays[-1])

        if fuzzy_value > 0.7:
            strategy = GoodGuy().action(state).strategy
        else:
            strategy = BadGuy().action(state).strategy
        return PlayEvent(issuer_id=self.identifier, strategy=strategy)


# ======================================================================================================================

class LearningPlayer(PlayerWithHistory, ABC):
    def __init__(self):
        super().__init__()

    def update_internal_state(self, game_state: GameState, self_action: int, other_action: int):
        super().update_internal_state(game_state, self_action, other_action)
        self.learn(game_state, self_action, other_action)

    def learn(self, game_state: GameState, self_action: int, other_action: int):
        pass


class NashGuy(LearningPlayer):
    def __init__(self, num_rounds_for_collection=1) -> None:
        super().__init__()
        self.probs = {}
        self.num_rounds_for_collection = num_rounds_for_collection
        self.count_collection_rounds = 0

    def learn(self, game_state: GameState, mine_action: int, other_action: int):
        vector = game_state.vector
        opponent_id = game_state.opponent_id

        self.probs[opponent_id][vector][mine_action][1][other_action] += 1
        self.probs[opponent_id][vector][mine_action] = (
            self.probs[opponent_id][vector][mine_action][0] + 1,
            self.probs[opponent_id][vector][mine_action][1])

    def action(self, game_state: GameState) -> PlayEvent:
        max_play = None
        max_expected = None
        opponent_id = game_state.opponent_id

        opponent = self.probs.setdefault(opponent_id, {})
        plays = opponent.setdefault(game_state.vector, {})

        for i, row in enumerate(game_state.matrix):
            expected = 0
            total, counts = plays.setdefault(i, (0, {}))

            for j in range(len(row)):
                counts.setdefault(j, 0)

            if self.count_collection_rounds < self.num_rounds_for_collection:
                if i == len(game_state.matrix) - 1:
                    self.count_collection_rounds += 1
                return PlayEvent(issuer_id=self.identifier, strategy=i)

            for j, gains in enumerate(row):
                expected += gains[0] * (counts[j] / total)

            if (not max_expected) or expected > max_expected:
                max_expected = expected

                max_play = i

        return PlayEvent(issuer_id=self.identifier, strategy=max_play)


# ======================================================================================================================

class SimpleMetaHeuristicGuy(LearningPlayer):
    def __init__(self) -> None:
        super().__init__()
        self.max_avg = {}
        self.memory = {}

    def get_memory_vector_similar(self, vector, action=None):
        for id, a in self.memory.keys():
            if (action is None or action == a) and len(id) == len(vector):
                sim = cosine_similarity([vector], [id])[0][0]

                if sim > 0.9:
                    return id

        return None

    def learn(self, game_state: GameState, mine_action: int, other_action: int):
        vector = game_state.vector
        reward = game_state.matrix[mine_action][other_action][0]

        id_vector = self.get_memory_vector_similar(vector, mine_action)

        if id_vector:
            self.memory[id_vector, mine_action] = (
                self.memory[id_vector, mine_action][0] + reward, self.memory[id_vector, mine_action][1] + 1)
        else:
            self.memory[vector, mine_action] = (reward, 1)
            id_vector = vector

        sum, count = self.memory[id_vector, mine_action]
        avg = sum / count

        if id_vector in self.max_avg:
            if self.max_avg[id_vector][0] < avg:
                self.max_avg[id_vector] = (avg, mine_action)
        else:
            self.max_avg[id_vector] = (avg, mine_action)

    def action(self, game_state: GameState) -> PlayEvent:
        id_vector = self.get_memory_vector_similar(game_state.vector)

        if random.random() < 0.1 or not id_vector:  # Exploration
            strategy = RandomGuy().action(game_state).strategy
        else:  # Exploitation
            strategy = self.max_avg[id_vector][1]
        return PlayEvent(issuer_id=self.identifier, strategy=strategy)


class AnotherGeneticGuy(LearningPlayer):
    def __init__(self) -> None:
        super().__init__()
        self.history_length = 5

        self.global_population = [self.initialize_strategy() for _ in range(20)]

        for generation in range(10):
            self.global_population, fitnesses = self.evolve_population(self.global_population)

        best_fitness = max(fitnesses)
        index_best_strategy = fitnesses.index(best_fitness)
        self.best_global_strategy = self.global_population[index_best_strategy]

        self.strategy = self.best_global_strategy
        self.population = self.global_population

    def clear(self):
        self.strategy = self.best_global_strategy
        self.population = self.global_population

    def get_opponent_similar_history(self, history, vector):
        best = None
        best_sim = None

        for h_vec in history.keys():
            new_vector = vector
            new_h_vector = h_vec

            if len(vector) < len(h_vec):
                new_vector = list(vector) + [0] * (len(h_vec) - len(vector))
            elif len(vector) > len(h_vec):
                new_h_vector = list(h_vec) + [0] * (len(vector) - len(h_vec))

            sim = cosine_similarity([new_h_vector], [new_vector])[0][0]

            if (not best_sim) or sim > best_sim:
                best = h_vec
                best_sim = sim

        return best

    def fitness_local(self, strategy, matrix, vector, opponent_history, opponent_move):
        player_move = self.get_strategy_response(strategy, opponent_history, vector)
        gain = matrix[player_move][opponent_move][0]

        return gain

    def learn(self, state: GameState, mine_action: int, other_action: int):
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        shistory = self.get_opponent_similar_history(history_against_opponent, state.op_vector)

        if shistory:
            opponent_history = shistory[-self.history_length:] if len(shistory) >= self.history_length else shistory

        for generation in range(2):
            self.population, fitnesses = self.evolve_population(self.population,
                                                                lambda s, strategy, simulations=10: self.fitness_local(
                                                                    strategy, state.matrix, state.vector,
                                                                    opponent_history, other_action))

        best_fitness = max(fitnesses)
        index_best_strategy = fitnesses.index(best_fitness)
        self.strategy = self.population[index_best_strategy]

    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        shistory = self.get_opponent_similar_history(history_against_opponent, state.op_vector)

        if shistory:
            oponent_history = shistory[-self.history_length:] if len(shistory) >= self.history_length else shistory
            strategy = self.get_strategy_response(self.strategy, oponent_history, state.vector)
        else:
            strategy = GoodGuy().action(state).strategy

        return PlayEvent(issuer_id=self.identifier, strategy=strategy)

    def get_strategy_response(self, strategy, oponent_history, current_vector):
        best = None
        sim_best = None

        if len(oponent_history) < self.history_length:
            oponent_history = list(oponent_history) + [0] * (self.history_length - len(oponent_history))

        for history, vector in strategy.keys():
            new_current_vector = current_vector
            new_vector = vector

            if len(vector) < len(current_vector):
                new_vector = list(vector) + [0] * (len(current_vector) - len(vector))
            elif len(vector) > len(current_vector):
                new_current_vector = list(current_vector) + [0] * (len(vector) - len(current_vector))

            sim_history = cosine_similarity([history], [oponent_history])[0][0]
            sim_vector = cosine_similarity([new_vector], [new_current_vector])[0][0]

            avg_sim = (sim_history + sim_vector) / 2
            if (not sim_best) or avg_sim > sim_best:
                sim_best = avg_sim
                best = (history, vector)

        return int(strategy[best] % get_matrix_len(len(current_vector)))

    def initialize_strategy(self):
        strategy = {}

        for i in range(20):
            n = np.random.randint(2, 3)

            history = tuple(np.random.random_integers(0, n - 1, self.history_length))
            vector = tuple(np.random.random_integers(0, 2, get_vector_len(n)))

            response = np.random.randint(0, n)
            strategy[(history, vector)] = response
        return strategy

    def fitness(self, strategy, simulations=10):
        total_gain = 0
        for _ in range(simulations):
            matrix_structure = generate_matrix()
            matrix1, matrix2, vector1 = matrix_structure.matrix1, matrix_structure.matrix2, matrix_structure.vector1

            opponent_history = np.random.choice(range(0, len(matrix2)), size=self.history_length)
            player_move = self.get_strategy_response(strategy, opponent_history, vector1)
            opponent_move = np.random.randint(0, len(matrix2))

            total_gain += matrix1[player_move][opponent_move][0]

        return total_gain / simulations

    def mutate(self, strategy, rate=0.1):
        for history, vector in strategy.keys():
            if np.random.rand() < rate:
                strategy[history, vector] = np.random.randint(0, get_matrix_len(len(vector)))
        return strategy

    def crossover(self, parent1, parent2):
        crossover_point = np.random.randint(1, len(parent1) - 1)
        son = list(parent1.items())[:crossover_point] + list(parent2.items())[crossover_point:]
        return {key: value for key, value in son}

    def select_population(self, population, fitnesses, num_selected):
        selected = random.choices(population, weights=fitnesses, k=num_selected)
        return selected

    def evolve_population(self, population, fitness=fitness):
        new_population = []
        fitness_scores = [fitness(self, strategy) for strategy in population]

        # Selection
        selected = self.select_population(population, fitness_scores, len(population) // 2)

        while len(new_population) < len(population):
            parent1, parent2 = random.sample(selected, 2)

            # Cross
            son = self.crossover(parent1, parent2)

            # Mutation
            son = self.mutate(son)

            new_population.append(son)

        return new_population, fitness_scores


class GeneticGuy(PlayerWithHistory):
    def __init__(self) -> None:
        super().__init__()
        self.history_length = 5

        population = [self.initialize_strategy() for _ in range(20)]

        for generation in range(10):
            population, fitnesses = self.evolve_population(population)

        best_fitness = max(fitnesses)
        index_best_strategy = fitnesses.index(best_fitness)
        best_strategy = population[index_best_strategy]

        self.strategy = best_strategy

    @staticmethod
    def get_oponent_similar_history(history, vector):
        best = None
        best_sim = None

        for h_vec in history.keys():
            new_vector = vector
            new_h_vector = h_vec

            if len(vector) < len(h_vec):
                new_vector = list(vector) + [0] * (len(h_vec) - len(vector))
            elif len(vector) > len(h_vec):
                new_h_vector = list(h_vec) + [0] * (len(vector) - len(h_vec))

            sim = cosine_similarity([new_h_vector], [new_vector])[0][0]

            if (not best_sim) or sim > best_sim:
                best = h_vec
                best_sim = sim

        return best

    def action(self, state: GameState) -> PlayEvent:
        history_against_opponent: History = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        shistory = self.get_oponent_similar_history(history_against_opponent, state.vector)

        if shistory:
            oponent_history = shistory[-self.history_length:] if len(shistory) >= self.history_length else shistory
            strategy = self.get_strategy_response(self.strategy, oponent_history, state.vector)
        else:
            strategy = GoodGuy().action(state)
        return PlayEvent(issuer_id=self.identifier, strategy=strategy)

    def get_strategy_response(self, strategy, opponent_history, current_vector):
        best = None
        sim_best = None

        if len(opponent_history) < self.history_length:
            opponent_history = list(opponent_history) + [0] * (self.history_length - len(opponent_history))

        for history, vector in strategy.keys():
            new_current_vector = current_vector
            new_vector = vector

            if len(vector) < len(current_vector):
                new_vector = list(vector) + [0] * (len(current_vector) - len(vector))
            elif len(vector) > len(current_vector):
                new_current_vector = list(current_vector) + [0] * (len(vector) - len(current_vector))

            sim_history = cosine_similarity([history], [opponent_history])[0][0]
            sim_vector = cosine_similarity([new_vector], [new_current_vector])[0][0]

            avg_sim = (sim_history + sim_vector) / 2
            if (not sim_best) or avg_sim > sim_best:
                sim_best = avg_sim
                best = (history, vector)

        return int(strategy[best] % get_matrix_len(len(current_vector)))

    def initialize_strategy(self):
        strategy = {}

        for i in range(10):
            n = np.random.randint(2, 3)

            history = tuple(np.random.random_integers(0, n - 1, self.history_length))
            vector = tuple(np.random.random_integers(0, 2, get_vector_len(n)))

            response = np.random.randint(0, n)
            strategy[(history, vector)] = response
        return strategy

    def fitness(self, strategy, simulations=10):
        total_gain = 0
        for _ in range(simulations):
            matrix_structure = generate_matrix()
            matrix1, matrix2, vector1 = matrix_structure.matrix1, matrix_structure.matrix2, matrix_structure.vector1

            opponent_history = np.random.choice(range(0, len(matrix2)), size=self.history_length)
            player_move = self.get_strategy_response(strategy, opponent_history, vector1)
            opponent_move = np.random.randint(0, len(matrix2))

            total_gain += matrix1[player_move][opponent_move][0]

        return total_gain / simulations

    def mutate(self, strategy, rate=0.1):
        for history, vector in strategy.keys():
            if np.random.rand() < rate:
                strategy[history, vector] = np.random.randint(0, get_matrix_len(len(vector)))
        return strategy

    def crossover(self, parent1, parent2):
        crossover_point = np.random.randint(1, len(parent1) - 1)
        son = list(parent1.items())[:crossover_point] + list(parent2.items())[crossover_point:]
        return {key: value for key, value in son}

    def select_population(self, population, fitnesses, num_selected):
        selected = random.choices(population, weights=fitnesses, k=num_selected)
        return selected

    def evolve_population(self, population):
        new_population = []
        fitness_scores = [self.fitness(strategy) for strategy in population]

        # Selection
        selected = self.select_population(population, fitness_scores, len(population) // 2)

        while len(new_population) < len(population):
            parent1, parent2 = random.sample(selected, 2)

            # Cross
            son = self.crossover(parent1, parent2)

            # Mutation
            son = self.mutate(son)

            new_population.append(son)

        return new_population, fitness_scores


# ======================================================================================================================

class Tournament:
    def __init__(self, players: List[Player], matrices: List[MatrixStructure]):
        self.players = players
        self.scores = [0] * len(players)
        self.matrices = matrices
        self.history: Dict[Tuple[int, int], History] = {}
        self.set_players_tournament_info()

    def play(self):
        """Play the tournament."""
        self._clear()
        num_players = len(self.players)

        for i in range(num_players):
            for j in range(i + 1, num_players):
                player1 = self.players[i]
                player2 = self.players[j]
                self._play_match(player1, player2)

    def _play_match(self, player1: Player, player2: Player):
        """
        Play a match between two players. A match consists of playing all the matrices in the tournament.
        :param player1: the first player.
        :param player2: the second player.
        """
        for matrix_structure in self.matrices:
            matrix1, vector1, matrix2, vector2 = matrix_structure.matrix1, matrix_structure.vector1, matrix_structure.matrix2, matrix_structure.vector2
            game_state_1 = GameState(matrix1, vector1, matrix2, vector2, player2.identifier)
            game_state_2 = GameState(matrix2, vector2, matrix1, vector1, player1.identifier)

            action1 = player1.action(game_state_1)
            action2 = player2.action(game_state_2)

            player1.update_internal_state(game_state_1, action1.strategy, action2.strategy)
            player2.update_internal_state(game_state_2, action2.strategy, action1.strategy)

            score1, score2 = matrix_structure.matrix1[action1.strategy][action2.strategy]
            self.scores[player1.identifier] += score1
            self.scores[player2.identifier] += score2

            self.update_history(action1, action2, vector1, vector2)

    def update_history(self, play_event1: PlayEvent, play_event2: PlayEvent, vector1: Vector, vector2: Vector):
        player1 = play_event1.issuer_id
        player2 = play_event2.issuer_id
        action1 = play_event1.strategy
        action2 = play_event2.strategy

        if (player1, player2) in self.history:
            history1 = self.history[(player1, player2)]
        else:
            history1 = {}

        if (player2, player1) in self.history:
            history2 = self.history[(player2, player1)]
        else:
            history2 = {}

        history1.setdefault(vector1, []).append(action1)
        history2.setdefault(vector2, []).append(action2)

    def set_players_tournament_info(self):
        for i, player in enumerate(self.players):
            player.identifier = i

    def _clear(self):
        """Clear the scores and history for all players."""
        self.history = {}
        self.scores = [0] * len(self.players)


def print_tournament_results(tournament: Tournament, index: int = 0):
    print("-" * 50 + "Tournament " + str(index + 1) + "-" * 50)

    player_name = lambda player: player.name if player.name else f"Player {player.identifier + 1}"

    print("Scores:" + "-" * 50)
    for player, score in zip(tournament.players, tournament.scores):
        print(f"{player_name(player)} ({player.__class__.__name__}): {score} score")

    print("Winner" + "-" * 50)

    winner_index = tournament.scores.index(max(tournament.scores))
    winner = tournament.players[winner_index]
    winner_score = tournament.scores[winner_index]
    print(f"{player_name(winner)} ({winner.__class__.__name__}): {winner_score} score")

    print("Loser" + "-" * 50)

    loser_index = tournament.scores.index(min(tournament.scores))
    loser = tournament.players[loser_index]
    loser_score = tournament.scores[loser_index]
    print(f"{player_name(loser)} ({loser.__class__.__name__}): {loser_score} score")
