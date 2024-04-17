import json
from typing import List, Tuple

decision_matrices_json = json.load(open('src/data.json', 'r'))


class DecisionMatrix:
    def __init__(self, title, matrix, actions, story):
        self.title = title
        self.matrix = self.fix_matrix(matrix)
        self.actions = actions
        self.story = story

    def fix_matrix(self, matrix: List[List[List[int]]]) -> List[List[Tuple[int]]]:
        normalized_matrix = self.normalize_matrix_data(matrix)
        return [[tuple(cell) for cell in row] for row in normalized_matrix]

    @staticmethod
    def normalize_matrix_data(matrix: List[List[List[int]]]) -> List[List[List[int]]]:
        """Normalizes the matrix data."""
        min_element = min(element for row in matrix for cell in row for element in cell)
        if min_element < 0:
            return [[[element + abs(min_element) for element in cell] for cell in row] for row in matrix]
        return matrix

    def __str__(self):
        return f"Title: {self.title}\nMatrix: {self.matrix}\nActions: {self.actions}\nStory: {self.story}"


decision_matrices = []
for matrix_data in decision_matrices_json:
    matrix = DecisionMatrix(matrix_data["title"], matrix_data["matrix"], matrix_data["actions"], matrix_data["story"])
    decision_matrices.append(matrix)
