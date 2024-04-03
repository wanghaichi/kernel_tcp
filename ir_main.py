import argparse
import json
import pickle
from datetime import datetime

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.ir_model import *
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *
import numpy as np


class TestCaseInfo:
    def __init__(self):
        self.file_path = ""
        self.type = ""


def update_token_mapping(m, mapping_path):
    json.dump(m, Path(mapping_path).open("w"))


def do_exp(cia: CIAnalysis, tokenizer: BaseTokenizer, ir_model: BaseModel, context_strategy="", history=0):
    ehelper = EHelper()
    gitHelper = GitHelper(linux_path)
    mapping_path = f"token-{tokenizer.name}.json"
    if Path(mapping_path).exists():
        m = json.load(Path(mapping_path).open("r"))
    else:
        m = {}
    apfd_res = []
    apfd_seperate = []
    for ci_index in range(1, len(cia.ci_objs)):
        if ci_index < history:
            continue

        ci_obj = cia.ci_objs[ci_index]
        if gitHelper.get_commit_info(ci_obj.instance.git_sha) is None:
            logger.debug(f"commit not exist, {ci_obj.instance.git_sha}")
            continue
        # start iteration of one test result
        # 1. first extract the faults result
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if test_cases[i].is_failed():
                faults_arr.append(i)
        if len(faults_arr) == 0:
            logger.debug(f"no faults detected for checkout {ci_obj.instance.git_sha}")
            continue
        # 2. get code changes
        last_ci_obj = cia.ci_objs[ci_index - history - 1]
        history_obj = cia.ci_objs[ci_index - history]
        code_changes = gitHelper.get_diff_contents(
            last_ci_obj.instance.git_sha, history_obj.instance.git_sha,
            context_strategy)
        # Assert the code changes must greater than 5
        if len(code_changes) == 0:
            logger.debug(f"no code change detected for checkout {ci_obj.instance.git_sha}")
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
                    if tokens is None or len(tokens) == 0:
                        logger.error(f"tokenizer failed with empty tokens, file path {t.file_path}")
                except Exception as e:
                    logger.error(f"tokenizer failed with {e}, file path {t.file_path}, ignore")
                    # print(e)
                    # print(t.file_path)
                    tokens = []
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

        logger.debug(s.shape)
        similarity_sum = np.sum(s, axis=1)
        # print(similarity_sum)
        # print(len(similarity_sum))

        order_arr = np.argsort(similarity_sum)[::-1]

        apfd_v = ehelper.APFD(faults_arr, order_arr)
        logger.info(f"model: {ir_model.name}, commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}")
        apfd_res.append(apfd_v)
        logger.debug("faults test cases file path")
        for fi in faults_arr:
            logger.debug(f"{test_cases[fi].file_path}, {order_arr[fi]}")
        logger.debug("code changes")
        for c in code_changes:
            logger.debug(c)

        # calculate the results for sh, and c files
        faults_c = []
        faults_sh = []
        for f_i in faults_arr:
            if test_cases[f_i].type == TestCaseType.C:
                faults_c.append(f_i)
            elif test_cases[f_i].type == TestCaseType.SH:
                faults_sh.append(f_i)
        order_arr_c = []
        order_arr_sh = []
        for i in range(len(order_arr)):
            o_i = order_arr[i]
            if test_cases[o_i].type == TestCaseType.C:
                order_arr_c.append(o_i)
            elif test_cases[o_i].type == TestCaseType.SH:
                order_arr_sh.append(o_i)
        apfd_v_c = ehelper.APFD(faults_c, order_arr_c)
        apfd_v_sh = ehelper.APFD(faults_sh, order_arr_sh)
        logger.info(f"his: {history}, model: {ir_model.name}, commit: {ci_obj.instance.git_sha}, apfd_c: {apfd_v_c}")
        logger.info(f"his: {history}, model: {ir_model.name}, commit: {ci_obj.instance.git_sha}, apfd_sh: {apfd_v_sh}")
        apfd_seperate.append((apfd_v_c, apfd_v_sh))

    logger.info(
        f"his: {history}, model: {ir_model.name}, avg apfd: {np.average(apfd_res)}, apfd_c: {np.average([x[0] for x in apfd_seperate])}, apfd_sh: {np.average([x[1] for x in apfd_seperate])}")
    return f"his: {history}, model: {ir_model.name}, avg apfd: {np.average(apfd_res)}, apfd_c: {np.average([x[0] for x in apfd_seperate])}, apfd_sh: {np.average([x[1] for x in apfd_seperate])}"


def extract_log():
    # IR - main
    root_path = "logs/main-2024-03-31-15:30:25.txt"
    text = Path(root_path).read_text().split("\n")
    res = {}
    for i in range(len(text)):
        line = text[i]
        import re

        pattern = r"INFO  model: ([^,]+), commit: ([^,]+), apfd: ([\d.]+)"
        matches = re.search(pattern, line)

        if matches:
            model = matches.group(1)
            commit = matches.group(2)
            apfd = matches.group(3)
            if commit not in res.keys():
                res[commit] = []
            res[commit].append(apfd)
            # print("Model:", model)
            # print("Commit:", commit)
            # print("APFD:", apfd)
    for k, v in res.items():
        s = " ".join(v)
        print(f"{k} {s}")


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument("--history", type=int, default=15, help="regression last version")

    args = parser.parse_args()
    logger.info(args)

    if not Path("cia_04-01.pkl").exists():
        sql = SQLHelper()
        checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()

        # # checkouts = sql.session.query(DBCheckout).limit(10).all()
        cia = CIAnalysis()
        for ch in checkouts:
            cia.ci_objs.append(Checkout(ch))
        cia.reorder()
        cia.set_parallel_number(40)
        cia.filter_job("COMBINE_SAME_CASE")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cia.filter_job("COMBINE_SAME_CONFIG")
        cia.filter_job("CHOOSE_ONE_BUILD")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
        cia.ci_objs = cia.ci_objs[1:]
        pickle.dump(cia, open("cia_04-01.pkl", "wb"))
    else:
        cia = pickle.load(open("cia_04-01.pkl", "rb"))
    cia.statistic_data()

    linux_path = '/home/wanghaichi/linux'

    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()
    #
    # cia = CIAnalysis()
    # cia.set_parallel_number(40)
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # cia.ci_objs = cia.ci_objs[1:]
    # cia.statistic_data()

    tokenizers = [AstTokenizer()]
    ir_models = [
        TfIdfModel(),
        LSIModel(num_topics=2),
        LDAModel(num_topics=2),
        Bm25Model(),
    ]

    context_strategy = "default"
    # tokenizer = AstTokenizer()
    # ir_model = TfIdfModel()
    logger.info("start exp, use context strategy: " + context_strategy)
    # TODO 加个多线程的方式
    summary = []
    for tokenizer in tokenizers:
        for ir_model in ir_models:
            res = do_exp(cia, tokenizer, ir_model, context_strategy, args.history)
            summary.append(res)
    logger.info("summary :---------------------------------")
    logger.info(f"use strategy: {context_strategy}")
    for s in summary:
        logger.info(s)
