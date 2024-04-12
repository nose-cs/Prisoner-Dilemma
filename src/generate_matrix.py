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

def generate_matrix():
    return prisoner_dilemma_matrix()


def prisoner_dilemma_matrix():
    # We are going to sum a constant to all the values in the matrix to avoid negative values
    # Original matrix is [[(-3, -3), (0, -5)], [(-5, 0), (-1, -1)]]
    matrix = [[(2, 2), (5, 0)], [(0, 5), (4, 4)]]
    fixed_matrix = tuple(tuple(row) for row in matrix)
    return fixed_matrix, vectorize(fixed_matrix)


def battle_of_sexes_matrix():
    matrix = [[(2, 1), (0, 0)], [(0, 0), (1, 2)]]
    fixed_matrix = tuple(tuple(row) for row in matrix)
    return fixed_matrix, vectorize(fixed_matrix)


def free_money_matrix():
    matrix = [[(10, 10), (0, 0)], [(0, 0), (0, 0)]]
    fixed_matrix = tuple(tuple(row) for row in matrix)
    return fixed_matrix, vectorize(fixed_matrix)
