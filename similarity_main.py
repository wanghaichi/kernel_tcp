import math
import random
import pathlib
from liebes.CiObjects import *
import numpy as np
from liebes.analysis import CIAnalysis
from liebes.EHelper import EHelper
from liebes.sql_helper import SQLHelper
from liebes.ci_logger import logger
from liebes.tcp_approach import adaptive_random_prior
import os
import threading
import time
import multiprocessing as mp

def do_exp4(params):
    adaptive_random_prior.do_exp4(params[0], params[1], params[2], params[3], params[4])

def do_exp3(params):
    adaptive_random_prior.do_exp3(params[0], params[1], params[2])

def do_exp2(params):
    adaptive_random_prior.do_exp2(params[0], params[1], params[2], params[3])

def do_exp5(params):
    adaptive_random_prior.do_exp5(params[0], params[1], params[2])

if __name__ == '__main__':
    # linux_path = '/home/wanghaichi/linux-1'
    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(600).all()
    # cia = CIAnalysis()
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.set_parallel_number(40)
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # cia.filter_job("FILTER_NOFILE_CASE")
    # cia.ci_objs = cia.ci_objs[1:]
    # cia.statistic_data()

    distance_metrics = [
        'hanming_distance',
        'edit_distance',
        'euclidean_string_distance',
        'manhattan_string_distance',
        'normalized_compression_distance'
    ]

    k = 10

    candidate_strategies = [
        'min_max'
    ]

    ltp_version = [
        '20220121',
        '20220527',
        '20220930',
        '20230127',
        '20230516',
        '20230929',
        '20240129'
    ]

    context_strategy = "default"

    # params_list = []
    # summary = []
    # for distance_metric in distance_metrics:
    #     for candidate_strategy in candidate_strategies:
    #         params_list.append((r'', 10, distance_metric, candidate_strategy))
    #         res = adaptive_random_prior.do_exp2(r'/home/duyiheng/projects/kernel-tcp/logs/flaky_info.txt', 10, distance_metric, candidate_strategy)
    #         summary.append(res)
    # logger.info("summary :---------------------------------")
    # for s in summary:
    #     logger.info(s)

    params_list = []
    for distance_metric in distance_metrics:
        params_list.append((k, distance_metric, candidate_strategies[0]))
            # res = adaptive_random_prior.do_exp4(r'/home/duyiheng/projects/kernel-tcp/logs/flaky_info.txt', 10, distance_metric, 'min_max', version)
            # adaptive_random_prior.do_exp3(r'/home/duyiheng/projects/kernel-tcp/logs/flaky_info.txt', distance_metric, version)
            # summary.append(res)

    pool = mp.Pool()
    pool.map(do_exp5, params_list)
    pool.close()
    pool.join()