import random

import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from src.generate_matrix import get_matrix_len, get_vector_len, generate_matrix
from src.players import Player, Random, GoodGuy, GameState


class SimpleMetaHeuristicGuy(Player):
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

    def sum_score(self, matrix, mine_action: int, other_action: int, score: int):
        super().sum_score(matrix, mine_action, score)

        _, vector = matrix

        id_vector = self.get_memory_vector_similar(vector, mine_action)

        if id_vector:
            self.memory[id_vector, mine_action] = (
                self.memory[id_vector, mine_action][0] + score, self.memory[id_vector, mine_action][1] + 1)
        else:
            self.memory[vector, mine_action] = (score, 1)
            id_vector = vector

        sum, count = self.memory[id_vector, mine_action]
        avg = sum / count

        if id_vector in self.max_avg:
            if self.max_avg[id_vector][0] < avg:
                self.max_avg[id_vector] = (avg, mine_action)
        else:
            self.max_avg[id_vector] = (avg, mine_action)

    def clear(self):
        super().clear()
        self.max_avg = {}
        self.memory = {}

    def play(self, game_state: GameState) -> int:
        id_vector = self.get_memory_vector_similar(game_state.vector)

        if random.random() < 0.1 or not id_vector:  # Exploration
            return Random().play(game_state)
        else:  # Exploitation
            return self.max_avg[id_vector][1]


class GeneticGuy(Player):
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

    def get_oponent_similar_history(self, history, vector):
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

    def play(self, game_state: GameState) -> int:
        shistory = self.get_oponent_similar_history(game_state.history, game_state.vector)

        if shistory:
            oponent_history = shistory[-self.history_length:] if len(shistory) >= self.history_length else shistory
            return self.getStrategyResponse(self.strategy, oponent_history, game_state.vector)

        return GoodGuy().play(game_state)

    def getStrategyResponse(self, strategy, oponent_history, current_vector):
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
            gain_matrix, vector_matrix = generate_matrix()

            opponent_history = np.random.choice(range(0, len(gain_matrix)), size=self.history_length)
            player_move = self.getStrategyResponse(strategy, opponent_history, vector_matrix)
            opponent_move = np.random.randint(0, len(gain_matrix))

            total_gain += gain_matrix[player_move][opponent_move][0]

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
        # selected_indices = np.argsort(fitness_scores)[-len(population)//2:]
        selected = self.select_population(population, fitness_scores, len(population) // 2)

        while len(new_population) < len(population):
            parent1, parent2 = random.sample(selected, 2)
            # parent1, parent2 = population[index1], population[index2]

            # Cross
            son = self.crossover(parent1, parent2)

            # Mutation
            son = self.mutate(son)

            new_population.append(son)

        return new_population, fitness_scores

    # def get_plays(self, simulate_tournament, num_rounds, oponent):
    #     def generate_strategy():
    #         return [random.choice(['C', 'T']) for _ in range(num_rounds)]

    #     def fitness(strategy, oponent):
    #         me = GeneticGuy(None, None, None, [strategy])
    #         simulate_tournament([oponent, me], num_rounds)
    #         oponent.clear()
    #         return me.years

    #     def select_population(population, fitnesses, num_selected):
    #         selected = random.choices(population, weights=fitnesses, k=num_selected)
    #         return selected

    #     def cross(strategy1, strategy2):
    #         point_break = random.randint(1, len(strategy1) - 1)
    #         son = strategy1[:point_break] + strategy2[point_break:]
    #         return son

    #     def mutate(strategy, mutation_rate=0.05):
    #         for i in range(len(strategy)):
    #             if random.random() < mutation_rate:
    #                 strategy[i] = 'C' if strategy[i] == 'T' else 'T'
    #         return strategy

    #     population = None
    #     new_generation = [generate_strategy() for _ in range(500)]

    #     for generation in range(50):
    #         population = new_generation

    #         fitnesses = numpy.array([fitness(s, oponent) for s in population])

    #         fitnesses -= numpy.max(fitnesses)
    #         fitnesses *= -1

    #         fitnesses = fitnesses.tolist()

    #         selected = select_population(population, fitnesses, len(population) // 2)

    #         new_generation = []
    #         while len(new_generation) < len(population):
    #             father1, father2 = random.sample(selected, 2)
    #             son = cross(father1, father2)
    #             son = mutate(son)
    #             new_generation.append(son)

    #     best_fitness = max(fitnesses)
    #     index_best_strategy = fitnesses.index(best_fitness)
    #     best_strategy = population[index_best_strategy]

    #     print(best_strategy)
    #     return best_strategy
