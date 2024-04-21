import textwrap
from typing import List, Tuple, Dict

import google.generativeai as genai
from IPython.display import Markdown

from src.decision_matrices_deserialization import decision_matrices
from src.players import Player

Vector = Tuple[int, int]
History = Dict[Vector, List[int]]


class GeminiClient:
    def __init__(self):
        API_KEY = 'AIzaSyCl_qFkDcVMJHWeeQsG9woFDrSTLDG6rmg'
        genai.configure(api_key=API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')

    def generate_content(self, prompt: str):
        return self.model.generate_content(prompt)


class StoryTeller:
    def __init__(self):
        self.client = GeminiClient()

    @staticmethod
    def to_markdown(text):
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    def tell_round_story(self, title: str, player1: Player, player2: Player, action1: int, action2: int, index: int = 0,
                         description: str = 'historia breve') -> Markdown:
        """
        Generates a story for a round based on the decision matrix.
        :param title: the title of the decision matrix.
        :param player1: the first player.
        :param player2: the second player.
        :param action1: the action of the first player.
        :param action2: the action of the second player.
        :param index: the index of the round.
        :param description: the description of the story.
        :return: the story.
        """
        decision_matrix = decision_matrices[title]
        action_player_1 = decision_matrix.actions[action1]
        action_player_2 = decision_matrix.actions[action2]
        player1_name = player1.name
        player2_name = player2.name

        story = f"A partir del siguiente cuento"
        story += f"\nCuento: {decision_matrix.story}"

        story += f"\n\nRedacta un/una {description} en el que describas fielmente las decisiones tomadas por cada personaje que se listan a continuación"
        story += f"\n{player1_name}: '{action_player_1}'."
        story += f"\n{player2_name}: '{action_player_2}'."

        story += f"\n\nTen en cuenta que {player1_name} y {player2_name} son personas. Además ambos toman la decisión sin conocer la decisión del otro."

        response = self.client.generate_content(story)

        return self.to_markdown(f"### Round {index}\n\n" + response.text)

    def tell_match_story(self, titles: List[str], player1: Player, player2: Player,
                         actions: List[Tuple[int, int]], index: int = 0, description: str = 'historia breve'):
        """
        Generates a story for a match based on the decision matrices and the actions taken by the players on each round.
        :param titles: the titles of the decision matrices.
        :param player1: the first player.
        :param player2: the second player.
        :param actions: the actions taken by the players on each round.
        :param index: the index of the match.
        :param description: the description of the story.
        :return: the story.
        """
        player1_name = player1.name
        player2_name = player2.name

        match_story = f"Redacta un {description} en el que describas cada round."
        match_story += f"\nEmpieza describiendo quiénes son los personajes {player1_name} y {player2_name}."
        match_story += f"\nTen en cuenta que {player1_name} y {player2_name} son personas."
        match_story += "\nLuego narra qué ocurrió entre nuestros personajes en cada round."

        stories = []
        for i, (title, actions) in enumerate(zip(titles, actions)):
            action1, action2 = actions
            decision_matrix = decision_matrices[title]
            action_player_1 = decision_matrix.actions[action1]
            action_player_2 = decision_matrix.actions[action2]

            story = f"A partir del siguiente cuento"
            story += f"\nCuento: {decision_matrix.story}"

            if i != 0:
                story += f"\n\nDescribe una situación entre nuestros personajes que enlace el round {i} con el round {i + 1}."

            story += f"\n\nEn esta ronda las decisiones tomadas por cada personaje fueron:"
            story += f"\n{player1_name}: '{action_player_1}'."
            story += f"\n{player2_name}: '{action_player_2}'."

            story += f"\n\nTen en cuenta que ambos toman la decisión sin conocer la decisión del otro."

            stories.append(story)

        for i, story in enumerate(stories):
            match_story += f"\n\n### Round {i + 1}\n" + story + "\n\n"

        response = self.client.generate_content(match_story)
        return self.to_markdown(f"## Match {index}\n\n" + response.text)


class Stratascriptor:
    def __init__(self):
        self.client = GeminiClient()

    @staticmethod
    def to_markdown(text):
        text = text.replace('•', '  *')
        return Markdown(textwrap.indent(text, '> ', predicate=lambda _: True))

    def describe_strategy_based_on_vectors(self, history: History):
        prompt = f"Describe la estrategia del jugador a partir del siguiente historial de decisiones.\n"

        prompt += '''
            El vector representa las relaciones de orden entre los elementos de la matriz de decisión.
          
            El vector resultante se forma recorriendo cada elemento de la matriz y comparándolo con su vecino derecho y su vecino inferior. La comparación se realiza en términos de ganancias:
            
            Si el elemento actual es mayor que su vecino, se interpreta como una mayor ganancia y se asigna un valor de 2 al vector.
            Si el elemento actual es menor que su vecino, s, se interpreta como una menor ganancia y se asigna un valor de 0.
            Si el elemento actual es igual que su vecino, se asigna un valor de 1.
            
            Por ejemplo, si tienes la siguiente matriz:
            
            [[3, 1, 4],
             [5, 2, 6],
             [9, 8, 7]]
            El vector resultante sería (0, 0, 2, 2, 2, 2, 0, 0, 0, 2, 0, 0).
        '''

        for vector, actions in history.items():
            prompt += f"\n\nCon el vector {vector} tomo las siguientes decisiones:\n"
            prompt += '\n'.join([f"{i + 1} {action}" for (i, action) in enumerate(actions)])

        prompt += 'No describas que es el vector, solo la aparente estrategia del jugador y por qué toman esa decisión basandoté en el significado del vector'

        response = self.client.generate_content(prompt)

        return response.text

    def describe_strategy_1(self, matrices: Tuple[List[List[Tuple[float, float]]], List[Tuple[int, int]]]):
        prompt = f"Describe la estrategia del jugador a partir del siguiente historial de decisiones.\n"

        for matrix, actions in matrices:
            prompt += f"\n\nCon la matriz {matrix} el jugador eligió las siguientes filas:"
            for i, action in enumerate(actions):
                mine_action, opponent_action = action
                prompt += f"{i + 1} Round: fila {mine_action}, su oponente jugó en la columna {opponent_action}\n"
                prompt += f"El jugador recibió una ganancia de {matrix[mine_action][opponent_action][0]}"

        prompt += '\n\nDescribe la aparente estrategia del jugador y por qué toma esa decisión.'

        response = self.client.generate_content(prompt)

        return response.text

    def describe_strategy(self, matrices):
        prompt = f"Describe la estrategia del jugador a partir del siguiente historial de decisiones.\n"

        for value in matrices:
            matrix = value[0]
            prompt += f"\n\nCon la matriz {matrix} el jugador eligió las siguientes filas:"
            mine_actions, opponent_actions = zip(*value[1])
            prompt += f"{mine_actions}\n"
            prompt += "Su oponente eligió las siguientes columnas:"
            prompt += f"{opponent_actions}\n"
            prompt += f"La posición i de la lista de acciones corresponde al round i.\n"
            prompt += "El jugador recibió las siguientes ganancias:"
            gains = [matrix[mine_action][opponent_action][0] for (mine_action, opponent_action) in
                     zip(mine_actions, opponent_actions)]
            prompt += f"{gains}"

        prompt += "\n\nDescribe la aparente estrategia del jugador, basándote en su historial y en el de su oponente."
        prompt += "\nExplica por qué toma esa decisión."

        response = self.client.generate_content(prompt)

        return response.text
