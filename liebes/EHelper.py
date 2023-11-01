from typing import List


class EHelper:
    def __init__(self):
        self.tokenizers = []
        self.ir_model = []

    def APFD(self, total_faults: List, test_cases_order: List) -> float:
        t = len(test_cases_order)

        # Step 1: Create a matrix/list of faults detected by each test case
        faults_detected = [[0] * total_faults for _ in range(t)]
        for i, order in enumerate(test_cases_order):
            for fault in order:
                faults_detected[i][fault - 1] = 1

        # Step 2: Calculate the number of faults detected by each test case
        faults_detected_counts = [sum(row) for row in faults_detected]

        # Step 3: Calculate the cumulative number of faults detected
        cumulative_faults_detected = [sum(faults_detected_counts[:i + 1]) for i in range(t)]

        # Step 4: Calculate the ideal cumulative number of faults detected
        ideal_cumulative_faults_detected = sorted(cumulative_faults_detected, reverse=True)

        # Step 5: Calculate the APFD score
        apfd = (sum(
            ideal_cumulative_faults_detected[i] / sum(ideal_cumulative_faults_detected) for i in range(t)) - 1) / t

        return apfd
