import pickle
from pathlib import Path

from tqdm import tqdm

from liebes.ci_logger import logger
import random
import copy


class CoverageHelper:
    def __init__(self, kernel_version):
        self.kernel_version = kernel_version
        self.test_case_name = None
        self.coverage_info = {}
        pass

    def load_coverage_info(self, file_path):
        self.extract(Path(file_path).read_text(encoding='utf-8', errors='ignore'))
        pass

    def remove_common_coverage(self):
        # this approach will remove all same coverage that is covered by all test cases
        common_coverage = {}
        for k, v in self.coverage_info.items():
            for file_path, lines in v.items():
                common_coverage[file_path] = lines
            break
        for _, v in self.coverage_info.items():
            for file_path, lines in v.items():
                if file_path not in common_coverage.keys():
                    continue
                common_coverage[file_path] = list(set(common_coverage[file_path]).intersection(set(lines)))
        common_coverage = {k: v for k, v in common_coverage.items() if len(v) > 0}
        # remove common coverage from all the test cases
        for _, v in self.coverage_info.items():
            for file_path, lines in v.items():
                if file_path not in common_coverage.keys():
                    continue
                v[file_path] = list(set(lines) - set(common_coverage[file_path]))
        # done

    def extract(self, raw_coverage_info):
        file_path = None
        tc_name = None
        cov_map = {}
        for line in raw_coverage_info.split("\n"):
            if tc_name is not None and tc_name in self.coverage_info.keys():
                logger.info(f"test case {tc_name} already exists in coverage info, skip the rest.")
                return
            if line.startswith("TN") and tc_name is None:
                temp = line.split(":")
                tc_name = temp[1]
            if line.startswith("SF"):
                file_path = line.split(":")[1]
                file_path = file_path.split(self.kernel_version)[1]
                file_path = file_path.removeprefix("/")
                cov_map[file_path] = []
            if line.startswith("DA"):
                temp = line.split(":")
                temp = temp[1].split(",")
                if int(temp[1]) > 0:
                    cov_map[file_path].append(int(temp[0]))
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
                a_covered = set(cov1[file_path])
            if file_path in cov2.keys():
                b_covered = set(cov2[file_path])
            a_b_res[file_path] = list((a_covered - b_covered))
            b_a_res[file_path] = list((b_covered - a_covered))
        a_b_res = {k: v for k, v in a_b_res.items() if len(v) > 0}
        b_a_res = {k: v for k, v in b_a_res.items() if len(v) > 0}
        return [a_b_res, b_a_res]

    def total_cov_generator(self):
        file_list = []
        cov_count = []
        for k, v in self.coverage_info.items():
            file_list.append(k)
            cnt = 0
            for _, lines in v.items():
                cnt += len(lines)
            cov_count.append(cnt)
        print(file_list)
        print(cov_count)
        sorted_file_list = [x for _, x in sorted(zip(cov_count, file_list), key=lambda pair: pair[0], reverse=True)]
        for f in sorted_file_list:
            yield f

    def get_additional_cov(self, base_cov, additional_cov):
        res = 0
        for k, v in additional_cov.items():
            if k not in base_cov.keys():
                res += len(v)
            else:
                diff = len(set(v) - set(base_cov[k]))
                res += diff
        return res

    def combine_cov(self, base_cov, additional_cov):
        for k, v in additional_cov.items():
            if k not in base_cov.keys():
                base_cov[k] = copy.deepcopy(v)
            else:
                base_cov[k] = list(set(base_cov[k]).union(set(v)))
        return base_cov

    def additional_cov_generator(self):
        # random choose one, or select the one with the highest coverage

        candidate = [x for x in self.coverage_info.keys()]
        # random
        # r_idx = random.randint(0, len(candidate) - 1)
        # first_one = candidate[r_idx]
        # candidate.pop(r_idx)
        # file_list = [first_one]
        # base_cov = copy.deepcopy(self.coverage_info[first_one])
        # use the one with the highest coverage
        file_list = []
        base_cov = {}
        while len(candidate) > 0:
            max_cov_idx = -1
            max_cov_cnt = -1
            for i in range(len(candidate)):
                increment_cov = self.get_additional_cov(base_cov, self.coverage_info[candidate[i]])
                if increment_cov > max_cov_cnt:
                    max_cov_cnt = increment_cov
                    max_cov_idx = i
            choose_one = candidate[max_cov_idx]
            candidate.pop(max_cov_idx)
            base_cov = self.combine_cov(base_cov, self.coverage_info[choose_one])
            file_list.append(choose_one)
        for f in file_list:
            yield f

    def load_coverage4checkout(self):
        checkout_path = Path("/home/wanghaichi/repro_linuxs/") / self.kernel_version
        if not checkout_path.exists() or not checkout_path.is_dir():
            logger.error("checkout path not found.")
            return
        previous_cache = checkout_path / "total_coverage.pkl"
        if previous_cache.exists():
            self.coverage_info = pickle.load(previous_cache.open("rb"))
        pr_len = len(self.coverage_info.keys())

        total_number = sum(1 for _ in checkout_path.glob("*.info"))

        for file in tqdm(checkout_path.glob("*.info"), total=total_number):
            self.load_coverage_info(file)
        diff = len(self.coverage_info.keys()) - pr_len
        if diff > 0:
            self.remove_common_coverage()
            logger.info(f"loaded {diff} new test cases coverage.")
            logger.info(f"update coverage cache at {previous_cache.absolute()}.")
            pickle.dump(self.coverage_info, previous_cache.open("wb"))
