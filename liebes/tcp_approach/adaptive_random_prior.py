import math
import sys
import random
import pathlib
from liebes.CiObjects import *
import numpy as np
from liebes.analysis import CIAnalysis
from liebes.EHelper import EHelper
from liebes.sql_helper import SQLHelper
from liebes.ci_logger import logger

distance_map = {}

def euclidean_string_distance(s1, s2):
    len_diff = abs(len(s1) - len(s2))
    if len(s1) < len(s2):
        s1 += '\0' * len_diff
    elif len(s1) > len(s2):
        s2 += '\0' * len_diff
    point1 = [ord(char) for char in s1]
    point2 = [ord(char) for char in s2]
    squared_diff = sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2))
    return math.sqrt(squared_diff)

def jaccard_distance_function(set1, set2):
    set1 = set(set1)
    set2 = set(set2)
    intersection = len(set1.intersection(set2))
    union = len(set1.union(set2))

    distance = 1 - intersection / union
    return distance

def manhattan_string_distance(s1, s2):
    len_diff = abs(len(s1) - len(s2))
    if len(s1) < len(s2):
        s1 += '\0' * len_diff
    elif len(s1) > len(s2):
        s2 += '\0' * len_diff
    point1 = [ord(char) for char in s1]
    point2 = [ord(char) for char in s2]

    distance = 0
    for i in range(len(point1)):
        distance += abs(point1[i] - point2[i])
    return distance

def edit_distance(s1, s2):
    m, n = len(s1), len(s2)
    dp = [[0] * (n + 1) for _ in range(m + 1)]

    for i in range(m + 1):
        dp[i][0] = i
    for j in range(n + 1):
        dp[0][j] = j

    for i in range(1, m + 1):
        for j in range(1, n + 1):
            if s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]
            else:
                dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + 1)

    return dp[m][n]

def hanming_distance(s1, s2):
    len_diff = abs(len(s1) - len(s2))
    if len(s1) < len(s2):
        s1 += '\0' * len_diff
    elif len(s1) > len(s2):
        s2 += '\0' * len_diff
    distance = 0
    for i in range(len(s1)):
        if s1[i] != s2[i]:
            distance += 1
    return distance

def ARP(test_cases: list[Test], k: int, distance_metric: str, candidate_stragety: str):
    if distance_metric is None:
        distance_metric = 'edit_distance'
    if candidate_stragety is None:
        candidate_stragety = 'min_max'

    candidate_list = []
    prioritized_list = []
    test_cases_len = len(test_cases)
    idx_list = list(range(0, test_cases_len))
    first_idx = random.choice(idx_list)
    prioritized_list.append(first_idx)
    idx_list.remove(first_idx)
    idx_list_len = len(idx_list)
    while idx_list_len != 0:
        candidate_list = []
        k = min(k, idx_list_len)
        candidate_list = random.sample(idx_list, k)
        d = [[0] * len(candidate_list) for _ in range(len(prioritized_list))]
        col = 0
        for candidate_idx in candidate_list:
            candidate = test_cases[candidate_idx]
            row = 0
            for p_idx in prioritized_list:
                pt = test_cases[p_idx]
                distance = distance_map.get(pt.file_path, {}).get(candidate.file_path, None)
                if distance is None:
                    candidate_text = Path(candidate.file_path).read_text(encoding='utf-8', errors='ignore')
                    pt_text = Path(pt.file_path).read_text(encoding='utf-8', errors='ignore')
                    if distance_metric == 'edit_distance':
                        distance = edit_distance(candidate_text, pt_text)
                    elif distance_metric == 'hanming_distance':
                        distance = hanming_distance(candidate_text, pt_text)

                    tmp_dict = distance_map.get(pt.file_path, {})
                    tmp_dict[candidate.file_path] = distance
                    distance_map[pt.file_path] = tmp_dict
                d[row][col] = distance
                row += 1
            col += 1
        
        if candidate_stragety == 'min_max':
            neighbours = list(np.min(d, axis=0))
            max_idx = neighbours.index(max(neighbours))
            next_pt_idx = candidate_list[max_idx]
        
        prioritized_list.append(next_pt_idx)
        idx_list.remove(next_pt_idx)
        idx_list_len -= 1
        print(idx_list_len)

    return prioritized_list

def do_exp(cia: CIAnalysis, k: int, distance_metric: str, candidate_stragety: str):
    ehelper = EHelper()
    apfd_res = []
    for ci_index in range(1, len(cia.ci_objs)):
        ci_obj = cia.ci_objs[ci_index]
        last_ci_obj = cia.ci_objs[ci_index - 1]
        # start iteration of one test result
        # 1. first extract the faults result
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if test_cases[i].is_failed():
                faults_arr.append(i)
        if len(faults_arr) == 0:
            continue

        prioritized_list = ARP(test_cases, k, distance_metric, candidate_stragety)
        apfd_v = ehelper.APFD(faults_arr, prioritized_list)
        logger.debug(f"distance_metric: {distance_metric}, commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}")
        apfd_res.append(apfd_v)
    logger.info(f"distance_metric: {distance_metric}, candidate_stragety: {candidate_stragety}, avg apfd: {np.average(apfd_res)}")
    return f"distance_metric: {distance_metric}, candidate_stragety: {candidate_stragety}, avg apfd: {np.average(apfd_res)}"

# if __name__ == '__main__':
#     linux_path = '/home/wanghaichi/linux-1'
#     sql = SQLHelper()
#     checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(20).all()
#     cia = CIAnalysis()
#     for ch in checkouts:
#         cia.ci_objs.append(Checkout(ch))
#     cia.reorder()
#     cia.set_parallel_number(40)
#     cia.filter_job("COMBINE_SAME_CASE")
#     cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
#     cia.ci_objs = cia.ci_objs[1:]
#     cia.statistic_data()

#     distance_metrics = [
#         'edit_distance'
#     ]

#     k = 10

#     candidate_strategies = [
#         'min_max'
#     ]

#     context_strategy = "default"
#     # tokenizer = AstTokenizer()
#     # ir_model = TfIdfModel()
#     # TODO 加个多线程的方式
#     summary = []
#     for distance_metric in distance_metrics:
#         for candidate_strategy in candidate_strategies:
#             res = do_exp(cia, k, distance_metric, candidate_strategy)
#             summary.append(res)
#     logger.info("summary :---------------------------------")
#     for s in summary:
#         logger.info(s)