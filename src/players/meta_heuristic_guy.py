import random

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.generate_matrix import get_matrix_len, get_vector_len, generate_matrix
from src.players import GoodGuy, GameState, LearningPlayer, PlayEvent, RandomGuy, PlayerWithHistory


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
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}
        shistory = self.get_oponent_similar_history(history_against_opponent, state.vector)

        if shistory:
            oponent_history = shistory[-self.history_length:] if len(shistory) >= self.history_length else shistory
            strategy = self.get_strategy_response(self.strategy, oponent_history, state.vector)
        else:
            strategy = GoodGuy().action(state).strategy
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
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}
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
        history_against_opponent = self.history[state.opponent_id] if state.opponent_id in self.history else {}
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
