import json
from itertools import chain
from typing import List
import pickle
from pathlib import Path
from liebes.test_path_mapping import mapping_config


class TestCase:
    def __init__(self, test_path, status):
        self.test_path = test_path
        self.status = status
        self.file_path = ""
        self.type = ""

    def is_pass(self):
        return self.status == "Test executed successfully"

    def is_unknown(self):
        return self.status == "Test execution status unknown" or self.status == ""

    def is_failed(self):
        return self.status == "Test execution failed" or self.status == "Test execution regressed"

    @staticmethod
    def load_from_dic(raw_data):
        case_list = []
        for r_case in raw_data:
            if not {"Test case path", "Status"}.issubset(r_case.keys()):
                continue
            t = TestCase(r_case["Test case path"], r_case["Status"])
            case_list.append(t)
        return case_list

    def __str__(self):
        return f"TestCase: {self.test_path}, Status: {self.status}"

    def map_test(self) -> bool:
        if self.test_path.startswith("ltp"):
            self.type = "ltp"
        elif self.test_path.startswith("kselftest"):
            self.type = "kselftest"
        elif self.test_path.startswith("baseline"):
            self.type = "baseline"

        for k in mapping_config.keys():
            if k in self.test_path:
                self.file_path = Path(mapping_config[k]).absolute()
                return True

        if self.test_path.startswith("ltp"):
            # res = TestCaseInfo()
            # TODO
            pass
        if self.test_path.startswith("kselftest"):
            # if "kselftest-lib.lib_prime_numbers_sh" in test_path:
            #     print(123)
            root = "test_cases/selftests"
            temp = self.test_path.split(".")
            test_prefix = temp[0].split("-")[1]
            test_suffix = temp[1]
            temp = test_suffix.split("_")
            if len(temp) == 1:
                test_suffix = temp[0]
            else:
                test_suffix = temp[1]
            file_suffix = [".c", ".sh"]
            for s in file_suffix:
                temp_file = Path(root) / test_prefix / (test_suffix + s)
                if temp_file.exists():
                    self.type = s
                    self.file_path = temp_file.absolute()
                    return True
        if self.test_path.startswith("baseline"):
            pass
        if self.test_path.startswith("lc-compliance"):
            self.type = "lc-compliance"
            self.file_path = Path(
                "test_cases/kernelci-core/config/rootfs/debos/overlays/libcamera/usr/bin/lc-compliance-parser.sh").absolute()
            return True
        if self.test_path.startswith("v4l2-compliance"):
            self.type = "v4l2-compliance"
            self.file_path = Path(
                "test_cases/kernelci-core/config/rootfs/debos/overlays/v4l2/usr/bin/v4l2-parser.sh").absolute()
            return True
        if self.test_path.startswith("igt"):
            temp = self.test_path.split(".")
            if len(temp) <= 1:
                return False
            fp = temp[1] + ".c"
            fp_prefix = Path("test_cases/igt-gpu-tools/tests")
            if (fp_prefix / fp).exists():
                self.type = "igt"
                self.file_path = (fp_prefix / fp).absolute()
                return True
        return False


class Test:
    def __init__(self, test_plan, status, test_cases: List[TestCase] = None):
        self.test_plan = test_plan
        self.status = status
        self.test_cases = test_cases if test_cases is not None else []

    @staticmethod
    def load_from_dic(raw_data):
        test_list = []
        for r_test in raw_data:
            if not {"Test Plan", "Status", "test_case_intro"}.issubset(r_test.keys()):
                continue
            t = Test(r_test["Test Plan"], r_test["Status"])
            t.test_cases = TestCase.load_from_dic(r_test["test_case_intro"])
            test_list.append(t)
        return test_list

    def __str__(self):
        test_cases_str = "\n".join(str(test_case) for test_case in self.test_cases)
        return f"Test:\nTest Plan: {self.test_plan}\nStatus: {self.status}\nTest Cases:\n{test_cases_str}"


class Build:
    def __init__(self, config, status, tests=None):
        self.config = config
        self.status = status
        self.tests = tests if tests is not None else []
        temp = self.config.split("/")
        self.label = temp[6] + "/" + temp[7]

    @staticmethod
    def load_from_dic(raw_data: dict):
        build_list = []
        for r_build in raw_data:
            if not {"Kernel config", "Status", "Test Results"}.issubset(r_build.keys()):
                continue
            b = Build(r_build["Kernel config"], r_build["Status"])
            b.tests = Test.load_from_dic(r_build["Test Results"])
            build_list.append(b)
        return build_list

    def __str__(self):
        tests_str = "\n".join(str(test) for test in self.tests)
        return f"Build:\nConfig: {self.config}\nStatus: {self.status}\nTests:\n{tests_str}"

    def get_all_testcases(self) -> List['TestCase']:
        return [test_case for test_plan in self.tests for test_case in test_plan.test_cases]


class CIObj:
    def __init__(self, commit_hash, branch, date, builds=None):
        self.commit_hash = commit_hash
        self.branch = branch
        self.date = date
        self.builds = builds if builds is not None else []

    @staticmethod
    def load_from_json(json_path: str):
        raw_data = json.load(Path(json_path).open("r"))
        ci_obj = CIObj(raw_data["Commit"], raw_data["Kernel"], raw_data["Date"])
        ci_obj.builds = Build.load_from_dic(raw_data["build_detail"])
        return ci_obj

    def print_with_intent(self):
        output_hierarchy = str(self)
        indent = "  "  # Specify the desired indentation string
        intent = ""  # Initialize the intent string

        for line in output_hierarchy.split("\n"):
            if line.startswith("CIObj:"):
                intent = ""
            elif line.startswith("Build:"):
                intent = indent
            elif line.startswith("Test:"):
                intent = indent * 2
            elif line.startswith("TestCase:"):
                intent = indent * 3

            # Add the intent to the line
            line_with_intent = intent + line

            # Print or store the line with the added intent
            print(line_with_intent)

    def __str__(self):
        builds_str = "\n".join(str(build) for build in self.builds)
        return f"CIObj:\nCommit Hash: {self.commit_hash}\nBranch: {self.branch}\nDate: {self.date}\nBuilds:\n{builds_str}"

    def get_all_testcases(self) -> List['TestCase']:
        return [test_case for build in self.builds for test_case in build.get_all_testcases()]


class CIAnalysis:
    def __init__(self, obj_list: List[CIObj] = None):
        self.ci_objs = obj_list if obj_list is not None else []

    def reorder(self):
        sorted(self.ci_objs, key=lambda x: x.date)

    def select(self, build_label: str) -> 'CIAnalysis':
        res = []
        for ci_obj in self.ci_objs:
            temp = CIObj(ci_obj.commit_hash, ci_obj.branch, ci_obj.date)
            temp.builds = [x for x in ci_obj.builds if x.label == build_label]
            if len(temp.builds) > 0:
                res.append(temp)
        return CIAnalysis(res)

    def get_all_testcases(self) -> List['TestCase']:
        return [test_case for ci_obj in self.ci_objs for test_case in ci_obj.get_all_testcases()]

    def filter_unknown_test_cases(self):
        cnt_before = 0
        cnt_after = 0
        for ci_obj in self.ci_objs:
            for build in ci_obj.builds:
                for test_plan in build.tests:
                    temp = []
                    for test_case in test_plan.test_cases:
                        if not test_case.is_unknown():
                            temp.append(test_case)
                            cnt_after += 1
                        cnt_before += 1
                    test_plan.test_cases = temp
        print(f"filter {cnt_before - cnt_after} unknown test cases, reduce test_cases from {cnt_before} to {cnt_after}")

    # 默认已经经过`select`方法了，即build_label只存在一个
    def filter_always_failed_test_cases(self):
        before = 0
        after = 0
        test_case_map = {}

        for test_case in self.get_all_testcases():
            if test_case.test_path not in test_case_map.keys():
                test_case_map[test_case.test_path] = False
            test_case_map[test_case.test_path] |= test_case.is_pass()

        for ci_obj in self.ci_objs:
            for build in ci_obj.builds:
                for test_plan in build.tests:
                    temp = []
                    for test_case in test_plan.test_cases:
                        if test_case_map[test_case.test_path]:
                            temp.append(test_case)
                            after += 1
                        before += 1
                    test_plan.test_cases = temp

        print(f"filter {before - after} always failed test cases, reduce test_cases from {before} to {after}")

    def statistic_data(self):
        self.reorder()
        for ci_obj in self.ci_objs:
            test_cases = ci_obj.get_all_testcases()
            l1 = len([x for x in test_cases if not x.is_pass()])

            path_set = set([x.test_path for x in test_cases])
            print(f"{ci_obj.branch}: {l1} / {len(test_cases)} failed. Unique test path count: {len(path_set)}")

    def filter_no_file_test_cases(self):
        before = 0
        after = 0
        for ci_obj in self.ci_objs:
            for build in ci_obj.builds:
                for test_plan in build.tests:
                    temp = []
                    for test_case in test_plan.test_cases:
                        if test_case.map_test():
                            temp.append(test_case)
                            after += 1
                        before += 1
                    test_plan.test_cases = temp
        print(f"filter {before - after} no file test cases, reduce test_cases from {before} to {after}")

    def filter_c_test_cases(self):
        before = 0
        after = 0
        for ci_obj in self.ci_objs:
            for build in ci_obj.builds:
                for test_plan in build.tests:
                    temp = []
                    for test_case in test_plan.test_cases:
                        if test_case.file_path.suffix == ".c":
                            temp.append(test_case)
                            after += 1
                        before += 1
                    test_plan.test_cases = temp
        print(f"filter {before - after} not c test cases, reduce test_cases from {before} to {after}")

    def combine_same_test_file_case(self):
        test_cases = self.get_all_testcases()
        m = {}
        for tc in test_cases:
            if tc.file_path not in m.keys():
                m[tc.file_path] = set()
            m[tc.file_path].add(tc.test_path)
        print(len(m.keys()))
        print(m.keys())
        exit(-1)
        in_one_m = {}
        for k, v in m.items():
            kk = v.pop()
            in_one_m[kk] = kk
            for temp in v:
                in_one_m[temp] = kk
        # print(in_one_m)
        res = []
        for tc in test_cases:
            if in_one_m[tc.test_path] == tc.test_path:
                res.append(tc)
        print(len(test_cases))
        print(len(res))


    def assert_all_test_file_exists(self):
        flag = True
        for t in self.get_all_testcases():
            if not Path(t.file_path).exists():
                print(f"{t.test_path}: {t.file_path} not exists!")
                flag = False
        if not flag:
            exit("failed to pass assertion, solve the above file inconsistency")


def load_cia(file_path) -> 'CIAnalysis':
    return pickle.load(Path(file_path).open("rb"))
