from datetime import datetime
from pathlib import Path
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout
from liebes.analysis import CIAnalysis
import openpyxl
from liebes.ci_logger import logger
from liebes.GitHelper import GitHelper

if __name__ == "__main__":
    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(201).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    m = {}
    for ch in cia.ci_objs:
        for build in ch.builds:
            unique_test = set([x.file_path for x in build.get_all_testcases()])
            # print(unique_test)
            if len(unique_test) > 1000:
                if build.label not in m.keys():
                    m[build.label] = 0
                m[build.label] += 1
    # print k , v in m, in order by v
    for k, v in sorted(m.items(), key=lambda item: item[1]):
        print(k, v)

    # # ch = Checkout(first_checkout
    cia.set_parallel_number(10)
    # # cia.select()
    # cia.filter_job("FILTER_UNKNOWN_CASE")
    # cia.filter_job("FILTER_NOFILE_CASE")
    cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_ALLFAIL_CASE")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # # cia.filter_job("")

    

    for ch in cia.ci_objs:
        logger.info('=================== ' + ch.instance.git_sha + ' ===================')
        for build in ch.builds:
            fail_case_sum, c_case_sum, sh_case_sum, py_case_sum = 0, 0, 0, 0
            for t in build.get_all_testcases():
                # print(t)
                if t.is_failed():
                    logger.info(t.id + '      ' + t.instance.file_path)

    gitHelper = GitHelper(r'/home/wanghaichi/linux-1')


