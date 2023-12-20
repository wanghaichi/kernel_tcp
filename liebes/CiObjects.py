import pickle
from enum import Enum
from pathlib import Path
from typing import List

from pqdm.threads import pqdm
from sqlalchemy import Column, String, ForeignKey, Text, Integer
from sqlalchemy.orm import declarative_base, relationship
from tqdm import tqdm

from liebes.ci_logger import logger
from liebes.test_path_mapping import mapping_config, has_mapping

Base = declarative_base()


class TestCaseType(Enum):
    UNKNOWN = 0
    C = 1
    SH = 2
    PY = 3


class Build:
    def __init__(self, db_instance: 'DBBuild'):
        self.instance = db_instance
        self.tests = [Test(x) for x in self.instance.tests]

    @property
    def label(self) -> str:
        return self.instance.config_name

    def get_all_testcases(self) -> List['Test']:
        return self.tests

    def __str__(self):
        return str(self.instance)


class DBBuild(Base):
    __tablename__ = 'build'
    checkout_id = Column(String, ForeignKey('checkout.id'), primary_key=True)
    id = Column(String, primary_key=True)
    origin = Column(String)
    comment = Column(Text)
    start_time = Column(String)
    duration = Column(String)
    architecture = Column(String)
    command = Column(Text)
    compiler = Column(String)
    input_files = Column(Text)
    output_files = Column(Text)
    config_name = Column(String)
    config_url = Column(String)
    log_url = Column(String)
    valid = Column(Integer)
    misc = Column(Text)

    checkout = relationship('DBCheckout', back_populates='builds')
    tests = relationship('DBTest', back_populates='build')

    def __str__(self):
        return f"Build{{checkout_id: {self.checkout_id}, id: {self.id}, origin: {self.origin}, " \
               f"comment: {self.comment}, start_time: {self.start_time}, duration: {self.duration}, " \
               f"architecture: {self.architecture}, command: {self.command}, compiler: {self.compiler}, " \
               f"input_files: {self.input_files}, output_files: {self.output_files}, " \
               f"config_name: {self.config_name}, config_url: {self.config_url}, log_url: {self.log_url}, " \
               f"valid: {self.valid}, misc: {self.misc}, tests: {len(self.tests)}tests}}"


class Test:
    def __init__(self, db_instance: 'DBTest'):
        self.instance = db_instance
        self._type = None
        self.file_path = None
        if self.instance.status == "Test executed successfully" or self.instance.status.lower() == "pass":
            self.status = 0
        elif self.instance.status == "Test execution failed" or self.instance.status.lower() == "fail":
            self.status = 1
        elif self.instance.status == "Test execution regressed":
            self.status = 2
        else:
            self.status = 3

    def __str__(self):
        return str(self.instance)

    '''
        0: "Test executed successfully" "PASS"
        1: "Test execution failed" "FAIL"
        2: "Test execution regressed"
        3: "Test execution status unknown" or otherwise "SKIP"
        '''

    @property
    def type(self):
        if self._type is None:
            if self.file_path is not None and self.file_path != "" and Path(self.file_path).exists():
                if Path(self.file_path).suffix.lower() == ".c":
                    self._type = TestCaseType.C
                if Path(self.file_path).suffix.lower() == ".sh" or Path(self.file_path).suffix == "":
                    self._type = TestCaseType.SH
                if Path(self.file_path).suffix.lower() == ".py":
                    self._type = TestCaseType.PY
                if self._type is None:
                    self._type = TestCaseType.UNKNOWN
        return self._type

    def is_pass(self):
        return self.status == 0

    def is_unknown(self):
        return self.status == 3

    def is_failed(self):
        return self.status in [1, 2]

    def merge_status(self, other_testcase: 'DBTest'):
        if self.is_pass() and other_testcase.is_pass():
            pass
        else:
            self.status = 1

    def map_test(self) -> bool:
        if self.file_path is not None:
            return True
        p = has_mapping(self.instance.path)
        if p is not None:
            if Path(p).exists():
                self.file_path = Path(p)
                return True
        return False
        # if self.instance.path.startswith("lc-compliance"):
        #     self.file_path = Path(
        #         "test_cases/kernelci-core/config/rootfs/debos/overlays/libcamera/usr/bin/lc-compliance-parser.sh").absolute()
        #     return True
        # if self.instance.path.startswith("v4l2-compliance"):
        #     self.file_path = Path(
        #         "test_cases/kernelci-core/config/rootfs/debos/overlays/v4l2/usr/bin/v4l2-parser.sh").absolute()
        #     return True
        # if self.instance.path.startswith("igt"):
        #     temp = self.instance.path.split(".")
        #     if len(temp) <= 1:
        #         return False
        #     fp = temp[1] + ".c"
        #     fp_prefix = Path("test_cases/igt-gpu-tools/tests")
        #     if (fp_prefix / fp).exists():
        #         self.file_path = (fp_prefix / fp).absolute()
        #         return True


class DBTest(Base):
    __tablename__ = 'test'

    build_id = Column(String, ForeignKey('build.id'), primary_key=True)
    id = Column(String, primary_key=True)
    origin = Column(String)
    path = Column(String)
    log_url = Column(String)
    status = Column(String)
    waived = Column(String)
    start_time = Column(String)
    output_files = Column(Text)
    has_known_issues = Column(String)
    known_issues = Column(Text)

    build = relationship('DBBuild', back_populates='tests')

    def __str__(self):
        return f"Test{{ build_id: {self.build_id}, id: {self.id}, origin: {self.origin}, " \
               f"path: {self.path}, log_url: {self.log_url}, status: {self.status}, " \
               f"waived: {self.waived}, start_time: {self.start_time}, output_files: {self.output_files}}}"


class Checkout:
    def __init__(self, db_instance: 'DBCheckout'):
        self.instance = db_instance
        self.builds = [Build(x) for x in self.instance.builds]

    def get_all_testcases(self) -> List['Test']:
        return [test_case for build in self.builds for test_case in build.get_all_testcases()]

    def filter_builds_with_less_tests(self, minimal_cases=100):
        temp = []
        for build in self.builds:
            if len(build.get_all_testcases()) < minimal_cases:
                continue
            temp.append(build)
        self.builds = temp

    def select_build_by_config(self, config_name):
        temp = []
        for build in self.builds:
            if build.instance.config_name == config_name:
                temp.append(build)
        self.builds = temp

    def __str__(self):
        return str(self.instance)


class DBCheckout(Base):
    __tablename__ = 'checkout'

    id = Column(String, primary_key=True)
    origin = Column(String)
    tree_name = Column(String)
    git_repository_url = Column(String)
    git_commit_hash = Column(String)
    git_repository_branch = Column(String)
    patchset_files = Column(Text)
    patchset_hash = Column(String)
    comment = Column(Text)
    start_time = Column(String)
    contacts = Column(Text)
    valid = Column(Integer)
    misc = Column(Text)

    builds = relationship('DBBuild', back_populates='checkout')

    def __str__(self):
        return f"Checkout{{id: {self.id}, origin: {self.origin}, tree_name: {self.tree_name}, " \
               f"git_repository_url: {self.git_repository_url}, git_commit_hash: {self.git_commit_hash}, " \
               f"git_repository_branch: {self.git_repository_branch}, patchset_files: {self.patchset_files}, " \
               f"patchset_hash: {self.patchset_hash}, comment: {self.comment}, start_time: {self.start_time}, " \
               f"contacts: {self.contacts}, valid: {self.valid}, misc: {self.misc}, builds: {len(self.builds)} builds}}"


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
        self.ci_objs = sorted(self.ci_objs, key=lambda x: x.instance.start_time)

    def select(self, build_config: str):
        for ci_obj in self.ci_objs:
            ci_obj.select_build_by_config(build_config)
        # return CIAnalysis(res)

    def get_all_testcases(self) -> List['Test']:
        return [test_case for ci_obj in self.ci_objs for test_case in ci_obj.get_all_testcases()]

    @staticmethod
    def _filter_unknown_test_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                temp = []
                for test_case in build.tests:
                    if not test_case.is_unknown():
                        temp.append(test_case)
                build.tests = temp
        return ci_objs

    # 默认已经经过`select`方法了，即build_label只存在一个
    # TODO 这个逻辑需要改，需要定义一下flaky test的pattern，一起过滤了
    def filter_always_failed_test_cases(self, ci_objs):
        # TODO 用test_path 还是 test_file作为过滤的key
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                temp = []
                for test_case in build.tests:
                    # TODO filter has known issues test cases
                    if test_case.instance.has_known_issues == "1":
                        continue
                    if self.test_case_status_map[test_case.instance.path]:
                        temp.append(test_case)
                build.tests = temp
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
                f"{ci_obj.instance.git_repository_branch}: {l1} / {len(test_cases)} failed. Unique test path count: {len(path_set)}. "
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
    def _filter_no_file_test_cases(ci_objs):
        for ci_obj in ci_objs:
            for build in ci_obj.builds:
                temp = []
                for test_case in build.tests:
                    if test_case.map_test():
                        temp.append(test_case)
                    # else:
                    #     if "login" in test_case.test_path or "speculative" in test_case.test_path:
                    #         continue
                    # TestCase.not_mapped_set.add(f"{test_plan.test_plan}: {test_case.test_path}")
                build.tests = temp
        return ci_objs

    def _filter_test_cases_by_type(self, ci_objs):

        # logger.info("process!")
        for ci_obj in ci_objs:
            # logger.info("process-obj!")
            for build in ci_obj.builds:
                temp = []
                for test_case in build.tests:
                    if test_case.type in self.used_type():
                        temp.append(test_case)
                build.tests = temp

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
    def _combine_same_test_file_case(ci_objs: List['DBCheckout']):
        for ci_obj in ci_objs:
            status_m = {}
            for build in ci_obj.builds:
                temp = []
                for testcase in build.tests:
                    if testcase.file_path in status_m.keys():
                        status_m[testcase.file_path].merge_status(testcase)
                        continue
                    status_m[testcase.file_path] = testcase
                    temp.append(testcase)
                build.tests = temp
            # update status
            for build in ci_obj.builds:
                for i in range(len(build.tests)):
                    build.tests[i].merge_status(status_m[build.tests[i].file_path])
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
        for t in tqdm(self.get_all_testcases(), desc="map file path"):
            t.map_test()

    def filter_job(self, job_task: str, *args, **kwargs):
        arguments = [self.ci_objs[i:i + self.execution_number_per_thread] for i in
                     range(0, len(self.ci_objs), self.execution_number_per_thread)]
        job_func = None
        if job_task == "FILTER_UNKNOWN_CASE":
            logger.info(f"filter unknown test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_unknown_test_cases

        if job_task == "FILTER_CASE_BY_TYPE":
            logger.info(f"filter {kwargs['case_type']} test cases job start. Threads number: {self.number_of_threads}.")
            # logger.info("????")
            self.used_type(kwargs['case_type'])
            # logger.info("!!!!!")
            job_func = self._filter_test_cases_by_type

        if job_task == "FILTER_NOFILE_CASE":
            logger.info(f"filter test cases with no file job start. Threads number: {self.number_of_threads}.")
            job_func = self._filter_no_file_test_cases

        if job_task == "COMBINE_SAME_CASE":
            logger.info(f"combine same test cases job start. Threads number: {self.number_of_threads}.")
            job_func = self._combine_same_test_file_case

        if job_task == "FILTER_ALLFAIL_CASE":
            logger.info(f"filter always failed test cases job start. Threads number: {self.number_of_threads}.")
            _ = self.test_case_status_map
            job_func = self.filter_always_failed_test_cases

        if job_func is not None:
            before = len(self.get_all_testcases())
            res = pqdm(arguments, job_func, n_jobs=self.number_of_threads,
                       desc="Filter test cases with unknown status", leave=False)
            self.ci_objs = []
            for x in res:
                self.ci_objs.extend(x)
            self.reorder()
            after = len(self.get_all_testcases())
            logger.info(f"filter {before - after} test cases, reduce test_cases from {before} to {after}")

        if job_task == "FILTER_SMALL_BRANCH":
            logger.info(
                f"filter branches with small cases (less than{kwargs['minimal_testcases']}) job start. Threads number: {self.number_of_threads}.")
            self.filter_branches_with_few_testcases(minimal_testcases=kwargs['minimal_testcases'])


def load_cia(file_path) -> 'CIAnalysis':
    return pickle.load(Path(file_path).open("rb"))
