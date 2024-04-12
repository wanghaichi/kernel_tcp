import pickle
from pathlib import Path

from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis
from liebes.ltp_result import TCResult
from liebes.sql_helper import SQLHelper

if __name__ == "__main__":

    cia = pickle.load(open("cia-04-10.pkl", "rb"))

    repro_root = Path("/home/wanghaichi/repro_results")
    failed_version = set()
    failed_path = set()
    failed_case = set()
    failed_case_m = {}
    for ci_obj in cia.ci_objs:
        failed_cnt = 0
        failed_total = 0
        broken_cnt = 0

        for tc in cia.get_all_testcases():
            if tc.is_failed():
                res_path = repro_root / ci_obj.instance.git_sha / (tc.get_testcase_name() + ".result")
                if res_path.exists():
                    if res_path.exists():
                        pass
                        failed_total += 1
                        tc_result = TCResult.create(tc.get_testcase_name(), tc.get_suite_name(), res_path.read_text())
                        if tc_result.total_failed_cnt() > 0:
                            # print(f"{ci_obj.instance.git_sha} {tc.get_testcase_name()} failed")
                            failed_version.add(ci_obj.instance.git_sha)
                            failed_path.add(res_path.absolute())
                            failed_case.add(tc.get_testcase_name())
                            failed_cnt += 1
                            failed_case_m[tc.get_testcase_name()] = failed_case_m.get(tc.get_testcase_name(), 0) + 1
                        elif tc_result.total_broken_cnt() > 0:
                            broken_cnt += 1
                        else:
                            pass
                            # print(ltp_result.total_pass_cnt())
                            # print(res_path.absolute())
                    else:
                        print(f"{tc.get_testcase_name()} not found")
                        # print(res_path.absolute())
                    # print(f"{tc.get_testcase_name()} is self test" )
    print(len(failed_version))
    for p in failed_path:
        print(p)
    print(len(failed_case))
    for k, v in failed_case_m.items():
        print(k, v)
    pass
