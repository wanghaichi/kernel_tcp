import pickle
from pathlib import Path
from typing import List

from tqdm import tqdm
from pqdm.threads import pqdm
from liebes.CiObjects import Checkout, Test, TestCaseType
from collections import defaultdict
from liebes.ci_logger import logger


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

    def load_db_instances(self, db_instances):
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
    #     logger.debug(f"filter {before_branch - after_branch} branches, reduce test_cases from {before} to {after}")

    def statistic_data(self, build_name=None):
        self.reorder()
        total_c = 0
        total_sh = 0
        total_py = 0

        for ci_obj in self.ci_objs:
            test_cases = ci_obj.get_all_testcases()
            if build_name is not None:
                test_cases = []
                for b in ci_obj.builds:
                    if b.instance.build_name == build_name:
                        test_cases = b.get_all_testcases()
                        break
            if len(test_cases) < 500:
                continue
            l1 = len([x for x in test_cases if x.is_failed()])
            path_set = set([x.instance.path for x in test_cases])
            file_set = set([x.file_path for x in test_cases])
            c_count = len([x for x in test_cases if x.type == TestCaseType.C])
            sh_count = len([x for x in test_cases if x.type == TestCaseType.SH])
            py_count = len([x for x in test_cases if x.type == TestCaseType.PY])

            logger.info(
                f"{ci_obj.instance.git_sha}/{ci_obj.instance.git_repo_branch}: {l1} failed / {len(test_cases)} total. Unique test path count: {len(path_set)}. "
                f"Unique file path count: {len(file_set)}. "
                f"C: {c_count}, SH: {sh_count}, PY: {py_count}"
                f"Total builds: {len(ci_obj.builds)}"
            )
            total_c += c_count
            total_sh += sh_count
            total_py += py_count
        file_set = set()
        test_cases = self.get_all_testcases()
        for t in test_cases:
            file_set.add(t.file_path)
        logger.info(f"Unique file count: {len(file_set)}")
        logger.info(f"On total: C: {total_c}, SH: {total_sh}, PY: {total_py}")

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

    def filter_fail_cases_in_last_version(self):
        # 每个版本只考虑一个build
        case_status = {}
        for ci_obj in self.ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if test_case.is_failed():
                            if case_status.get(test_case.file_path, False):
                                continue
                            else:
                                case_status[test_case.file_path] = True
                        else:
                            case_status[test_case.file_path] = False
                        temp.append(test_case)
                    testrun.tests = temp
        return

    @staticmethod
    def _filter_no_file_test_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        # if test_case.map_test() and Path(test_case.file_path).exists() and test_case.file_path != '':
                        if test_case.map_test() and Path(test_case.file_path).exists() and Path(test_case.file_path).is_file():
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

    def filter_branches_and_builds_with_few_testcases(self, minimal_testcases=20):
        before = len(self.get_all_testcases())
        before_branch = len(self.ci_objs)
        temp_obj = []
        for ci_obj in self.ci_objs:
            temp_builds = []
            for build in ci_obj.builds:
                if len(build.get_all_testcases()) > minimal_testcases:
                    temp_builds.append(build)
            ci_obj.builds = temp_builds
            if len(ci_obj.get_all_testcases()) >= minimal_testcases:
                temp_obj.append(ci_obj)
        self.ci_objs = temp_obj
        after = len(self.get_all_testcases())
        after_branch = len(self.ci_objs)
        logger.debug(f"filter {before_branch - after_branch} branches, reduce test_cases from {before} to {after}")

    @staticmethod
    def _combine_same_test_file_case(ci_objs: List['Checkout']):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                status_m = {}
                for testrun in build.testruns:
                    temp = []
                    for testcase in testrun.tests:
                        if testcase.file_path is None or testcase.file_path.strip() == "":
                            continue
                        if testcase.file_path in status_m.keys():
                            status_m[testcase.file_path].merge_status(testcase)
                            continue
                        status_m[testcase.file_path] = testcase
                        temp.append(testcase)
                    testrun.tests = temp
        return ci_objs

    @staticmethod
    def _combine_same_config_(ci_objs: List['Checkout']):
        for ci_obj in ci_objs:
            same_config_builds = {}  # 以config为键，用于存放config相同的build
            for build in ci_obj.builds:
                config = build.instance.kconfig
                # print(config)
                if isinstance(config, list):
                    config_key = tuple(sorted(config))
                else:
                    config_key = tuple(sorted(config.split()))
                if config_key in same_config_builds:  # 如果找到config重复的build
                    same_config_builds[config_key].append(build)
                else:
                    same_config_builds[config_key] = [build]
            # 合并，保留config name 最短的那个build TODO 需要完善，考虑夸版本的相同config的情况
            new_builds = []
            log_str = ""
            for k, v in same_config_builds.items():
                if len(v) == 1:
                    new_builds.append(v[0])
                    continue
                v = sorted(v, key=lambda x: len(x.instance.build_name))
                for sub_v in v:
                    log_str += f"{sub_v.instance.build_name}: {len(sub_v.get_all_testcases())} \n"
                for i in range(1, len(v)):
                    v[0].testruns.extend(v[i].testruns)
                    v[0].previous_build_names.add(v[i].instance.build_name)
                log_str += f"combine {len(v)} builds to {v[0].instance.build_name}\n"
                new_builds.append(v[0])
            log_str += "after ===========\n"
            ci_obj.builds = new_builds
            ci_obj = CIAnalysis._combine_same_test_file_case([ci_obj])[0]
            for build in ci_obj.builds:
                log_str += f"{build.instance.build_name}: {len(build.get_all_testcases())} \n"
            # print(log_str)
        return ci_objs
    
    @staticmethod
    def _good_config_(ci_objs: List['Checkout']):
        common_kconfigs = {}  # 以kconfig为键，用于存放共同的kconfig及其统计信息
        kconfig_build = {}  # 记录相同kconfig对应的build
    # 统计每个ci_obj中的kconfig信息
        for ci_obj in ci_objs:
            for build in ci_obj.builds:                         
                config = build.instance.kconfig
                if isinstance(config, list):
                    config_key = tuple(sorted(config))
                else:
                    config_key = tuple(sorted(config.split()))
                kconfig_build.setdefault(config_key, []).append(build)
            # 找到共同的kconfig，并记录对应的checkout和testcase数量
                #元组的第一个元素表示该共同的 kconfig 出现在多少个不同的 checkout 中，初始值为 0。
                #元组的第二个元素是一个空列表，用于存储该共同的 kconfig 在哪些 checkout 中出现以及每个 checkout 对应的 testcase 数量。
        for kconfig, build_list in kconfig_build.items():
            if kconfig not in common_kconfigs:
                common_kconfigs[kconfig] = ([])
            for build in build_list:
                total_testcases = len(build.get_all_testcases())
                common_kconfigs[kconfig].append((build.instance.build_name, build.instance.checkout_id, total_testcases))
                
        with open("good config.txt", 'w') as file:
            for kconfig, info_list in common_kconfigs.items():
                file.write(f"KConfig: {kconfig}\n")
                for info in info_list:
                    build_name, checkout_id, testcase_count = info
                    file.write(f"  Build Name: {build_name}\n")
                    file.write(f"  Checkout ID: {checkout_id}\n")
                    file.write(f"  Testcase Count: {testcase_count}\n")
                file.write("\n")
        return ci_objs
    

    def assert_all_test_file_exists(self):
        flag = True
        for t in self.get_all_testcases():
            if not Path(t.file_path).exists():
                logger.debug(f"{t.instance.path}: {t.file_path} not exists!")
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
        logger.debug("done")

    def choose_one_build(self):
        count_in_each_version = {}
        total_test_cases = {}
        k_name = {}
        for ci_obj in self.ci_objs:
            for b in ci_obj.builds:
                config = b.instance.kconfig
                # print(config)
                if isinstance(config, list):
                    config_key = tuple(sorted(config))
                else:
                    config_key = tuple(sorted(config.split()))
                if config_key not in k_name.keys():
                    k_name[config_key] = b.instance.build_name
                b.build_name = k_name[config_key]
                if config_key not in count_in_each_version.keys():
                    count_in_each_version[config_key] = 1
                    total_test_cases[config_key] = len(b.get_all_testcases())
                else:
                    count_in_each_version[config_key] += 1
                    total_test_cases[config_key] += len(b.get_all_testcases())
        l = []
        for k, v in count_in_each_version.items():
            l.append((v, total_test_cases[k] / v, k_name[k]))
        l = sorted(l, key=lambda x: x[0], reverse=True)
        logger.info(f"select {l[0][1]} as build name with {l[0][1]} test cases per build, total {l[0][0]} builds.")
        self.select(l[0][2])
        # print(v, total_test_cases[k], total_test_cases[k] / v, k_name[k], k)

    def filter_job(self, job_task: str, *args, **kwargs):
        arguments = [self.ci_objs[i:i + self.execution_number_per_thread] for i in
                     range(0, len(self.ci_objs), self.execution_number_per_thread)]
        job_func = None
        if job_task == "FILTER_UNKNOWN_CASE":
            logger.debug(f"filter unknown test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_unknown_test_cases

        if job_task == "FILTER_CASE_BY_TYPE":
            logger.debug(
                f"filter {kwargs['case_type']} test cases job start. Threads number: {self.number_of_threads}.")
            self.used_type(kwargs['case_type'])
            job_func = self._filter_test_cases_by_type

        if job_task == "FILTER_NOFILE_CASE":
            logger.debug(f"filter test cases with no file job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_no_file_test_cases

        if job_task == "COMBINE_SAME_CASE":
            logger.debug(f"combine same test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._combine_same_test_file_case

        if job_task == "FILTER_ALLFAIL_CASE":
            logger.debug(f"filter always failed test cases job start. Threads number: {self.number_of_threads}.")
            _ = self.test_case_status_map
            job_func = self.filter_always_failed_test_cases

        if job_task == "COMBINE_SAME_CONFIG":
            logger.debug(f"combine same config job start. Threads number: {self.number_of_threads}.")
            job_func = self._combine_same_config_
        if job_task == "FIND_GOOD_CONFIG":
            logger.debug(f"find  good config job start. Threads number: {self.number_of_threads}.")
            job_func = self._good_config_

        if job_task == "FILTER_NO_C_CASE":
            job_func = self._filter_no_c_cases

        if job_task == "FILTER_NO_SH_CASE":
            job_func = self._filter_no_sh_cases

        if job_func is not None:
            before = len(self.get_all_testcases())
            res = pqdm(arguments, job_func, n_jobs=self.number_of_threads,
                       desc="Filter test cases with unknown status", leave=False)
            self.ci_objs = []
            for x in res:
                self.ci_objs.extend(x)
            self.reorder()
            after = len(self.get_all_testcases())
            logger.debug(f"filter {before - after} test cases, reduce test_cases from {before} to {after}")

        if job_task == "FILTER_SMALL_BRANCH":
            logger.debug(
                f"filter branches and builds with few cases (less than{kwargs['minimal_testcases']}) job start.")
            self.filter_branches_and_builds_with_few_testcases(minimal_testcases=kwargs['minimal_testcases'])

        if job_task == "FILTER_FAIL_CASES_IN_LAST_VERSION":
            self.filter_fail_cases_in_last_version()

        if job_task == "CHOOSE_ONE_BUILD":
            self.choose_one_build()


def load_cia(file_path) -> 'CIAnalysis':
    return pickle.load(Path(file_path).open("rb"))
