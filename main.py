import json
import os
import time

import numpy as np

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.tokenizer import *
from liebes.ir_model import *
from datetime import datetime


class TestCaseInfo:
    def __init__(self):
        self.file_path = ""
        self.type = ""


def update_token_mapping(m, mapping_path):
    json.dump(m, Path(mapping_path).open("w"))


def do_exp(cia: CIAnalysis, tokenizer: BaseTokenizer, ir_model: BaseModel):
    ehelper = EHelper()
    gitHelper = GitHelper(linux_path)
    mapping_path = f"token-{tokenizer.name}.json"
    if Path(mapping_path).exists():
        m = json.load(Path(mapping_path).open("r"))
    else:
        m = {}
    apfd_res = []
    for ci_index in range(1, len(cia.ci_objs)):
        ci_obj = cia.ci_objs[ci_index]
        if gitHelper.get_commit_info(ci_obj.instance.git_commit_hash) is None:
            print(1)
            continue
        last_ci_obj = cia.ci_objs[ci_index - 1]
        # start iteration of one test result
        # 1. first extract the faults result
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if not test_cases[i].is_pass():
                faults_arr.append(i)
        if len(faults_arr) == 0:
            continue
        # 2. get code changes
        code_changes = gitHelper.get_diff_contents(last_ci_obj.instance.git_commit_hash
                                                   , ci_obj.instance.git_commit_hash)
        # Assert the code changes must greater than 5
        if len(code_changes) == 0:
            continue
        # 3. second obtain the sort result
        token_arr = []
        for i in range(len(test_cases)):
            t = test_cases[i]
            if str(t.file_path) in m.keys():
                token_arr.append(m[str(t.file_path)])
            else:
                try:
                    tokens = tokenizer.get_tokens(Path(t.file_path).read_text(), t.type)
                except Exception as e:
                    print(e)
                    print(t.file_path)
                    continue

                v = " ".join(tokens)
                v = v.lower()
                token_arr.append(v)
                m[str(t.file_path)] = v
                json.dump(m, Path(mapping_path).open("w"))
        queries = []
        for cc in code_changes:
            tokens = tokenizer.get_tokens(cc, TestCaseType.C)
            queries.append(" ".join(tokens))
        # print(f"corpus: {len(token_arr)}, queries: {len(queries)}")
        s = ir_model.get_similarity(token_arr, queries)

        print(s.shape)
        similarity_sum = np.sum(s, axis=1)
        # print(similarity_sum)
        # print(len(similarity_sum))

        order_arr = np.argsort(similarity_sum)[::-1]

        apfd_v = ehelper.APFD(faults_arr, order_arr)
        print(f"model: {ir_model.name}, commit: {ci_obj.instance.git_commit_hash}, apfd: {apfd_v}")
        apfd_res.append(apfd_v)
    print(f"model: {ir_model.name}, avg apfd: {np.average(apfd_res)}")
    return f"model: {ir_model.name}, avg apfd: {np.average(apfd_res)}"


if __name__ == '__main__':
    linux_path = '/home/wanghaichi/linux-1'
    build_label = "all"
    cia = load_cia("cia-fil-1.pkl")
    # cia.ci_objs = cia.ci_objs[:10]
    failed_map = {}
    cia.statistic_data()
    total = len(cia.ci_objs)
    for ci_obj in cia.ci_objs:
        failed_testcases = [x.instance.path for x in ci_obj.get_all_testcases() if (not x.is_pass())]
        for ft in failed_testcases:
            if ft not in failed_map.keys():
                failed_map[ft] = 0
            failed_map[ft] += 1
    flaky_set = set()
    for k, v in failed_map.items():
        if v / total > 0.6:
            flaky_set.add(k)
        # print(f"{k}: {v}/{total} {v/total}")
    # TODO 封装起来
    for ci_obj in cia.ci_objs:
        for build in ci_obj.builds:
            temp = []
            for test_case in build.tests:
                if test_case.instance.path in flaky_set:
                    continue
                temp.append(test_case)
            build.tests = temp

    # cia.statistic_data()
    # failed_map = {}
    # for ci_obj in cia.ci_objs:
    #     failed_testcases = [str(x.file_path) for x in ci_obj.get_all_testcases() if (not x.is_pass())]
    #     for ft in failed_testcases:
    #         if ft not in failed_map.keys():
    #             failed_map[ft] = 0
    #         failed_map[ft] += 1
    # flaky_set = set()
    # for k, v in failed_map.items():
    #     print(f"{k}: {v}/{total} {v/total}")

    # cia.filter_job("FILTER_CASE_BY_TYPE", case_type=[TestCaseType.C])
    cia.statistic_data()

    # exit(-1)
    # ttt = set()
    # for t in [x for x in cia.get_all_testcases() if x.type == TestCaseType.SH]:
    #     ttt.add(t)
    #
    # for t in ttt:
    #     print(f"{t.test_path}: {t.file_path}")
    #
    # exit(-1)
    tokenizers = [AstTokenizer()]
    ir_models = [
        # Bm25Model(),
        TfIdfModel(),
        # RandomModel(),
        # RandomModel(),
        # RandomModel(),
        # RandomModel(),

        LSIModel(num_topics=2),
        # LSIModel(num_topics=3),
        # LSIModel(num_topics=4),
        # LSIModel(num_topics=5),
        LDAModel(num_topics=2),
        # LDAModel(num_topics=3),
        # LDAModel(num_topics=4),
        # LDAModel(num_topics=5),
        Bm25Model(),
    ]

    # tokenizer = AstTokenizer()
    # ir_model = TfIdfModel()
    # TODO 加个多线程的方式
    summary = []
    for tokenizer in tokenizers:
        for ir_model in ir_models:
            res = do_exp(cia, tokenizer, ir_model)
            summary.append(res)
    print("summary :---------------------------------")
    for s in summary:
        print(s)
