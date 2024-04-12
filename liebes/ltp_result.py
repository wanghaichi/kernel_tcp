import json
import re


class TCResult:
    def __init__(self):
        self.items = []
        self.total_cost = -1
        self.tc_name = ""
        self.type = ""

    def total_failed_cnt(self):
        return sum([item.fail_cnt for item in self.items])

    def total_broken_cnt(self):
        return sum([item.broken_cnt for item in self.items])

    def total_pass_cnt(self):
        return sum([item.pass_cnt for item in self.items])

    @staticmethod
    def create(tc_name, tc_type, log_content):
        ltp_result = TCResult()
        ltp_result.tc_name = tc_name
        ltp_result.type = tc_type
        ltp_result.parse_log(log_content)
        return ltp_result

    def parse_ltp_log(self, log_content):
        # 1. extract TPASS, TFAIL, TSKIP
        # 2. extract Summary
        # "Summary:
        # passed   3
        # failed   0
        # broken   0
        # skipped  0
        # warnings 0"
        #     # 3. figure out the reason of not executed
        #     # 3.1 xxx not found (need to install the corresponding package)
        #     # 3.2 INFO: ltp-pan reported some tests FAIL (need to check the reason, one reason is
        #     the testcase should be executed in a shell command)

        # get text between
        # <<<test_start>>>
        # <<<test_end>>>
        sub_blocks = []
        start_extracted = False
        for line in log_content.split("\n"):
            if start_extracted:
                extracted_content += line + "\n"
            if line.startswith("<<<test_start>>>"):
                extracted_content = ""
                start_extracted = True
            elif line.startswith("<<<test_end>>>"):
                start_extracted = False
                sub_blocks.append(extracted_content)
            elif line.startswith("Time cost"):
                pattern = r"Time cost: (\d+):(\d+):(\d+\.\d+)s"
                match = re.search(pattern, line)
                if match:
                    h = int(match.group(1))
                    m = int(match.group(2))
                    s = float(match.group(3))
                    self.total_cost = h * 3600 + m * 60 + s

        for rec in sub_blocks:
            self.items.append(self.create_sub_result(rec))

    def parse_selftest_log(self, log_content):
        selftest_result = SelfTestResult()
        for line in log_content.split("\n"):
            if line.startswith("# # Totals"):
                numbers = re.findall(r'\d+', line)
                # pass:2 fail:0 xfail:0 xpass:0 skip:0 error:0
                if len(numbers) != 6:
                    raise Exception(f"invalid line {line}")
                selftest_result.pass_cnt += int(numbers[0]) + int(numbers[3])
                selftest_result.fail_cnt += (int(numbers[1]) + int(numbers[2]))
                selftest_result.skip_cnt += int(numbers[4])
                selftest_result.broken_cnt += int(numbers[5])
            elif line.startswith("Time cost:"):
                pattern = r"Time cost: (\d+):(\d+):(\d+\.\d+)s"
                match = re.search(pattern, line)
                if match:
                    h = int(match.group(1))
                    m = int(match.group(2))
                    s = float(match.group(3))
                    self.total_cost = h * 3600 + m * 60 + s
            elif line.startswith("ok") or line.startswith("not ok"):
                temp = line.split("#")
                if len(temp) == 2:
                    selftest_result.addition_message += temp[1] + "\n"
        self.items.append(selftest_result)
        pass

    def parse_log(self, log_content):
        if self.type == "ltp":
            self.parse_ltp_log(log_content)
        elif self.type == "selftest":
            self.parse_selftest_log(log_content)
        else:
            raise Exception(f"unknown type {self.type}")

    def create_sub_result(self, sub_content):
        ltp_result = LTPResult()
        passed_count = 0
        failed_count = 0
        broken_count = 0

        # print(record)
        has_summary = False
        for line in sub_content.split("\n"):
            line = line.strip()
            if line.startswith("cmdline"):
                match = re.search(r'cmdline="([^"]+)"', line)
                ltp_result.cmdline = match.group(1)
            if line.startswith("duration"):
                match = re.search(r'duration=(\d+)\s', line)
                ltp_result.duration = match.group(1)
            if "TPASS" in line:
                passed_count += 1
            if "TFAIL" in line:
                failed_count += 1
            if "TBROK" in line:
                broken_count += 1

            words_to_match = ["passed", "failed", "broken", "skipped", "warnings"]
            pattern = r'^\b(?:' + '|'.join(words_to_match) + r')\b\s+(\d+)'
            match = re.search(pattern, line)
            if match:
                has_summary = True
                if "passed" in line:
                    ltp_result.pass_cnt = int(match.group(1))
                if "failed" in line:
                    ltp_result.fail_cnt = int(match.group(1))
                if "broken" in line:
                    ltp_result.broken_cnt = int(match.group(1))
                if "skipped" in line:
                    ltp_result.skip_cnt = int(match.group(1))
        if not has_summary:
            ltp_result.pass_cnt = passed_count
            ltp_result.fail_cnt = failed_count
            ltp_result.broken_cnt = broken_count
        return ltp_result

    # def dump_to_json(self, file_path):
    #     with open(file_path, "w") as f:
    #         f.write(json.dumps(self.__dict__, indent=4))
    #
    # def load_from_json(self, file_path):
    #     with open(file_path, "r") as f:
    #         data = json.load(f)
    #         self.cmdline = data["cmdline"]
    #         self.duration = data["duration"]
    #         self.cost = data["cost"]
    #         self.pass_cnt = data["pass_cnt"]
    #         self.skip_cnt = data["skip_cnt"]
    #         self.broken_cnt = data["broken_cnt"]
    #         self.fail_cnt = data["fail_cnt"]


class BaseTestResult:
    def __init__(self):
        self.pass_cnt = 0
        self.skip_cnt = 0
        self.broken_cnt = 0
        self.fail_cnt = 0

    def is_valid(self):
        return self.pass_cnt + self.skip_cnt + self.broken_cnt + self.fail_cnt > 0


class SelfTestResult(BaseTestResult):
    def __init__(self):
        super().__init__()
        self.cmdline = ""
        self.addition_message = ""


class LTPResult(BaseTestResult):
    def __init__(self):
        super().__init__()
        self.cmdline = ""
        self.duration = ""
        self.cost = ""
        self.collect_cov_cost = ""

    def __str__(self):
        return f"cmdline: {self.cmdline}, duration: {self.duration}, cost: {self.cost}, pass_cnt: {self.pass_cnt}, skip_cnt: {self.skip_cnt}, broken_cnt: {self.broken_cnt}, fail_cnt: {self.fail_cnt}"
