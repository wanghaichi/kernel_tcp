import argparse
import time

from liebes.CiObjects import DBCheckout, Checkout
from liebes.EHelper import EHelper
from liebes.analysis import CIAnalysis
from liebes.ci_logger import logger
from liebes.reproduce import ReproUtil
from liebes.sql_helper import SQLHelper

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # python temp.py --vmport=8001 --vmindex=1 --vmnum=15 --file_image=file_images/ltp-1 --ltp_repo=ltp_mirror --linux_repo=linux --home_dir=/home/wanghaichi
    # Add arguments
    parser.add_argument("--vmport", type=int, default=9001, help="vm port")
    parser.add_argument("--file_image", type=str, default="kernel_images/ltp",
                        help="relevant path of the file image from home dir")
    parser.add_argument("--ltp_repo", type=str, default="ltp-cp-only",
                        help="relevant path of the ltp repo from home dir")
    parser.add_argument("--linux_repo", type=str, default="linux", help="relevant path of the linux repo from home dir")
    parser.add_argument("--home_dir", type=str, default="/data/wanghaichi", help="home dir")
    parser.add_argument("--linux_git_sha", type=str, required=True, help="linux version")
    parser.add_argument("--testcases_name", type=str, required=True, help="testcase names, separated by ,")
    args = parser.parse_args()
    logger.info(args)

    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).filter(DBCheckout.git_sha == args.linux_git_sha).order_by(DBCheckout.git_commit_datetime.desc()).all()
    cia = CIAnalysis()
    cia.ci_objs = [Checkout(checkout) for checkout in checkouts]
    cia.filter_job("COMBINE_SAME_CONFIG")
    cia.filter_job("CHOOSE_ONE_BUILD")
    config = cia.ci_objs[0].builds[0].get_config()
    reproutil = ReproUtil(
        home_dir=args.home_dir,
        fs_image_root=args.file_image,
        port=args.vmport,
        linux_dir=args.linux_repo,
        ltp_dir=args.ltp_repo,
    )
    reproutil.prepare_linux_image(
        base_config="defconfig",
        git_sha=args.linux_git_sha,
        extra_config="config"
    )
    ehelper = EHelper()
    reproutil.prepare_ltp_binary(ehelper.get_ltp_version(args.linux_git_sha))
    reproutil.start_qemu()
    time.sleep(90)
    reproutil.copy_essential_files_to_vm()
    reproutil.copy_ltp_bin_to_vm()

    testcases = args.testcases_name.split(",")
    for tc in testcases:
        logger.info(f"reproducing {tc} in {args.linux_git_sha}")
        reproutil.execute_ltp_testcase(tc)

    reproutil.kill_qemu()
