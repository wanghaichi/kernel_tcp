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
from liebes.tcp_approach.metric_manager import DistanceMetric
distance_map = {}

def ARP(test_cases: list[Test], k: int, distance_metric: str, candidate_stragety: str):

    dm = DistanceMetric()

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
                    # if Path(candidate.file_path).is_dir():
                    #     print(candidate.instance.id, candidate.file_path, candidate.instance.path)
                    candidate_text = Path(candidate.file_path).read_text(encoding='utf-8', errors='ignore')
                    pt_text = Path(pt.file_path).read_text(encoding='utf-8', errors='ignore')
                    if distance_metric == 'edit_distance':
                        distance = dm.edit_distance(candidate_text, pt_text)
                    elif distance_metric == 'hanming_distance':
                        distance = dm.hanming_distance(candidate_text, pt_text)

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
        # print(idx_list_len)

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
    logger.info(
        f"distance_metric: {distance_metric}, candidate_stragety: {candidate_stragety}, avg apfd: {np.average(apfd_res)}")
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
