import os

import numpy as np

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.tokenizer import *
from liebes.ir_model import *


class TestCaseInfo:
    def __init__(self):
        self.file_path = ""
        self.type = ""


def iterate_files(root_folder):
    res = []
    for folder_name, _, filenames in os.walk(root_folder):
        for filename in filenames:
            file_path = os.path.join(folder_name, filename)
            file_path = file_path.replace("test_cases/igt-gpu-tools/", "")
            # file_path = file_path.replace("/", "_")
            res.append(file_path)
    return res


def update_token_mapping(m, mapping_path):
    json.dump(m, Path(mapping_path).open("w"))


def do_exp(cia: CIAnalysis, tokenizer: BaseTokenizer, ir_model: BaseModel):
    mapping_path = f"token-{tokenizer.name}.json"
    if Path(mapping_path).exists():
        m = json.load(Path(mapping_path).open("r"))
    else:
        m = {}
    apfd_res = []
    for ci_index in range(1, len(cia.ci_objs)):
        ci_obj = cia.ci_objs[ci_index]
        last_ci_obj = cia.ci_objs[ci_index - 1]
        # start iteration of one test result
        # 1. first extract the faults result
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if not test_cases[i].is_pass():
                faults_arr.append(i)

        # 2. get code changes
        code_changes = gitHelper.get_diff_contents(last_ci_obj.commit_hash, ci_obj.commit_hash)

        # 3. second obtain the sort result
        token_arr = []
        for i in range(len(test_cases)):
            t = test_cases[i]
            if str(t.file_path) in m.keys():
                token_arr.append(m[str(t.file_path)])
            else:
                tokens = tokenizer.get_tokens(Path(t.file_path).read_text())
                v = " ".join(tokens)
                v = v.lower()
                token_arr.append(v)
                m[str(t.file_path)] = v
        queries = []
        for cc in code_changes:
            tokens = tokenizer.get_tokens(cc)
            queries.append(" ".join(tokens))
        # print(f"corpus: {len(token_arr)}, queries: {len(queries)}")
        s = ir_model.get_similarity(token_arr, queries)

        print(s.shape)
        similarity_sum = np.sum(s, axis=1)
        # print(similarity_sum)
        # print(len(similarity_sum))
        order_arr = np.argsort(similarity_sum)[::-1]
        apfd_v = ehelper.APFD(faults_arr, order_arr)
        print(f"model: {ir_model.name}, commit: {ci_obj.commit_hash}, apfd: {apfd_v}")
        apfd_res.append(apfd_v)
    print(f"model: {ir_model.name}, avg apfd: {np.average(apfd_res)}")


if __name__ == '__main__':
    # data_path = Path("dataset/mainline-master/data0.json")
    # ci_obj = CIObj.load_from_json("dataset/mainline-master/data0.json")
    # ci_obj.print_with_intent()
    cia = CIAnalysis()
    for i in range(20):
        ci_obj = CIObj.load_from_json(f"dataset/next-master/data{i}.json")
        cia.ci_objs.append(ci_obj)
    pickle.dump(cia, Path("cia-next-master.pkl").open("wb"))


    linux_path = '/home/duyiheng/linux/linux'
    gitHelper = GitHelper(linux_path)
    ehelper = EHelper()
    cia = load_cia("cia.pkl")
    for ci_obj in cia.ci_objs:
        for build in ci_obj.builds:
            print(build.label)
    exit(-1)
    # for i in range(len(cia.ci_objs) -

    #     gitHelper.diff(cia.ci_objs[i].commit_hash, cia.ci_objs[i+1].commit_hash)

    # cia = cia.select("arm64/defconfig+arm64-chromebook")
    # cia.filter_unknown_test_cases()
    # cia.filter_always_failed_test_cases()
    # cia.filter_no_file_test_cases()
    # cia.filter_c_test_cases()

    # pickle.dump(cia, Path("cia-filter.pkl").open("wb"))
    cia = load_cia("cia-filter.pkl")

    # cia.combine_same_test_file_case()




    cia.assert_all_test_file_exists()
    cia.statistic_data()

    tokenizers = [AstTokenizer()]
    ir_models = [
        # Bm25Model(),
        # TfIdfModel(),
        # RandomModel(),

        # LSIModel(num_topics=2),
        # LSIModel(num_topics=3),
        # LSIModel(num_topics=4),
        # LSIModel(num_topics=5),
        # LDAModel(num_topics=2),
        # LDAModel(num_topics=3),
        # LDAModel(num_topics=4),
        # LDAModel(num_topics=5),
        Bm25Model(),
    ]

    # tokenizer = AstTokenizer()
    # ir_model = TfIdfModel()

    for tokenizer in tokenizers:
        for ir_model in ir_models:

            do_exp(cia, tokenizer, ir_model)