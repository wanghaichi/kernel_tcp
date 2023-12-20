import datetime
import json
import time

import requests
import pickle
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from pathlib import Path
from tqdm import tqdm
from liebes.CiObjects import DBCheckout, CIAnalysis, Checkout, load_cia, DBBuild, DBTest, TestCaseType
from liebes.test_path_mapping import mapping_config, has_mapping
import Levenshtein


def calculate_most_similar_string(s, s_set):
    min_distance = float('inf')
    most_similar_string = None

    for string in s_set:
        temp = Path(string).name
        distance = Levenshtein.distance(s, temp)
        if distance < min_distance:
            min_distance = distance
            most_similar_string = string

    return most_similar_string


def create_db_checkout_instance(data_source: dict):
    dc = DBCheckout()
    dc.id = data_source["id"]
    dc.origin = "lkft"
    dc.tree_name = "mainline"
    dc.git_repository_url = data_source["metadata"]["git_repo"]
    dc.git_commit_hash = data_source["metadata"]["git_sha"]
    dc.git_repository_branch = "master"
    dc.patchset_files = None
    dc.patchset_hash = None
    dc.comment = data_source["metadata"]["git_describe"]
    dc.start_time = data_source["created_at"]
    dc.contacts = None
    dc.valid = None
    dc.misc = ""
    return dc


def create_db_build_instance(data_source: dict):
    db = DBBuild()
    db.checkout_id = data_source["id"]
    db.id = data_source["id"]
    db.origin = "lkft"
    db.comment = ""
    db.start_time = None
    db.duration = None
    db.architecture = "x86_64"
    db.command = None
    db.compiler = None
    db.input_files = None
    db.output_files = None
    db.config_name = "defconfig"
    db.config_url = None
    db.log_url = None
    db.valid = None
    db.misc = None
    return db


def create_db_test_instance(data_source: dict, bid):
    dt = DBTest()
    dt.id = data_source["id"]
    dt.build_id = bid
    dt.origin = "lkft"
    dt.path = data_source["name"]
    dt.status = data_source["status"]
    dt.waived = None
    dt.start_time = None
    dt.output_files = None
    dt.has_known_issues = data_source["has_known_issues"]
    dt.known_issues = str(data_source["known_issues"])
    return dt


if __name__ == "__main__":
    # for k, v in mapping_config.items():
    #     for kk, vv in v.items():
    #         if not Path(vv).exists():
    #             print(kk, vv)
    # exit(-1)

    #
    # path_set = pickle.load(open("path_set.pkl", "rb"))
    # l = []
    # for ps in path_set:
    #     a = ps.split("/")
    #     if a[0] in ["log-parser-boot", "boot", "kselftest-android"]:
    #         continue
    #     if has_mapping(ps) is not None:
    #         continue
    #     l.append(ps)
    #     # print(ps)
    # l = sorted(l)
    #
    # root_path = Path("test_cases/kvm-unit-tests")
    # # obtain all paths from root_path that ends with .c or .sh
    #
    # paths = [str(x) for x in root_path.rglob("*.c")]
    # paths.extend([str(x) for x in root_path.rglob("*.sh")])
    #
    # # paths = [str(Path(x).name) for x in paths]
    # for i in l:
    #     if "ltp" in i:
    #         continue
    #     if "shardfile" in i:
    #         continue
    #     if "kvm-unit-tests" in i:
    #         continue
    #     most_s = calculate_most_similar_string(i.split("/")[1], paths)
    #     print(f"{i}: {most_s}")
    #
    # # for a in l:
    # #     print(a)
    # exit(-1)
    
    #
    # passed_set = {"log-parser-boot", "mptcp_connect_sh"}
    # for ps in path_set:
    #     f = False
    #     for i in passed_set:
    #         if i in ps:
    #             f = True
    #             break
    #     if f:
    #         continue
    #     if ps in mapping_config.keys():
    #         continue
    #     print(ps)
    # exit(-1)

    #
    # engine = create_engine('sqlite:///lkft.db', echo=False)
    # Session = sessionmaker(bind=engine)
    # session = Session()

    # # # git_helper = GitHelper(repo_path="/home/wanghaichi/sound")
    # checkouts = session.query(DBCheckout).all()
    # has been filtered: FILTER_UNKNOWN_CASE, FILTER_NOFILE_CASE, FILTER_CASE_BY_TYPE
    cia = load_cia("cia-fil-1.pkl")
    for t in cia.get_all_testcases():
        t.file_path = t.file_path.replace("/Users/liebes/project/python/", "")
    for t in cia.get_all_testcases()[:5]:
        print(t.file_path)
    exit(-1)

    cia.number_of_threads = 20
    cia.filter_job("FILTER_ALLFAIL_CASE")

    # cia.map_file_path()
    # cia.filter_job("FILTER_UNKNOWN_CASE")
    # cia.filter_job("FILTER_NOFILE_CASE")
    # cia.filter_job("FILTER_CASE_BY_TYPE", case_type=[TestCaseType.C,])
    # pickle.dump(cia, open("cia-fil-0.pkl", "wb"))
    # # exit(-1)
    # cia.filter_job("COMBINE_SAME_CASE")
    cia.statistic_data()
    pickle.dump(cia, open("cia-fil-1.pkl", "wb"))
    exit(-1)

    # test_path = Path("lkft/tests")
    # for t in test_path.iterdir():
    #     test_instance = pickle.load(open(t, "rb"))
    #     print(t.name)
    #     print(len(test_instance))
    #     print(test_instance[0].keys())
    #     print(test_instance[0]["environment"])
    #     exit(-1)
    # print(test_instance[20]["name"])

    # for build in builds[:50]:
    # api_url = "https://qa-reports.linaro.org/api/projects/?format=json&limit=1500"
    # response = requests.get(api_url)
    #
    # if response.status_code == 200:
    #     # Get the JSON data from the response
    #     data = response.json()
    #     pickle.dump(data["results"], open("projects.pkl", "wb"))
    #
    # else:
    #     print('Error:', response.status_code)
