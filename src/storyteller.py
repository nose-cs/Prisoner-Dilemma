import textwrap
from typing import List, Tuple

import google.generativeai as genai
from IPython.display import Markdown

from src.deserialization import decision_matrices
from src.players import Player


class GeminiClient:
    def __init__(self):
        API_KEY = 'AIzaSyBdMrVOCjzemRTjvM_BMWuyf6iZRbisWUc'
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

    def tell_round_story(self, title, player1: Player, player2: Player, action1, action2, index=0,
                         description='historia breve'):
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
                         actions: List[Tuple[int, int]], index=0, description='historia breve'):
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
