import json
import time
import urllib.request
from pathlib import Path

import numpy as np
import random

from tqdm import tqdm

from liebes.CiObjects import DBConfig, DBCheckout, Checkout
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.ltp_result import LTPResult
from liebes.reproduce import ReproUtil
from liebes.sql_helper import SQLHelper
from liebes.llvm_process import LLVMHelper
import re

from liebes.tcp_approach.information_achieve import InformationManager, TestCaseInformationManager
from liebes.tcp_approach.topic_model import TopicModel
from liebes.tcp_approach.metric_manager import DistanceMetric
from liebes.ci_logger import logger
from liebes.test_path_mapping import has_mapping
import argparse


if __name__ == "__main__":
    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()
    # print(len(checkouts))
    cia = CIAnalysis()
    cia.set_parallel_number(40)
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("COMBINE_SAME_CONFIG")
    cia.filter_job("CHOOSE_ONE_BUILD")

    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")



    for ci_obj in tqdm(cia.ci_objs):
        logger.info(f"{ci_obj.instance.git_sha}")
        for build in ci_obj.builds:
            logger.info(build.instance.build_name)
            config_cmd = build.get_config(gcov=True)
            base_config = "defconfig"
            reproutil = ReproUtil(
                home_dir="/home/wanghaichi",
                fs_image_root="file_images/ltp-1",
                port=8011,
                linux_dir="linux",
                ltp_dir="ltp-cp-only",
                pid_index=1,
            )
            res = reproutil.prepare_linux_image(
                git_sha=ci_obj.instance.git_sha,
                base_config=base_config,
                extra_config=config_cmd,
                # renew=True
            )
            if not res:
                print("failed to prepare linux image")
                exit(-1)
