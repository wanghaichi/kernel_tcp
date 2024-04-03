import multiprocessing
import os
import subprocess
from pathlib import Path

from tqdm import tqdm

from liebes.ci_logger import logger
from liebes.coverage_ana import CoverageHelper


def run_command(cmd, cwd):
    logger.info(f"execute command: {cmd}")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True, cwd=cwd)
    if result.returncode != 0:
        logger.error(f"execute command failed: {cmd}")
        logger.error(f"error message: {result.stderr}")
    return result


if __name__ == '__main__':

    def run(versions):
        for version in versions:
            cov_helper = CoverageHelper(version)
            cov_helper.load_coverage4checkout()
            print(f"{version} done")

    #
    root = Path("/home/wanghaichi/repro_linuxs")
    task_list = []
    for f in root.iterdir():
        if f.is_dir():
            task_list.append(f.name)
    number_of_process = 10
    batch = len(task_list) // number_of_process
    process_list = []
    for i in range(number_of_process):
        start = i * batch
        end = (i + 1) * batch
        if i == number_of_process - 1:
            end = len(task_list)
        p = multiprocessing.Process(target=run, args=(task_list[start: end],))
        process_list.append(p)
    for p in process_list:
        p.start()
    for p in process_list:
        p.join()
    print("all done!!!")


    # cov_helper = CoverageHelper("b30d7a77c53ec04a6d94683d7680ec406b7f3ac8")
    #
    # files = Path(root).glob('**/*.info')
    # cnt = 0
    # for f in files:
    #     cnt += 1
    # files = Path(root).glob('**/*.info')
    # t = 0
    # for f in tqdm(files, total=cnt):
    #     t += 1
    #     cov_helper.load_coverage_info(f.absolute())
    #     if t > 10:
    #         break
    # cov_helper.remove_common_coverage()
    #
    # sort_list = []
    # for f in cov_helper.total_cov_generator():
    #     sort_list.append(f)
    # print(sort_list)
    # sort_list = []
    # for f in cov_helper.additional_cov_generator():
    #     sort_list.append(f)
    # print(sort_list)
    # # print(cov_helper.coverage_info.keys())
    # # diff = cov_helper.compare_two_coverages('ptrace10_coverage', 'getrandom04_coverage')
    # # print(diff)
    # exit(-1)

    def remove_gcda(root):
        files = Path(root).glob('**/*.gcda')

        # Delete each file
        for file in files:
            os.remove(file)


    def run(subversions):
        for subversion in subversions:
            logger.info(subversion.absolute())
            cmd = "mkdir cov_all"
            run_command(cmd, cwd=subversion.absolute())
            cmd = "cp *.tar.gz cov_all/"
            run_command(cmd, cwd=subversion.absolute())
            for f in subversion.iterdir():
                if f.suffix == ".gz" or f.suffix == ".tar.gz":
                    # remove all *.gcda first
                    tc_name = f.name.removesuffix('.tar.gz')
                    if (subversion / (tc_name + ".info")).exists():
                        logger.info(f"skip {tc_name}")
                        continue
                    remove_gcda(subversion.absolute())
                    cmd = f"tar -xvf {f.name}"
                    run_command(cmd, cwd=subversion.absolute())
                    cmd = f" lcov -c -d ./ -t {tc_name} -o {tc_name}.info"
                    run_command(cmd, cwd=subversion.absolute())
                    logger.info(f"collect coverage for {tc_name} done, result is {tc_name}.info")


    to_list = []
    for subversion in root.iterdir():
        if not subversion.is_dir():
            continue
        to_list.append(subversion)

    number_of_process = 50

    batch = len(to_list) // number_of_process
    logger.info(f"start {number_of_process} processes, {batch} per process")
    processes = []

    for i in range(number_of_process):
        start = i * batch
        end = (i + 1) * batch
        if i == number_of_process - 1:
            end = len(to_list)
        p = multiprocessing.Process(target=run, args=(to_list[start: end],))
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()
