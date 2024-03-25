import json


class LTPResult:
    def __init__(self):
        self.cmdline = ""
        self.duration = ""
        self.cost = ""
        self.collect_cov_cost = ""
        self.pass_cnt = 0
        self.skip_cnt = 0
        self.broken_cnt = 0
        self.fail_cnt = 0

    def is_valid(self):
        return self.pass_cnt + self.skip_cnt + self.broken_cnt + self.fail_cnt > 0

    def __str__(self):
        return f"cmdline: {self.cmdline}, duration: {self.duration}, cost: {self.cost}, pass_cnt: {self.pass_cnt}, skip_cnt: {self.skip_cnt}, broken_cnt: {self.broken_cnt}, fail_cnt: {self.fail_cnt}"

    def dump_to_json(self, file_path):
        with open(file_path, "w") as f:
            f.write(json.dumps(self.__dict__, indent=4))

    def load_from_json(self, file_path):
        with open(file_path, "r") as f:
            data = json.load(f)
            self.cmdline = data["cmdline"]
            self.duration = data["duration"]
            self.cost = data["cost"]
            self.pass_cnt = data["pass_cnt"]
            self.skip_cnt = data["skip_cnt"]
            self.broken_cnt = data["broken_cnt"]
            self.fail_cnt = data["fail_cnt"]