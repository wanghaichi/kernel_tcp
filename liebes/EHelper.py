from typing import List


class EHelper:
    def __init__(self):
        self.tokenizers = []
        self.ir_model = []

    def APFD(self, total_faults: List, test_cases_order: List) -> float:
        res = 0.0
        for i in range(len(test_cases_order)):
            if test_cases_order[i] in total_faults:
                res += i
        res /= (len(total_faults) * len(test_cases_order))
        res = 1 - res
        res += 1 / (2 * len(test_cases_order))
        return res
