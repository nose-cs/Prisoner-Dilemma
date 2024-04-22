import random
from dataclasses import dataclass
from typing import List, Tuple

from src.decision_matrices_deserialization import decision_matrices

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple


@dataclass
class MatrixStructure:
    """
    Represents a decision matrix.

    Attributes:
        matrix1 (Matrix): The matrix for the first player.
        vector1 (Vector): The vector that represents the first matrix.
        matrix2 (Matrix): The matrix for the second player.
        vector2 (Vector): The vector that represents the second matrix.
        matrix_title (str): The title of the matrix.
    """
    matrix1: Matrix
    vector1: Vector
    matrix2: Matrix
    vector2: Vector
    matrix_title: str


def get_matrix_len(len_vector):
    return (2 + (4 + 8 * len_vector) ** 0.5) / 4


def get_vector_len(len_matrix):
    return 2 * (len_matrix ** 2) - 2 * len_matrix


def vectorize(matrix):
    vector = []
    for i in range(len(matrix)):
        for j in range(len(matrix[0])):
            # Check Right
            if j + 1 < len(matrix[0]):
                if matrix[i][j] > matrix[i][j + 1]:
                    vector.append(2)
                elif matrix[i][j] < matrix[i][j + 1]:
                    vector.append(0)
                else:
                    vector.append(1)
            # Check Down
            if i + 1 < len(matrix):
                if matrix[i][j] > matrix[i + 1][j]:
                    vector.append(2)
                elif matrix[i][j] < matrix[i + 1][j]:
                    vector.append(0)
                else:
                    vector.append(1)
    return tuple(vector)


def transpose(matrix: Matrix) -> Matrix:
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    transposed: Matrix = [[(0, 0) for _ in range(num_rows)] for _ in range(num_cols)]

    for i in range(num_rows):
        for j in range(num_cols):
            first, second = matrix[i][j]
            transposed[j][i] = (second, first)

    return transposed


def is_symmetric(matrix: Matrix) -> bool:
    num_rows = len(matrix)
    num_cols = len(matrix[0])

    for i in range(num_rows):
        for j in range(num_cols):
            first, second = matrix[j][i]
            if (second, first) != matrix[i][j]:
                return False

    return True


def get_matrices(titles: List[str]) -> List[MatrixStructure]:
    """
    Get the matrices for the given titles.
    :param titles: The titles of the matrices.
    :return: The matrices.
    """
    matrices = []
    for title in titles:
        decision_matrix = decision_matrices[title]
        matrix1: Matrix = decision_matrix.matrix
        vector1: Vector = vectorize(matrix1)
        matrix2: Matrix = matrix1 if is_symmetric(matrix1) else transpose(matrix1)
        vector2: Vector = vector1 if is_symmetric(matrix1) else vectorize(matrix2)
        matrices.append(MatrixStructure(matrix1, vector1, matrix2, vector2, title))
    return matrices


def get_random_matrices(count: int = 10) -> List[MatrixStructure]:
    decision_titles = list(decision_matrices.keys())
    selected_decision_titles = random.choices(decision_titles, k=count)
    return get_matrices(selected_decision_titles)


def generate_matrix():
    decision_titles = list(decision_matrices.keys())
    random.shuffle(decision_titles)
    for matrix in get_matrices(decision_titles[:1]):
        return matrix
