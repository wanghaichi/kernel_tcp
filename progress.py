import copy
import pickle
import time
from pathlib import Path
from termcolor import colored


from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis
from liebes.sql_helper import SQLHelper

if __name__ == "__main__":
    cia = pickle.load(open("cia-04-10.pkl", "rb"))
    for ci_obj in cia.ci_objs:
        failed_cases = [x for x in ci_obj.get_all_testcases() if x.is_failed()]
        print(f"{ci_obj.instance.git_sha}: {len(failed_cases)}")

    root_res = "/home/wanghaichi/repro_results"
    root_cov = "/home/wanghaichi/repro_linuxs"
    previous = {}
    first = True
    while True:
        total_left = 0
        total = 0
        total_left_parsed = 0
        for version in versions:
            res_path = Path(root_res) / version
            cov_path = Path(root_cov) / version
            if not cov_path.exists():
                print(f"{version} not started!")
                continue
            finished_number = 0
            parsed_number = 0
            gzs = cov_path.glob("*.tar.gz")
            for f in gzs:
                finished_number += 1
            infos = cov_path.glob("*.info")
            for f in infos:
                parsed_number += 1
            if first:
                print(f"{version} progress: {finished_number} ({finished_number / cnt_m[version] * 100:.2f}%)/ {parsed_number} ({parsed_number / finished_number * 100 :.2f}%) / {cnt_m[version]} .")
            else:
                finished_changed = finished_number - previous[version]['finished']
                parsed_changed = parsed_number - previous[version]['parsed']
                finished_str = ""
                parsed_str = ""
                if finished_changed > 0:
                    finished_str = colored(f"+ {finished_changed}", "green")
                if parsed_changed > 0:
                    parsed_str = colored(f"+ {parsed_changed}", "green")
                print(f"{version} progress: {finished_number} {finished_str} ({finished_number / cnt_m[version] * 100:.2f}%)/ {parsed_number} {parsed_str} ({parsed_number / finished_number * 100 :.2f}%) / {cnt_m[version]} .")
            total_left += finished_number
            total += cnt_m[version]
            total_left_parsed += parsed_number

            previous[version] = {"finished": finished_number, "parsed": parsed_number}
        if first:
            print(
                f"{total_left} {(total_left / total * 100):.2f}% / {total_left_parsed} ({total_left_parsed / total_left * 100:.2f}%) / {total} ")
        else:
            finished_changed = total_left - previous['total_left']
            parsed_changed = total_left_parsed - previous['total_left_parsed']
            finished_str = ""
            parsed_str = ""
            if finished_changed > 0:
                finished_str = colored(f"+ {finished_changed}", "green")
            if parsed_changed > 0:
                parsed_str = colored(f"+ {parsed_changed}", "green")
            print(
                f"{total_left} {finished_str} {(total_left / total * 100):.2f}% / {total_left_parsed} {parsed_str} ({total_left_parsed / total_left * 100:.2f}%) / {total} ")
        previous['total_left'] = total_left
        previous['total'] = total
        previous['total_left_parsed'] = total_left_parsed

        first = False
        print("=====================================")
        time.sleep(60)
