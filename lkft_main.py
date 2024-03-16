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

if __name__ == '__main__':
    linux_path = '/home/wanghaichi/linux-1'
    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(600).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_NOFILE_CASE")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.ci_objs = cia.ci_objs[1:]
    cia.statistic_data()

    distance_metrics = [
        # 'hanming_distance',
        'edit_distance',
        'euclidean_string_distance',
        'manhattan_string_distance'
    ]

    k = 10

    candidate_strategies = [
        'min_max'
    ]

    context_strategy = "default"
    # tokenizer = AstTokenizer()
    # ir_model = TfIdfModel()
    # TODO 加个多线程的方式
    summary = []
    for distance_metric in distance_metrics:
        for candidate_strategy in candidate_strategies:
            res = adaptive_random_prior.do_exp(cia, k, distance_metric, candidate_strategy)
            summary.append(res)
    logger.info("summary :---------------------------------")
    for s in summary:
        logger.info(s)