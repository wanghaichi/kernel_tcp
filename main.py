from pathlib import Path
from git import Repo
import json
from typing import List
import pickle
from liebes.CiObjects import *
from liebes.GitHelper import GitHelper
import os
import Levenshtein


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


if __name__ == '__main__':
    # data_path = Path("dataset/data0.json")
    # ci_obj = CIObj.load_from_json("dataset/data0.json")
    # ci_obj.print_with_intent()
    # cia = CIAnalysis()
    # for i in range(20):
    #     ci_obj = CIObj.load_from_json(f"dataset/data{i}.json")
    #     cia.ci_objs.append(ci_obj)
    # pickle.dump(cia, Path("cia.pkl").open("wb"))

    linux_path = '/home/wanghaichi/linux'
    gitHelper = GitHelper(linux_path)

    cia = load_cia("cia.pkl")

    # for i in range(len(cia.ci_objs) - 1):
    #     gitHelper.diff(cia.ci_objs[i].commit_hash, cia.ci_objs[i+1].commit_hash)

    cia = cia.select("arm64/defconfig+arm64-chromebook")
    cia.filter_unknown_test_cases()
    cia.filter_always_failed_test_cases()
    cia.filter_no_file_test_cases()
    cia.statistic_data()

    # print(f"{cnt} / {len(test_cases)}")
