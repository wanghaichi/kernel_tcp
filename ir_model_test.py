from rank_bm25 import BM25Okapi
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
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout
from liebes.analysis import CIAnalysis


def get_similarity(corpus, queries):
    corpus = [doc.split(' ') for doc in corpus]
    bm25 = BM25Okapi(corpus)
    bm25.k1 = 2
    bm25.b = 0.75
    tokenized_query = [doc.split(' ') for doc in queries]
    tmp = []
    for q in tokenized_query:
        tmp.append(bm25.get_scores(q))
    result = [sum(nums) for nums in zip(*tmp)]
    return result


linux_path = '/home/wanghaichi/linux-1'
sql = SQLHelper("/home/wanghaichi/kernelTCP/lkft/lkft.db")
checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(20).all()
cia = CIAnalysis()
for ch in checkouts:
    cia.ci_objs.append(Checkout(ch))
m = {}
for ch in cia.ci_objs:
    for build in ch.builds:
        unique_test = set([x.file_path for x in build.get_all_testcases()])
        # print(unique_test)
        if len(unique_test) > 1000:
            if build.label not in m.keys():
                m[build.label] = 0
            m[build.label] += 1
# print k , v in m, in order by v
for k, v in sorted(m.items(), key=lambda item: item[1]):
    print(k, v)

cia.set_parallel_number(10)
# # cia.select()
# cia.filter_job("FILTER_UNKNOWN_CASE")
cia.filter_job("FILTER_NOFILE_CASE")
cia.filter_job("COMBINE_SAME_CASE")
cia.filter_job("FILTER_ALLFAIL_CASE")
cia.filter_job("FILTER_NO_C_CASE")
# cia.filter_job("FILTER_NO_SH_CASE")

tokenizer = AstTokenizer()
ir_model = Bm25Model()

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
        print(1)
        continue
    last_ci_obj = cia.ci_objs[ci_index - 1]
    # start iteration of one test result
    # 1. first extract the faults result
    test_cases = ci_obj.get_all_testcases()
    if len(test_cases) == 0:
        continue
    
    # 2. get code changes
    code_changes = []
    txt = ''
    with open(r'test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind29.sh', r'r') as f:
        for line in f:
            line = line.strip()
            if(len(line) == 0):
                continue
            txt = txt + line + ' '
    code_changes.append(txt)
    # 3. second obtain the sort result
    token_arr = []
    to_remove = []
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
                to_remove.append(i)
                continue

            v = " ".join(tokens)
            v = v.lower()
            token_arr.append(v)
            m[str(t.file_path)] = v
            json.dump(m, Path(mapping_path).open("w"))
    for idx in to_remove:
        del test_cases[idx]

    queries = []
    for cc in code_changes:
        tokens = tokenizer.get_tokens(cc, TestCaseType.C)
        queries.append(" ".join(tokens))
    # print(f"corpus: {len(token_arr)}, queries: {len(queries)}")
    get_similarity(token_arr, queries)
    s = ir_model.get_similarity(token_arr, queries)

    # print(s.shape)
    similarity_sum = np.sum(s, axis=1)
    # print(similarity_sum)
    # print(len(similarity_sum))

    order_arr = np.argsort(similarity_sum)[::-1]



