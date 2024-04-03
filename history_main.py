import argparse
import pickle
from pathlib import Path

import numpy as np

from liebes.CiObjects import DBCheckout, Checkout
from liebes.EHelper import EHelper
from liebes.analysis import CIAnalysis
from liebes.ci_logger import logger
from liebes.sql_helper import SQLHelper
from liebes.tcp_approach.information_achieve import HistoryInformationManager


def extract_log():
    # history_main
    root_path = "logs/main-2024-04-02-11:33:12.txt"
    text = Path(root_path).read_text().split("\n")
    res = []
    for i in range(len(text)):
        line = text[i]
        if "APFD avg" in line:
            temp = ["avg"]
            for j in range(1, 7):
                s = text[i + j].split("INFO")[1].strip()
                temp.append(s)
            res.append(temp)
        elif "APFD" in line:
            temp = []
            v_id = text[i - 1].split("INFO")[1].strip()
            temp.append(v_id)
            for j in range(1, 7):
                s = text[i + j].split("INFO")[1].strip()
                temp.append(s)
            res.append(temp)
    for r in res:
        print(r[0], r[1], r[2], r[3], r[4], r[5], r[6])




if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=int, default=15, help="regression last version")

    args = parser.parse_args()
    logger.info(args)

    if not Path("cia_04-01.pkl").exists():
        sql = SQLHelper()
        checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()

        # # checkouts = sql.session.query(DBCheckout).limit(10).all()
        cia = CIAnalysis()
        for ch in checkouts:
            cia.ci_objs.append(Checkout(ch))
        cia.reorder()
        cia.set_parallel_number(40)
        cia.filter_job("COMBINE_SAME_CASE")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cia.filter_job("COMBINE_SAME_CONFIG")
        cia.filter_job("CHOOSE_ONE_BUILD")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
        cia.ci_objs = cia.ci_objs[1:]
        pickle.dump(cia, open("cia_04-01.pkl", "wb"))
    else:
        cia = pickle.load(open("cia_04-01.pkl", "rb"))
    cia.statistic_data()

    # achieve history data
    logger.info("start to achieve history data")
    history_information_manager = HistoryInformationManager(cia)
    history_information_manager.load()
    # history_information_manager.extract()
    #
    # history_information_manager.save()

    ehelper = EHelper()
    # for k, v in history_information_manager.failed_count.items():
    #     print(k, v)
    # print(history_information_manager.executed_count[i])

    # for i in range(len(cia.ci_objs)):
    apfd_arr = []
    logger.info(len(cia.ci_objs))
    for i in range(len(cia.ci_objs)):
        # logger.info(f"process {i}")
        if i == 0:
            continue
        if i <= args.history:
            # logger.info(i)
            continue
        ci_obj = cia.ci_objs[i]
        faults_arr = []
        all_cases = ci_obj.get_all_testcases()
        for j in range(len(all_cases)):
            tc = all_cases[j]
            if tc.is_failed():
                faults_arr.append(j)
        if len(faults_arr) == 0:
            # logger.info(i)
            continue
        his_arr = []

        his_index = i - args.history
        # logger.info(f"start !!! {i}")
        for j in range(len(all_cases)):
            tc = all_cases[j]
            if tc.is_failed():
                faults_arr.append(j)
            time_since_last_failure = 0
            if history_information_manager.last_failure_time[tc.file_path][his_index] is not None:
                time_since_last_failure = ci_obj.instance.git_commit_datetime - \
                                          history_information_manager.last_failure_time[tc.file_path][his_index]
                time_since_last_failure = time_since_last_failure.days
            time_since_last_execute = 0
            if history_information_manager.last_executed_time[tc.file_path][his_index] is not None:
                time_since_last_execute = ci_obj.instance.git_commit_datetime - \
                                          history_information_manager.last_executed_time[tc.file_path][his_index]
                time_since_last_execute = time_since_last_execute.days
            if history_information_manager.executed_count[tc.file_path][his_index] == 0:
                failed_rate = 0
            else:
                failed_rate = history_information_manager.failed_count[tc.file_path][his_index] / \
                              history_information_manager.executed_count[tc.file_path][his_index]
            his_arr.append([
                history_information_manager.failed_count[tc.file_path][his_index],
                time_since_last_failure,
                failed_rate,
                history_information_manager.exd_value[tc.file_path][his_index],
                history_information_manager.rocket_value[tc.file_path][his_index],
                time_since_last_execute
            ])

        order_arr = np.argsort(np.array(his_arr), axis=0)[::-1]
        order_arr = np.transpose(order_arr)
        # print(order_arr.shape)
        apfd = []
        for j in range(6):
            apfd.append(ehelper.APFD(faults_arr, order_arr[j].tolist()))
        logger.info(ci_obj.instance.git_sha)
        logger.info("APFD:")
        for j in range(6):
            logger.info(apfd[j])
        apfd_arr.append(apfd)
        # print(his_arr)
        # exit(-1)
    logger.info("APFD avg:")
    for i in range(6):
        logger.info(np.average([x[i] for x in apfd_arr]))

