import json
from datetime import datetime

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.ir_model import *
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *


class TestCaseInfo:
    def __init__(self):
        self.file_path = ""
        self.type = ""


def update_token_mapping(m, mapping_path):
    json.dump(m, Path(mapping_path).open("w"))


def do_exp(cia: CIAnalysis, tokenizer: BaseTokenizer, ir_model: BaseModel, context_strategy=""):
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
        if gitHelper.get_commit_info(ci_obj.instance.git_sha) is None:
            logger.debug(f"commit not exist, {ci_obj.instance.git_sha}")
            continue
        last_ci_obj = cia.ci_objs[ci_index - 1]
        # start iteration of one test result
        # 1. first extract the faults result
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if test_cases[i].is_failed():
                faults_arr.append(i)
        if len(faults_arr) == 0:
            continue
        # 2. get code changes
        code_changes = gitHelper.get_diff_contents(
            last_ci_obj.instance.git_sha, ci_obj.instance.git_sha,
            context_strategy)
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
                    # print(e)
                    # print(t.file_path)
                    tokens = []
                    # continue
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
        logger.debug(f"model: {ir_model.name}, commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}")
        apfd_res.append(apfd_v)
    logger.info(f"model: {ir_model.name}, avg apfd: {np.average(apfd_res)}")
    return f"model: {ir_model.name}, avg apfd: {np.average(apfd_res)}"


if __name__ == '__main__':
    linux_path = '/home/wanghaichi/linux-1'
    sql = SQLHelper()
    start_time = datetime.now()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(20).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.ci_objs = cia.ci_objs[1:]
    cia.statistic_data()
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
    # TODO 加个多线程的方式
    summary = []
    for tokenizer in tokenizers:
        for ir_model in ir_models:
            res = do_exp(cia, tokenizer, ir_model, context_strategy)
            summary.append(res)
    logger.info("summary :---------------------------------")
    logger.info(f"use strategy: {context_strategy}")
    for s in summary:
        logger.info(s)
