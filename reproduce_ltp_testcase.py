import argparse
import os
import pickle
import time
from pathlib import Path

from liebes.EHelper import EHelper
from liebes.ci_logger import logger, logger_file_name
from liebes.reproduce import ReproUtil

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    # python temp.py --vmport=8001 --vmindex=1 --vmnum=15 --file_image=file_images/ltp-1 --ltp_repo=ltp_mirror --linux_repo=linux --home_dir=/home/wanghaichi
    # Add arguments
    parser.add_argument("--vmport", type=int, default=8001, help="vm port, range from 8001-8009")
    parser.add_argument("--vmindex", type=int, default=1, help="vm index, range from 1-9")

    parser.add_argument("--vmnum", type=int, default=4, help="total vm number")
    parser.add_argument("--file_image", type=str, default="kernel_images/ltp",
                        help="relevant path of the file image from home dir")
    parser.add_argument("--ltp_repo", type=str, default="ltp-cp-only",
                        help="relevant path of the ltp repo from home dir")
    parser.add_argument("--linux_repo", type=str, default="linux", help="relevant path of the linux repo from home dir")
    parser.add_argument("--home_dir", type=str, default="/home/wanghaichi", help="home dir")
    args = parser.parse_args()
    logger.info(args)

    pid = os.getpid()
    pid_root = Path("pids")
    if not pid_root.exists():
        pid_root.mkdir(parents=True)
    (pid_root / f"{args.vmindex}.pid").write_text(str(pid))
    (pid_root / f"{args.vmindex}.log").write_text(logger_file_name)

    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).all()
    #
    # cia = CIAnalysis()
    # cia.set_parallel_number(40)
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.filter_job("COMBINE_SAME_CASE")
    # # print(len(cia.get_all_testcases()))
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # cia.statistic_data()
    # pickle.dump(cia, open("cia-04-10.pkl", "wb"))
    cia = pickle.load(open("cia-04-10.pkl", "rb"))
    batch_per_run = int(len(cia.ci_objs) / args.vmnum)
    start_index = (args.vmindex - 1) * batch_per_run
    end_index = args.vmindex * batch_per_run

    for ci_obj in cia.ci_objs[start_index:end_index]:
        ehelper = EHelper()
        for b in ci_obj.builds:
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
            res = reproutil.prepare_selftest_binary()
            if not res:
                logger.info("failed to prepare selftest binary")
                exit(-1)

            reproutil.start_qemu()
            logger.info("start qemu vm")
            time.sleep(90)
            logger.info("copy ltp to qemu")
            reproutil.copy_essential_files_to_vm()
            reproutil.copy_ltp_bin_to_vm()
            logger.info("copy selftest to qemu")
            reproutil.copy_selftest_bin_to_vm()
            logger.info("start to execute testcases")
            failed_cases = [x for x in b.get_all_testcases() if x.is_failed()]
            # for tc in b.get_all_testcases():
            for tc in failed_cases:
                tc_name = tc.get_testcase_name()
                if tc_name == "filecapstest" or tc_name == "breakpoints:step_after_suspend_test":
                    continue
                if (
                        (
                                (Path(reproutil.result_dir) / (tc_name + ".result")).exists()
                                or (Path(reproutil.result_dir) / (tc_name + ".err")).exists()
                        )
                        and
                        (Path(reproutil.work_linux_dir / (tc_name + "_coverage.tar.gz"))).exists()):
                    logger.info(f"skip {tc_name}")
                    continue
                logger.info(f"start to reproduce {tc_name}")
                reproutil.execute_testcase(tc_name, tc.get_suite_name(), 600, collect_coverage=True)
            logger.info("done")
            reproutil.kill_qemu()
