import argparse
import json
import os
import pickle
import string
import time
import datetime
from pathlib import Path
import shutil
import numpy as np
from sqlalchemy import or_, and_
from tqdm import tqdm

from liebes.CiObjects import TestCaseType, DBCheckout, Checkout, DBConfig, DBTest
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.reproduce import ReproUtil
from liebes.sql_helper import SQLHelper
from liebes.ci_logger import logger_file_name
from liebes.tcp_approach.information_achieve import HistoryInformationManager
from liebes.tokenizer import AstTokenizer
from liebes.tree_parser import CodeAstParser
from dateutil.relativedelta import relativedelta
import urllib.request
import re
from liebes.ci_logger import logger

import copy

from nltk.tokenize import sent_tokenize, word_tokenize
from liebes.embedding import TextEmbedding
from liebes.coverage_ana import CoverageHelper

if __name__ == "__main__":

    parser = argparse.ArgumentParser()
    # python temp.py --vmport=8001 --vmindex=1 --vmnum=15 --file_image=file_images/ltp-1 --ltp_repo=ltp_mirror --linux_repo=linux --home_dir=/home/wanghaichi
    # Add arguments
    parser.add_argument("--vmport", type=int, default=8001, help="vm port, range from 8001-8009")
    parser.add_argument("--file_image", type=str, default="kernel_images/ltp", help="relevant path of the file image from home dir")
    parser.add_argument("--ltp_repo", type=str, default="ltp-cp-only", help="relevant path of the ltp repo from home dir")
    parser.add_argument("--linux_repo", type=str, default="linux", help="relevant path of the linux repo from home dir")
    parser.add_argument("--home_dir", type=str, default="/home/wanghaichi", help="home dir")
    parser.add_argument("--version", type=str, help="linux version")
    parser.add_argument("--vmindex", type=int, default=1, help="vm index, range from 1-9")

    args = parser.parse_args()
    logger.info(args)

    cia = pickle.load(open("cia_04-01.pkl", "rb"))

    logger.info("start to reproduce each case")
    ehelper = EHelper()
    for ci_obj in cia.ci_objs:
        if ci_obj.instance.git_sha != args.version:
            continue
        logger.info(ci_obj.instance.git_sha)
        for b in ci_obj.builds:
            # failed_testcases = [x for x in b.get_all_testcases() if x.is_failed()]
            # if len(failed_testcases) == 0:
            #     continue
            test_cases = b.get_all_testcases()
            config_cmd = b.get_config(gcov=True)
            base_config = "defconfig"
            reproutil = ReproUtil(
                home_dir=args.home_dir,
                fs_image_root=args.file_image,
                port=args.vmport,
                linux_dir=args.linux_repo,
                ltp_dir=args.ltp_repo,
                pid_index=args.vmindex,
            )
            res = reproutil.prepare_linux_image(
                git_sha=ci_obj.instance.git_sha,
                base_config=base_config,
                extra_config=config_cmd,
                # renew=True
            )
            if not res:
                logger.info("failed to prepare linux image")
                exit(-1)
            ltp_tag = ehelper.get_ltp_version(ci_obj.instance.git_sha)
            res = reproutil.prepare_ltp_binary(ltp_tag)
            if not res:
                logger.info("failed to prepare ltp binary")
                exit(-1)
            reproutil.start_qemu()
            logger.info("start qemu vm")
            time.sleep(90)
            logger.info("copy ltp to qemu")
            reproutil.copy_essential_files_to_vm()

            reproutil.copy_ltp_bin_to_vm()
            logger.info("start to execute ltp testcases")
            for fc in test_cases:
                if fc.get_suite_name() != "ltp":
                    continue
                testcase_name = Path(fc.file_path).stem
                if testcase_name == "filecapstest":
                    continue
                # print(fc.file_path)
                # print(testcase_name)
                # exit(-1)
                if (Path(reproutil.result_dir) / (testcase_name + ".err")).exists() or (
                        Path(reproutil.result_dir) / (testcase_name + ".result")).exists():
                    logger.info(f"skip {testcase_name}")
                    continue
                logger.info(f"start to reproduce {testcase_name}")
                reproutil.execute_testcase(testcase_name,"ltp", 600, collect_coverage=True)
                # if (Path(reproutil.result_dir) / (testcase_name + ".result")).exists():
                #     # print("skip", testcase_name)
                #     continue
                # # print((Path(reproutil.result_dir) / testcase_name + ".err"))
                # if (Path(reproutil.result_dir) / (testcase_name + ".err")).exists():
                #     print("start to reproduce", testcase_name)
                #     reproutil.execute_ltp_testcase(testcase_name, 600)

            logger.info("done")
            reproutil.kill_qemu()


