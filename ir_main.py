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
from multiprocessing import Pool


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
        print(f"code changes: \n{code_changes}")
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
    parser.add_argument("--history", type=int, default=0, help="regression last version")
    parser.add_argument("--process", type=int, default=1, help="number of process")
    args = parser.parse_args()
    logger.info(args)
    #
    # if not Path("cia_04-01.pkl").exists():
    #     sql = SQLHelper()
    #     checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).all()
    #
    #     # # checkouts = sql.session.query(DBCheckout).limit(10).all()
    #     cia = CIAnalysis()
    #     for ch in checkouts:
    #         cia.ci_objs.append(Checkout(ch))
    #     cia.reorder()
    #     cia.set_parallel_number(40)
    #     cia.filter_job("COMBINE_SAME_CASE")
    #     cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    #     cia.filter_job("COMBINE_SAME_CONFIG")
    #     cia.filter_job("CHOOSE_ONE_BUILD")
    #     cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    #     cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    #     cia.ci_objs = cia.ci_objs[1:]
    #     pickle.dump(cia, open("cia_04-01.pkl", "wb"))
    # else:
    #     cia = pickle.load(open("cia_04-01.pkl", "rb"))
    # cia.statistic_data()


    versions = ['91ec4b0d11fe115581ce2835300558802ce55e6c','1ae78a14516b9372e4c90a89ac21b259339a3a3a','58390c8ce1bddb6c623f62e7ed36383e7fa5c02f','671e148d079f4d4eca0a98f7dadf1fe69d856374','d295b66a7b66ed504a827b58876ad9ea48c0f4a8','533c54547153d46c0bf99ac0e396bed71f760c03','e338142b39cf40155054f95daa28d210d2ee1b2d','8d15d5e1851b1bbb9cd3289b84c7f32399e06ac5','1639fae5132bc8a904af28d97cea0bedb3af802e','2214170caabbff673935eb046a7edf4621213931','3a8a670eeeaa40d87bd38a587438952741980c18','6cdbb0907a3c562723455e351c940037bdec9b7a','a901a3568fd26ca9c4a82d8bc5ed5b3ed844d451','03275585cabd0240944f19f33d7584a1b099a3a8','3290badd1bb8c9ea91db5c0b2e1a635178119856','7fcd473a6455450428795d20db7afd2691c92336','06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5','fdf0eaf11452d72945af31804e2a1048ee1b574c','18b44bc5a67275641fb26f2c54ba7eef80ac5950','ffabf7c731765da3dbfaffa4ed58b51ae9c2e650','251a94f1f66e909d75a774ac474a63bd9bc38382','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','25aa0bebba72b318e71fe205bfd1236550cc9534','ae545c3283dc673f7e748065efa46ba95f678ef2','4c75bf7e4a0e5472bd8f0bf0a4a418ac717a9b70','b320441c04c9bea76cbee1196ae55c20288fd7a6','28f20a19294da7df158dfca259d0e2b5866baaf9','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','1c59d383390f970b891b503b7f79b63a02db2ec5','b96a3e9142fdf346b05b20e867b4f0dfca119e96','53ea7f624fb91074c2f9458832ed74975ee5d64c','ef2a0b7cdbc5b84f7b3f6573b7687e72bede0964','4debf77169ee459c46ec70e13dc503bc25efd7d2','e0152e7481c6c63764d6ea8ee41af5cf9dfac5e9','92901222f83d988617aee37680cb29e1a743b5e4','3f86ed6ec0b390c033eae7f9c487a3fea268e027','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','744a759492b5c57ff24a6e8aabe47b17ad8ee964','dd1386dd3c4f4bc55456c88180f9f39697bb95c0','2a5a4326e58339a26cd1510259e7310b8c0980ff','535a265d7f0dd50d8c3a4f8b4f3a452d56bd160f','aed8aee11130a954356200afa3f1b8753e8a9482','ad8a69f361b9b9a0272ed66f04e6060b736d2788','8018e02a87031a5e8afcbd9d35133edd520076bb','830380e3178a103d4401689021eadddadbb93d6d','84186fcb834ecc55604efaf383e17e6b5e9baa50','750b95887e567848ac2c851dae47922cac6db946','be3ca57cfb777ad820c6659d52e60bbdd36bf5ff','90450a06162e6c71ab813ea22a83196fe7cff4bc']
    sql_helper = SQLHelper()
    checkouts = sql_helper.session.query(DBCheckout).filter(DBCheckout.git_sha.in_(versions)).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("COMBINE_SAME_CONFIG")
    cia.filter_job("CHOOSE_ONE_BUILD")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)

    cia.statistic_data()
    # exit(-1)
    linux_path = '/home/wanghaichi/linux'

    # for ci_obj in cia.ci_objs:
    #     if ci_obj.instance.git_sha == "6cdbb0907a3c562723455e351c940037bdec9b7a":
    #         test_cases = ci_obj.get_all_testcases()
    #         failed_cases = [x for x in test_cases if x.is_failed()]
    #         print(f"commit: {ci_obj.instance.git_sha}, failed cases: {len(failed_cases)}")
    #         for fc in failed_cases:
    #             print(f"file path: {fc.file_path}, type: {fc.type}")
    # exit(-1)
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

    process_pool = Pool(processes=args.process)
    input_data = []
    for tokenizer in tokenizers:
        for ir_model in ir_models:
            input_data.append((cia, tokenizer, ir_model, context_strategy, args.history))
    res = process_pool.starmap(do_exp, input_data)
            # res = do_exp(cia, tokenizer, ir_model, context_strategy, args.history)
            # summary.append(res)\
    process_pool.close()
    process_pool.join()
    logger.info("summary :---------------------------------")
    logger.info(f"use strategy: {context_strategy}")
    for s in res:
        logger.info(s)
