import textwrap

import google.generativeai as genai
from IPython.display import Markdown

from src.deserialization import decision_matrices


class GeminiClient:
    def __init__(self):
        API_KEY = 'AIzaSyD4oPew_mhZ4igkQ_3QXFtupQZ_ZVavg74'
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

    def tell_round_story(self, title, player1, player2, action1, action2, index=0, description='historia breve'):
        decision_matrix = decision_matrices[title]
        action_player_1 = decision_matrix.actions[action1]
        action_player_2 = decision_matrix.actions[action2]

        story = f"A partir del siguiente cuento"
        story += f"\nCuento: {decision_matrix.story}"

        story += f"\n\nRedacta un/una {description} en el que describas fielmente las decisiones tomadas por cada personaje que se listan a continuación"
        story += f"\n{player1}: '{action_player_1}'."
        story += f"\n{player2}: '{action_player_2}'."

        story += f"\n\nTen en cuenta que {player1} y {player2} son personas. Además ambos toman la decisión sin conocer la decisión del otro."

        response = self.client.generate_content(story)

        return self.to_markdown(f"### Round {index}\n\n" + response.text)
