class FuzzyFunctions:
    def envy(Matrix, Row):
        cand = 0
        for tuple in Matrix[Row]:
            cand = max(cand, (tuple[1]/ tuple[0]))
        return min(cand, 1)
    
    def sub_joint(Matrix, Row):
        max_joint = -1000000
        expected_share = -10000000
        min_dif = 10000000
        for i in Matrix:
            for tuple in Matrix[i]:
                if(tuple[0] + tuple[1] > max_joint):
                    max_joint = tuple[0] + tuple[1]
                    expected_share = tuple[1] 
                    min_dif = 10000000
                elif(tuple[0] + tuple[1] == max_joint):
                    avg = (tuple[0] + tuple[1])/2
                    if(abs(tuple[0] - avg < min_dif)):
                        min_dif = abs(tuple[0] - avg < min_dif)
                        expected_share = tuple[1]

        max_row_share = -10000000
        for tuple in Matrix[Row]:
            max_row_share = max(max_row_share, tuple[1])

        return (min(1, max_row_share/ expected_share))





