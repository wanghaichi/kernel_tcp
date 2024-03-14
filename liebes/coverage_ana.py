from pathlib import Path
from liebes.ci_logger import logger


class CoverageHelper:
    def __init__(self):
        self.test_case_name = None
        self.coverage_info = {}
        pass

    def load_coverage_info(self, file_path):
        self.extract(Path(file_path).read_text(encoding='utf-8', errors='ignore'))
        pass

    def extract(self, raw_coverage_info):
        file_path = None
        tc_name = None
        cov_map = {}
        for line in raw_coverage_info.split("\n"):
            if line.startswith("TN") and tc_name is None:
                temp = line.split(":")
                tc_name = temp[1]
            if line.startswith("SF"):
                file_path = line.split(":")[1]
                cov_map[file_path] = []
            if line.startswith("DA"):
                temp = line.split(":")
                temp = temp[1].split(",")
                cov_map[file_path].append((temp[0], temp[1]))
            if line == "end_of_record":
                file_path = None
        if tc_name is None or tc_name == "":
            idx = 0
            tc_name = f"unknown_{idx}"
            while tc_name in self.coverage_info.keys():
                idx += 1
                tc_name = f"unknown_{idx}"
            logger.error(f"no test case name found in coverage info, use {tc_name} instead.")
        self.coverage_info[tc_name] = cov_map
        pass

    def compare_two_coverages(self, tc_name1, tc_name2):
        if tc_name1 not in self.coverage_info.keys() or tc_name2 not in self.coverage_info.keys():
            logger.error("test case not found in coverage info")
            return None
        cov1 = self.coverage_info[tc_name1]
        cov2 = self.coverage_info[tc_name2]

        all_keys = set(cov1.keys()).union(set(cov2.keys()))
        # lines covered by a but not b
        a_b_res = {}
        # lines covered by b but not a
        b_a_res = {}

        for file_path in all_keys:
            a_covered = set()
            b_covered = set()
            if file_path in cov1.keys():
                for line_number, covered_times in cov1[file_path]:
                    if int(covered_times) > 0:
                        a_covered.add(line_number)
            if file_path in cov2.keys():
                for line_number, covered_times in cov2[file_path]:
                    if int(covered_times) > 0:
                        b_covered.add(line_number)
            a_b_res[file_path] = list((a_covered - b_covered))
            b_a_res[file_path] = list((b_covered - a_covered))
        a_b_res = {k: v for k, v in a_b_res.items() if len(v) > 0}
        b_a_res = {k: v for k, v in b_a_res.items() if len(v) > 0}
        return [a_b_res, b_a_res]
