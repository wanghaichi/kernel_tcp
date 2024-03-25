import json
from datetime import datetime

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.ir_model import *
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *
from git import Repo
import tree_sitter
from tree_sitter import Language, Parser
import difflib
import subprocess
import numpy as np
import requests
import re
from datetime import datetime
import pymysql

class TestCaseInfo:
    def __init__(self):
        self.file_path = ""
        self.type = ""


def update_token_mapping(m, mapping_path):
    json.dump(m, Path(mapping_path).open("w"))


if __name__ == '__main__':
    connection = pymysql.connect(
    host = 'localhost',
    user = 'root',
    password = 'linux@133',
    database = 'lkft',
    port = 3306
    )

    cursor = connection.cursor()

    sql = r'select * from checkout'
    cursor.execute(sql)

    results = cursor.fetchall()

    with open(r'checkout_ltp_version_map.json', r'r') as f:
        tmp = json.load(f)
    f.close()

    print(len(tmp))

    # checkout_ltp_map = {}
    # version_date = datetime(2024, 1, 31)

    # for ci_obj in results:
    #     ltp_version = None
    #     if tmp.get(ci_obj[6]) is not None:
    #         continue

    #     commit_time = ci_obj[13]
    #     if commit_time >= version_date:
    #         ltp_version = '20240129'
    #     else:
    #         ltp_version = '20230929'

    #     tmp[ci_obj[6]] = ltp_version
        
        

    # with open(r'checkout_ltp_version_map.json', r'w') as f:
    #     json.dump(tmp, f)
    # f.close()

