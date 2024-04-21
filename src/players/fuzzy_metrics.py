class FuzzyFunctions:
    @staticmethod
    def envy(Matrix, Row):
        cand = 0
        for tuple in Matrix[Row]:
            if (tuple[0] == 0):  return 1
            cand = max(cand, (tuple[1] / tuple[0]))
        return min(cand, 1)

    @staticmethod
    def sub_joint(Matrix, Row):
        max_joint = -1000000
        expected_share = -10000000
        min_dif = 10000000
        for row in Matrix:
            for tuple in row:
                if (tuple[0] + tuple[1] > max_joint):
                    max_joint = tuple[0] + tuple[1]
                    expected_share = tuple[1]
                    min_dif = abs((tuple[0] + tuple[1]) / 2 - tuple[0])
                elif (tuple[0] + tuple[1] == max_joint):
                    avg = (tuple[0] + tuple[1]) / 2
                    if (abs(tuple[0] - avg < min_dif)):
                        min_dif = abs(tuple[0] - avg < min_dif)
                        expected_share = tuple[1]

        max_row_share = -10000000
        for tuple in Matrix[Row]:
            max_row_share = max(max_row_share, tuple[1])

        return (min(1, max_row_share / expected_share))

    @staticmethod
    def dif_sum_rows(Matrix, Row):
        max_sum = 0
        max_sum_index = 0
        min_dif_in_max_sum = 100000000
        for index, row in enumerate(Matrix):
            total_sum = sum(map(sum, row))
            if (total_sum > max_sum):
                max_sum = total_sum
                max_sum_index = index
                min_dif_in_max_sum = abs(total_sum / 2 - sum(map(lambda x: x[1], row)))
            elif (total_sum == max_sum):
                dif = abs(total_sum / 2 - sum(map(lambda x: x[1], row)))
                if (dif < min_dif_in_max_sum):
                    max_sum_index = index
                    min_dif_in_max_sum = dif

        return min(1, sum(map(lambda x: x[1], Matrix[Row])) / sum(map(lambda x: x[1], Matrix[max_sum_index])))
