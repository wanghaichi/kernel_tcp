import pickle
from pathlib import Path
from typing import List

from pqdm.threads import pqdm
from tqdm import tqdm

from liebes.CiObjects import Checkout, Test, TestCaseType
# from liebes.ci_logger import logger


class CIAnalysis:
    def __init__(self, obj_list: List['Checkout'] = None):
        self.ci_objs = obj_list if obj_list is not None else []
        self.number_of_threads = 1
        self.execution_number_per_thread = 1024
        self._test_case_status_map = None

    def set_parallel_number(self, number_of_threads: int):
        if not hasattr(self, "number_of_threads"):
            setattr(self, "number_of_threads", 1)
            setattr(self, "execution_number_per_thread", 1024)
        self.number_of_threads = number_of_threads
        self.execution_number_per_thread = 32

    def reorder(self):
        self.ci_objs = sorted(self.ci_objs, key=lambda x: x.instance.git_commit_datetime)

    def select(self, build_config: str):
        for ci_obj in self.ci_objs:
            ci_obj.select_build_by_config(build_config)
        # return CIAnalysis(res)

    def get_all_testcases(self) -> List['Test']:
        return [test_case for ci_obj in self.ci_objs for test_case in ci_obj.get_all_testcases()]

    def load_db_instances(self,  db_instances):
        def _load_db_instances_parallel(db_instances):
            temp = []
            for db_instance in db_instances:
                temp.append(Checkout(db_instance))
            return temp

        number_per_batch = int(len(db_instances) / self.number_of_threads)
        arguments = [db_instances[i:i + number_per_batch] for i in
                     range(0, len(db_instances), number_per_batch)]
        res = pqdm(arguments, _load_db_instances_parallel, n_jobs=self.number_of_threads, desc="Load DB instances",
                   leave=False)
        for sub_obj_list in res:
            self.ci_objs.extend(sub_obj_list)

    @staticmethod
    def _filter_unknown_test_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if not test_case.is_unknown():
                            temp.append(test_case)
                    testrun.tests = temp

        return ci_objs

    # TODO 这个逻辑需要改，需要定义一下flaky test的pattern，一起过滤了
    def filter_always_failed_test_cases(self, ci_objs):
        # TODO 用test_path 还是 test_file作为过滤的key
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        # TODO filter has known issues test cases
                        if test_case.instance.has_known_issues == "1":
                            continue
                            # test_case.status = 0

                        if self.test_case_status_map[test_case.instance.path]:
                            # test_case.status = 0
                            temp.append(test_case)
                    testrun.tests = temp

        return ci_objs

    @property
    def test_case_status_map(self):
        if self._test_case_status_map is None:
            self._test_case_status_map = {}
            for test_case in self.get_all_testcases():
                if test_case.instance.path not in self._test_case_status_map.keys():
                    self._test_case_status_map[test_case.instance.path] = False
                self._test_case_status_map[test_case.instance.path] |= test_case.is_pass()

        return self._test_case_status_map

    # def filter_by_unique_files(self, minimal_size=10):
    #     before = len(self.get_all_testcases())
    #     before_branch = len(self.ci_objs)
    #     temp_obj = []
    #     for ci_obj in self.ci_objs:
    #         file_set = set([x.file_path for x in ci_obj.get_all_testcases()])
    #     self.ci_objs = temp_obj
    #     after = len(self.get_all_testcases())
    #     after_branch = len(self.ci_objs)
    #     print(f"filter {before_branch - after_branch} branches, reduce test_cases from {before} to {after}")

    def statistic_data(self):
        self.reorder()
        total_c = 0
        total_sh = 0
        total_py = 0
        for ci_obj in self.ci_objs:
            test_cases = ci_obj.get_all_testcases()
            if len(test_cases) < 500:
                continue
            l1 = len([x for x in test_cases if not x.is_pass()])
            path_set = set([x.instance.path for x in test_cases])
            file_set = set([x.file_path for x in test_cases])
            c_count = len([x for x in test_cases if x.type == TestCaseType.C])
            sh_count = len([x for x in test_cases if x.type == TestCaseType.SH])
            py_count = len([x for x in test_cases if x.type == TestCaseType.PY])

            print(
                f"{ci_obj.instance.git_repo_branch}: {l1} / {len(test_cases)} failed. Unique test path count: {len(path_set)}. "
                f"Unique file path count: {len(file_set)}. "
                f"C: {c_count}, SH: {sh_count}, PY: {py_count}")
            total_c += c_count
            total_sh += sh_count
            total_py += py_count
        file_set = set()
        test_cases = self.get_all_testcases()
        for t in test_cases:
            file_set.add(t.file_path)
        print(f"Unique file count: {len(file_set)}")
        print(f"On total: C: {total_c}, SH: {total_sh}, PY: {total_py}")

    @staticmethod
    def _filter_no_c_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if test_case.file_path.endswith(r'.c'):
                            temp.append(test_case)
                    testrun.tests = temp
        return ci_objs
    
    @staticmethod
    def _filter_no_sh_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if test_case.file_path.endswith(r'.sh'):
                            temp.append(test_case)
                    testrun.tests = temp
        return ci_objs

    @staticmethod
    def _filter_no_file_test_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if test_case.map_test() and Path(test_case.file_path).exists():
                            temp.append(test_case)
                        # else:
                        #     if "login" in test_case.test_path or "speculative" in test_case.test_path:
                        #         continue
                        # TestCase.not_mapped_set.add(f"{test_plan.test_plan}: {test_case.test_path}")
                    testrun.tests = temp
        return ci_objs

    def _filter_test_cases_by_type(self, ci_objs):

        # logger.info("process!")
        for ci_obj in ci_objs:
            # logger.info("process-obj!")
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in build.tests:
                        if test_case.type in self.used_type():
                            temp.append(test_case)
                    testrun.tests = temp
        return ci_objs

    def used_type(self, type_list: List[TestCaseType] = None):
        if not hasattr(self, "_used_type"):
            if type_list is None:
                setattr(self, "_used_type", [TestCaseType.C, TestCaseType.SH, TestCaseType.PY])
            else:
                setattr(self, "_used_type", type_list)
        elif type_list is not None:
            self._used_type = type_list
        return self._used_type

    def filter_branches_with_few_testcases(self, minimal_testcases=20):
        before = len(self.get_all_testcases())
        before_branch = len(self.ci_objs)
        temp_obj = []
        for ci_obj in self.ci_objs:
            if len(ci_obj.get_all_testcases()) >= minimal_testcases:
                temp_obj.append(ci_obj)
        self.ci_objs = temp_obj
        after = len(self.get_all_testcases())
        after_branch = len(self.ci_objs)
        print(f"filter {before_branch - after_branch} branches, reduce test_cases from {before} to {after}")

    @staticmethod
    def _combine_same_test_file_case(ci_objs: List['Checkout']):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                status_m = {}
                for testrun in build.testruns:
                    temp = []
                    for testcase in testrun.tests:
                        if testcase.file_path in status_m.keys():
                            status_m[testcase.file_path].merge_status(testcase)
                            continue
                        status_m[testcase.file_path] = testcase
                        temp.append(testcase)
                    testrun.tests = temp

            # update statusA
            # for build in ci_obj.builds:
            #     for testrun in build.testruns:
            #         for i in range(len(testrun.tests)):
            #             testrun.tests[i].merge_status(status_m[testrun.tests[i].file_path])
        return ci_objs

    def assert_all_test_file_exists(self):
        flag = True
        for t in self.get_all_testcases():
            if not Path(t.file_path).exists():
                print(f"{t.instance.path}: {t.file_path} not exists!")
                flag = False
        if not flag:
            exit("failed to pass assertion, solve the above file inconsistency")

    def map_file_path(self):
        def _map_file_path_parallel(ci_objs):
            for ci_obj in ci_objs:
                for t in tqdm(ci_obj.get_all_testcases(), desc=f"{ci_obj.instance.id} map file path"):
                    t.map_test()
            for ci_obj in ci_objs:
                pickle.dump(ci_obj, open(f"lkft/caches-withfile/{ci_obj.instance.id}.pkl", "wb"))

        number_of_per_task = int(len(self.ci_objs) / self.number_of_threads)
        arguments = [self.ci_objs[i:i + number_of_per_task] for i in
                     range(0, len(self.ci_objs), number_of_per_task)]
        res = pqdm(arguments, _map_file_path_parallel, n_jobs=self.number_of_threads,
                   desc="map files", leave=False)
        print("done")

    def filter_job(self, job_task: str, *args, **kwargs):
        arguments = [self.ci_objs[i:i + self.execution_number_per_thread] for i in
                     range(0, len(self.ci_objs), self.execution_number_per_thread)]
        job_func = None
        if job_task == "FILTER_UNKNOWN_CASE":
            # logger.info(f"filter unknown test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_unknown_test_cases

        if job_task == "FILTER_CASE_BY_TYPE":
            # logger.info(f"filter {kwargs['case_type']} test cases job start. Threads number: {self.number_of_threads}.")
            # logger.info("????")
            self.used_type(kwargs['case_type'])
            # logger.info("!!!!!")
            job_func = self._filter_test_cases_by_type

        if job_task == "FILTER_NOFILE_CASE":
            # logger.info(f"filter test cases with no file job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_no_file_test_cases

        if job_task == "COMBINE_SAME_CASE":
            # logger.info(f"combine same test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._combine_same_test_file_case

        if job_task == "FILTER_ALLFAIL_CASE":
            # logger.info(f"filter always failed test cases job start. Threads number: {self.number_of_threads}.")
            _ = self.test_case_status_map
            job_func = self.filter_always_failed_test_cases

        if job_task == "FILTER_NO_C_CASE":
            job_func = self._filter_no_c_cases

        if job_task == "FILTER_NO_SH_CASE":
            job_func = self._filter_no_sh_cases

        if job_func is not None:
            before = len(self.get_all_testcases())
            res = pqdm(arguments, job_func, n_jobs=self.number_of_threads,
                       desc="Filter test cases with unknown status", leave=False)
            self.ci_objs = []
            print(res)
            for x in res:
                self.ci_objs.extend(x)
            self.reorder()
            after = len(self.get_all_testcases())
            # logger.info(f"filter {before - after} test cases, reduce test_cases from {before} to {after}")

        if job_task == "FILTER_SMALL_BRANCH":
            # logger.info(
                # f"filter branches with small cases (less than{kwargs['minimal_testcases']}) job start. Threads number: {self.number_of_threads}.")
            self.filter_branches_with_few_testcases(minimal_testcases=kwargs['minimal_testcases'])


def load_cia(file_path) -> 'CIAnalysis':
    return pickle.load(Path(file_path).open("rb"))
