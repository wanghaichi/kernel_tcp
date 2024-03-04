import pickle
from enum import Enum
from pathlib import Path
from typing import List

from pqdm.threads import pqdm
from sqlalchemy import Column, String, ForeignKey, Text, Boolean, Integer, DateTime
from sqlalchemy.orm import declarative_base, relationship
from tqdm import tqdm

# from liebes.ci_logger import logger
from liebes.test_path_mapping import has_mapping

Base = declarative_base()


class DBConfig(Base):
    __tablename__ = 'config'
    id = Column(Integer, primary_key=True)
    url = Column(String(255))
    content = Column(Text)
    name = Column(String(255))


class DBCheckout(Base):
    __tablename__ = 'checkout'

    id = Column(String(100), primary_key=True)
    testruns = Column(String(200))
    testjobs = Column(String(200))
    status = Column(String(200))
    git_repo = Column(String(200))
    git_repo_branch = Column(String(200))
    git_sha = Column(String(200))
    git_describe = Column(String(200))
    kernel_version = Column(String(200))
    created_at = Column(String(200))
    patch_id = Column(String(200))
    patch_url = Column(String(200))
    patch_source = Column(String(200))
    git_commit_datetime = Column(DateTime)

    builds = relationship('DBBuild', back_populates='checkout',
                          primaryjoin="and_(DBCheckout.id == DBBuild.checkout_id, DBBuild.build_name =='clang-17-lkftconfig-compat', DBBuild.arch == 'x86_64', DBBuild.build_name != '')")

    def __str__(self):
        return (
            f"Checkout(id={self.id}, testruns={self.testruns}, testjobs={self.testjobs}, "
            f"status={self.status}, git_repo={self.git_repo}, git_repo_branch={self.git_repo_branch}, "
            f"git_sha={self.git_sha}, git_describe={self.git_describe}, "
            f"kernel_version={self.kernel_version}, created_at={self.created_at}, "
            f"patch_id={self.patch_id}, patch_url={self.patch_url}, patch_source={self.patch_source})"
        )


class DBBuild(Base):
    __tablename__ = 'build'

    id = Column(String(100), primary_key=True)
    checkout_id = Column(String, ForeignKey('checkout.id'), primary_key=True)
    plan = Column(String(100))
    kconfig = Column(Text)
    arch = Column(String(200))
    build_name = Column(String(200))
    status = Column(String(60))
    duration = Column(String(200))
    start_time = Column(String(200))
    download_url = Column(String(200))

    checkout = relationship('DBCheckout', back_populates='builds', lazy='joined')
    testruns = relationship('DBTestRun', back_populates='build', lazy='joined')

    # tests = relationship('DBTest', back_populates='build')

    def __str__(self):
        return (
            f"Build(id={self.id}, checkout_id={self.checkout_id}, plan={self.plan}, "
            f"kconfig={self.kconfig}, arch={self.arch}, build_name={self.build_name}, "
            f"status={self.status}, duration={self.duration}, start_time={self.start_time}, "
            f"download_url={self.download_url})"
        )


class DBTestRun(Base):
    __tablename__ = 'testrun'

    id = Column(String(100), primary_key=True)
    build_id = Column(String(200), ForeignKey('build.id'))
    tests_file = Column(String(200))
    log_file = Column(String(200))
    test_url = Column(String(200))
    job_url = Column(String(200))
    created_at = Column(String(200))
    download_url = Column(String(200))
    build_name = Column(String(200))

    # Define relationships
    # checkout = relationship('Checkout', back_populates='testruns')
    build = relationship('DBBuild', back_populates='testruns', lazy='joined')
    tests = relationship('DBTest',
                         back_populates='testrun',
                         lazy='joined',
                         primaryjoin="and_(DBTestRun.id == DBTest.testrun_id, DBTest.file_path != None)")

    def __str__(self):
        return (
            f"TestRun(id={self.id}, checkout_id={self.checkout_id}, build_id={self.build_id}, "
            f"tests_file={self.tests_file}, log_file={self.log_file}, tests={self.tests}, "
            f"job_url={self.job_url}, created_at={self.created_at}, "
            f"download_url={self.download_url}, build_name={self.build_name})"
        )


class DBTest(Base):
    __tablename__ = 'test'

    id = Column(String(100), primary_key=True)
    testrun_id = Column(String(200), ForeignKey('testrun.id'))
    status = Column(String(100))
    result = Column(String(100))
    path = Column(String(200))
    log_url = Column(Text)
    has_known_issues = Column(Boolean)
    known_issues = Column(Text)
    environment = Column(Text)
    suite = Column(Text)
    file_path = Column(Text)
    TP = Column(Integer)

    # Define relationships
    testrun = relationship('DBTestRun', back_populates='tests', lazy='joined')

    def __str__(self):
        return (
            f"Test(id={self.id}, testrun_id={self.testrun_id}, status={self.status}, "
            f"result={self.result}, path={self.path}, build_id={self.build_id}, "
            f"build_name={self.build_name}, log_url={self.log_url}, "
            f"has_known_issues={self.has_known_issues}, known_issues={self.known_issues}, "
            f"environment={self.environment}, suite={self.suite}, file_path={self.file_path}, "
            f"TP={self.TP})"
        )


class TestCaseType(Enum):
    UNKNOWN = 0
    C = 1
    SH = 2
    PY = 3


class Checkout:
    def __init__(self, db_instance: 'DBCheckout'):
        self.instance = db_instance
        self.builds = [Build(x) for x in self.instance.builds]

    def get_all_testcases(self) -> List['Test']:
        return [test_case for build in self.builds for test_case in build.get_all_testcases()]

    def get_case_by_file_path(self, file_path: str) -> 'Test' or None:
        for tc in self.get_all_testcases():
            if tc.file_path == file_path:
                return tc
        return None
        # def combine_build(self):

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
            if build.instance.build_name == config_name:
                temp.append(build)
        self.builds = temp

    def __str__(self):
        return str(self.instance)


class Build:
    def __init__(self, db_instance: 'DBBuild'):
        self.instance = db_instance
        self.testruns = [TestRun(x) for x in self.instance.testruns]
        # self.tests = [Test(x) for x in self.instance.tests]

    @property
    def label(self) -> str:
        return self.instance.build_name

    def get_all_testcases(self) -> List['Test']:
        return [t for r in self.testruns for t in r.get_all_testcases()]

    def __str__(self):
        return str(self.instance)


class TestRun:
    def __init__(self, db_instance: 'DBTestRun'):
        self.instance = db_instance
        self.tests = [Test(x) for x in self.instance.tests]

    def get_all_testcases(self) -> List['Test']:
        return self.tests

    def __str__(self):
        return str(self.instance)


class Test:
    def __init__(self, db_instance: 'DBTest'):
        self.instance = db_instance
        self._type = None
        self.file_path = self.instance.file_path
        self.id = self.instance.id
        if self.instance.status == "Test executed successfully" or self.instance.status.lower() == "pass":
            self.status = 0
        elif self.instance.status == "Test execution failed" or self.instance.status.lower() == "fail":
            self.status = 1
        elif self.instance.status == "Test execution regressed":
            self.status = 2
        else:
            self.status = 3
        # filter TP case
        if self.is_failed() and self.instance.TP == 1:
            self.status = 0

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
        return (self.status == 0 or self.status == 10)
        # return self.instance.status != 'fail' or self.instance.TP is None

    def is_unknown(self):
        return self.status == 3

    def is_failed(self):
        return self.status in [1, 2]

    def merge_status(self, other_testcase: 'DBTest'):
        if self.is_pass() and other_testcase.is_pass():
            pass
        else:
            self.status = 1
            self.id = other_testcase.id

    def map_test(self) -> bool:
        if self.file_path is not None:
            return True
        if self.instance.file_path is not None:
            self.file_path = self.instance.file_path
            return True
        p = has_mapping(self.instance.path)
        if p is not None:
            if Path(p).exists():
                self.file_path = Path(p)
                return True
        return False
