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
    # n = np.random.randint(2, 4)
    # matrix = [[(np.random.randint(-5, 5), np.random.randint(-5, 5)) if k >= j else 0 for k in range(n)] for j in range(n)]

    # for i in range(n):
    #     for j in range(n):
    #         if j < i:
    #             matrix[i][j] = (matrix[j][i][1], matrix[j][i][0])
    #         elif j == i:
    #             matrix[i][j] = (matrix[i][j][0], matrix[i][j][0])
    #         else:
    #             break

    matrix = [[(3, 3), (0, 5)], [(5, 0), (1, 1)]]

    fixed_matrix = tuple(tuple(row) for row in matrix)

    return (fixed_matrix, vectorize(fixed_matrix))
