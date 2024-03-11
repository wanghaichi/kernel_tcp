import json
from datetime import datetime

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *
import numpy as np

if __name__ == '__main__':
    linux_path = '/home/wanghaichi/linux-1'
    sql = SQLHelper()
    start_time = datetime.now()

    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(20).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    #cia.filter_job("COMBINE_SAME_CASE")
    #cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.ci_objs = cia.ci_objs[1:]
    cia.statistic_data()

    for ci_obj in cia.ci_objs:
        ci_obj.get_all_testcases()

