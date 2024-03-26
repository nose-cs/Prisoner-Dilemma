from players.player import Player
import random
import numpy

class SimpleMetaHeuristicGuy(Player):
    def __init__(self) -> None:
        super().__init__()
        self.memory = {'C': 0, 'T': 0}

    def sum_years(self, action: str, years: int):
        super().sum_years(action, years)
        self.memory[action] += years
    
    def clear(self):
        super().clear()
        self.memory = {'C': 0, 'T': 0}

    def play(self, index_player, full_history: list[list], history: list) -> str:
        if random.random() < 0.1:  # Exploration
            return random.choice(['C', 'T'])
        else:  # Exploitation
            return 'C' if self.memory['C'] < self.memory['T'] else 'T'
        
class GeneticGuy(Player):
    def __init__(self, simulate_tournament, num_rounds: int, oponents: list[Player], plays=None) -> None:
        super().__init__()
        if not plays:
            self.plays = [self.get_plays(simulate_tournament, num_rounds, oponent) for oponent in oponents]
        else:
            self.plays = plays

    def play(self, index_player, full_history: list[list], history: list) -> str:
        return self.plays[index_player][len(history)]

    def get_plays(self, simulate_tournament, num_rounds, oponent):
        def generate_strategy():
            return [random.choice(['C', 'T']) for _ in range(num_rounds)]

        def fitness(strategy, oponent):
            me = GeneticGuy(None, None, None, [strategy])
            simulate_tournament([oponent, me], num_rounds)
            oponent.clear()
            return me.years

        def select_population(population, fitnesses, num_selected):
            selected = random.choices(population, weights=fitnesses, k=num_selected)
            return selected

        def cross(strategy1, strategy2):
            point_break = random.randint(1, len(strategy1) - 1)
            son = strategy1[:point_break] + strategy2[point_break:]
            return son

        def mutate(strategy, mutation_rate=0.05):
            for i in range(len(strategy)):
                if random.random() < mutation_rate:
                    strategy[i] = 'C' if strategy[i] == 'T' else 'T'
            return strategy

        population = None
        new_generation = [generate_strategy() for _ in range(500)]
        
        for generation in range(50):
            population = new_generation

            fitnesses = numpy.array([fitness(s, oponent) for s in population])

            fitnesses -= numpy.max(fitnesses)
            fitnesses *= -1

            fitnesses = fitnesses.tolist()

            selected = select_population(population, fitnesses, len(population) // 2)
            
            new_generation = []
            while len(new_generation) < len(population):
                father1, father2 = random.sample(selected, 2)
                son = cross(father1, father2)
                son = mutate(son)
                new_generation.append(son)

        best_fitness = max(fitnesses)
        index_best_strategy = fitnesses.index(best_fitness)
        best_strategy = population[index_best_strategy]

        print(best_strategy)
        return best_strategy
