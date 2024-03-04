"""
This file is used to achieve the information of the test case, coverage, history, etc.
Input: testcase, relevant information
Output: extracted information for each test case
"""
from liebes.analysis import CIAnalysis


class InformationManager:
    def __init__(self, cia: "CIAnalysis"):
        self.cia = cia
        pass


class HistoryInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis"):
        super().__init__(cia)
        self.history_information = []

    def get_last_executed_time(self):
        pass


class TestCaseInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis"):
        super().__init__(cia)
        self.test_case_information = []


class CoverageInformationManager(InformationManager):
    def __init__(self, cia: "CIAnalysis"):
        super().__init__(cia)
        self.coverage_information = []


if __name__ == "__main__":
    pass
