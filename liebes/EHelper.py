from typing import List
import json


class EHelper:
    def __init__(self):
        self.tokenizers = []
        self.ir_model = []

    def APFD(self, total_faults: List, test_cases_order: List) -> float:
        if len(total_faults) == 0 or len(test_cases_order) == 0:
            return 0.5
        res = 0.0
        for i in range(len(test_cases_order)):
            if test_cases_order[i] in total_faults:
                res += i + 1
        res /= (len(total_faults) * len(test_cases_order))
        res = 1 - res
        res += 1 / (2 * len(test_cases_order))
        return res
    
    def get_ltp_version(git_sha: str):
        with open(r'checkout_ltp_version_map.json', r'r') as f:
            data = json.load(f)
        f.close()

        return data.get(git_sha)
