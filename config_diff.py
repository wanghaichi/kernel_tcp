import math
import random
import pathlib
from liebes.CiObjects import *
import numpy as np
from liebes.analysis import CIAnalysis
from liebes.EHelper import EHelper
from liebes.sql_helper import SQLHelper
from liebes.ci_logger import logger
from liebes.tcp_approach import adaptive_random_prior
import json

config_suit_map = {'gcc-13-lkftconfig': 'ltp', 'gcc-13-lkftconfig-kselftest': 'kselftest', 'gcc-13-lkftconfig-compat': 'ltp', \
                   'gcc-13-lkftconfig-debug-kmemleak': 'ltp', 'gcc-13-lkftconfig-no-kselftest-frag': 'kselftest'}

file_map = {}

def get_set_diff(set1: set, set2: set):
    increment = set1 - set2
    decrement = set2 - set1
    
    diff = '+++   ' + str(increment) + '\n'
    diff = diff + '---   ' + str(decrement)

    return diff

def get_file_path(cia: CIAnalysis):
    for ci_obj in cia.ci_objs:
            for build in ci_obj.builds:
                for testrun in build.testruns:
                    temp = []
                    for test_case in testrun.tests:
                        if test_case.map_test() and Path(test_case.file_path).exists() and test_case.file_path != '':
                            temp.append(test_case)
                    testrun.tests = temp



if __name__ == '__main__':
    with open(r'liebes/mapping_config.json', r'r') as f:
        file_map = json.load(f)
    f.close()

    sql = SQLHelper()
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(100).all()
    cia = CIAnalysis()
    for ch in checkouts:
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_NOFILE_CASE")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.ci_objs = cia.ci_objs[1:]
    cia.statistic_data()

    for ci_obj in cia.ci_objs:
        logger.info(f'========== {ci_obj.instance.git_sha} ==========')
        classified_builds = {}
        for build in ci_obj.builds:
            # if len(build.get_all_testcases()) == 0:
            #     continue
            kconfig_text = build.instance.kconfig[1: -1]
            if ', ' in kconfig_text:
                kconfig_list = kconfig_text.split(', ')
            else:
                kconfig_list = kconfig_text.split(' ')
            kconfig = set()
            for k in kconfig_list:
                k = k.replace('\'', '')
                if str(k).startswith('https://'):
                    k = k.split('/')[-1]
                kconfig.add(k)
            build_node = (build.instance.build_name, kconfig, len(build.get_all_testcases()))
            config_key = frozenset(kconfig)
            base_config = kconfig
            if config_key in classified_builds:
                classified_builds[config_key].append(build_node)
            else:
                classified_builds[config_key] = [build_node]
        
        base_config = set()
        base_size = 0
        for category_key in classified_builds:
            category_value = classified_builds[config_key]
            if len(category_value) > base_size:
                base_size = len(category_value)
                base_config = category_value[0][1]
        
        # if ci_obj.instance.git_sha == 'b712075e03cf95d9009c99230775dc41195bde8a':
        #     pass
        logger.info('======== base config ========')
        logger.info(base_config)
        group_idx = 1
        for k in classified_builds:
            v = classified_builds[k]
            config = v[0][1]
            config_diff = ''
            if config != base_config:
                config_diff = get_set_diff(config, base_config)
            
            total_test = 0
            max_test = 0
            build_names = []
            for b_node in v:
                if b_node[2] > max_test:
                    max_test = b_node[2]
                total_test += b_node[2]
                build_names.append(b_node[0])
            
            logger.info('======== Group' + str(group_idx) + ' ========')
            logger.info(build_names)
            logger.info(config_diff)
            # print(str(max_test) + '  :  ' + str(total_test))
            group_idx += 1
            

            


