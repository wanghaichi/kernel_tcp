"""
This file is used to achieve the information of the test case, coverage, history, etc.
Input: testcase, relevant information
Output: extracted information for each test case
"""
import copy
import json

from liebes.analysis import CIAnalysis
from liebes.tokenizer import AstTokenizer
from liebes.ci_logger import logger
from datetime import datetime, date


class InformationManager:
    def __init__(self, cia: "CIAnalysis"):
        self.cia = cia
        pass


class HistoryInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis"):
        super().__init__(cia)
        self.last_failure_time = {}
        self.last_executed_time = {}
        self.failed_count = {}
        self.exd_value = {}
        self.alpha = 0.9
        self.rocket_value = {}
        self.executed_count = {}

    def init_map(self):
        updated_set = set()
        for tc in self.cia.get_all_testcases():
            if tc.file_path not in updated_set:
                self.last_failure_time[tc.file_path] = [None]
                self.last_executed_time[tc.file_path] = [None]
                self.failed_count[tc.file_path] = [0]
                self.executed_count[tc.file_path] = [0]
                self.exd_value[tc.file_path] = [0]
                self.rocket_value[tc.file_path] = [0]
                updated_set.add(tc.file_path)

    def extract(self):
        self.init_map()

        for i in range(1, len(self.cia.ci_objs) + 1):
            ci_obj = self.cia.ci_objs[i - 1]
            # mark any test case that is not executed

            for k in self.failed_count.keys():
                tc = ci_obj.get_case_by_file_path(k)
                # record executed number
                self.executed_count[k].append(self.executed_count[k][i - 1] + 1)
                self.last_executed_time[k].append(ci_obj.instance.git_commit_datetime)

                if tc is not None and tc.is_failed():
                    self.last_failure_time[k].append(ci_obj.instance.git_commit_datetime)
                    self.failed_count[k].append(self.failed_count[k][i - 1] + 1)
                    exd_v = self.alpha * 1 + self.exd_value[k][i - 1] * (1 - self.alpha)
                    self.exd_value[k].append(exd_v)
                else:
                    if tc is None:
                        # record executed number
                        self.executed_count[k][-1] -= 1
                        self.last_executed_time[k][-1] = self.last_executed_time[k][-2]

                    self.last_failure_time[k].append(self.last_failure_time[k][i - 1])
                    self.exd_value[k].append(self.exd_value[k][i - 1] * (1 - self.alpha))
                    self.failed_count[k].append(self.failed_count[k][i - 1])
                rocket_v = 0
                for j in range(i):
                    if i - j == 1:
                        w = 0.7
                    elif i == 2:
                        w = 0.2
                    else:
                        w = 0.1
                    tc_this = self.cia.ci_objs[j].get_case_by_file_path(k)
                    if tc_this is None or (not tc_this.is_failed()):
                        continue
                    else:
                        rocket_v += w
                self.rocket_value[k].append(rocket_v)
        pass

    def save(self, save_path="history_information.json"):
        def json_serial(obj):
            """JSON serializer for objects not serializable by default json code"""
            if isinstance(obj, (datetime, date)):
                return obj.isoformat()
            raise TypeError("Type %s not serializable" % type(obj))

        res = {
            "last_failure_time": self.last_failure_time,
            "last_executed_time": self.last_executed_time,
            "failed_count": self.failed_count,
            "executed_count": self.executed_count,
            "exd_value": self.exd_value,
            "rocket_value": self.rocket_value
        }
        json.dump(res, open(save_path, "w"), indent=4, default=json_serial)
        logger.info(f"success save history res to {save_path}")

    def load(self, save_path="history_information.json"):
        res = json.load(open(save_path, "r"))
        self.last_failure_time = res["last_failure_time"]
        for k, v in self.last_failure_time.items():
            self.last_failure_time[k] = [datetime.fromisoformat(str(x)) if x is not None else None for x in v]
        self.last_executed_time = res["last_executed_time"]
        for k, v in self.last_executed_time.items():
            self.last_executed_time[k] = [datetime.fromisoformat(str(x)) if x is not None else None for x in v]
        self.failed_count = res["failed_count"]
        self.executed_count = res["executed_count"]
        self.exd_value = res["exd_value"]
        self.rocket_value = res["rocket_value"]
        logger.info(f"success load history res to {save_path}")
        pass


class TestCaseInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis", git_helper):
        super().__init__(cia)
        self.git_helper = git_helper
        self.token_cache = {}

    def init_map(self):
        updated_set = set()
        for tc in self.cia.get_all_testcases():
            if tc.file_path not in updated_set:
                self.testcase_content[tc.file_path] = []
                updated_set.add(tc.file_path)

    def extract(self):
        tokenizer = AstTokenizer()

        last_commit = None
        for ci_obj in self.cia.ci_objs:
            commit = self.git_helper.get_commit_info_by_time(ci_obj.instance.git_commit_datetime)
            if commit is None:
                logger.error(
                    f"commit is not found for {self.git_helper.repo.path} with time: {ci_obj.instance.git_commit_datetime}")
                continue
            changed_files = []
            if last_commit is not None:
                changed_files = self.git_helper.get_changed_files(last_commit.hexsha, commit.hexsha)
            last_commit = commit
            res = {}
            for tc in ci_obj.get_all_testcases():
                is_modified = tc.file_path in changed_files
                if not is_modified and tc.file_path in self.token_cache.keys():
                    tokens = self.token_cache[tc.file_path]
                else:
                    file_content = self.git_helper.get_file_content_by_commit(
                        commit.hexsha, tc.file_path.replace("test_cases/ltp/", ""))
                    if file_content is None:
                        continue
                    # print(tc.file_path)
                    tokens = tokenizer.get_tokens(file_content, tc.type)
                res[tc.file_path] = tokens
            yield ci_obj, res
        pass


class CoverageInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis"):
        super().__init__(cia)
        self.coverage_information = []


if __name__ == "__main__":
    pass
