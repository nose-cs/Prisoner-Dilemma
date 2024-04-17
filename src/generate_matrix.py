from typing import List, Tuple

from deserialization import decision_matrices

Matrix = List[List[Tuple[float, float]]]
Vector = Tuple[int, int]


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
            transposed[j][i] = matrix[i][j]

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


def generate_matrices(titles: List[str]) -> (Matrix, Vector, Matrix, Vector):
    for title in titles:
        decision_matrix = decision_matrices[title]
        matrix1 = decision_matrix.matrix
        vector1 = vectorize(matrix1)
        matrix2 = transpose(matrix1) if not is_symmetric(matrix1) else matrix1
        vector2 = vectorize(matrix2)
        yield matrix1, vector1, matrix2, vector2


x = generate_matrices(['Cuento sobre decisiones en un concurso de cocina'])
for y in x:
    print(y)
