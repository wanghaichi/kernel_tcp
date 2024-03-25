from datetime import datetime
from pathlib import Path
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout, Test
from liebes.analysis import CIAnalysis
import openpyxl
from liebes.ci_logger import logger
from liebes.GitHelper import GitHelper
from liebes.Glibc_CG import CallGraph as G_CG
from liebes.CallGraph import CallGraph as CG
from liebes.EHelper import EHelper
import pickle
import pathlib
import os
import traceback
import numpy as np


ltp_cg_dir = r'/home/duyiheng/projects/ltp_cg/'

GLIBC_CG = G_CG(r'everything_graph.new')
KERNEL_CG = CG()
KERNEL_CG.load_from_source(r'output-cg.txt')
with open(r'syscall_list', r'rb') as f:
    syscall_list = pickle.load(f)
f.close()

with open(r'syscall_64.tbl') as f:
    syscall_64_tbl = f.read()
f.close()

syscall_table = {}

for line in syscall_64_tbl.split('\n'):
    if line.split('\t')[1] == 'x32':
        continue
    glibc_func = line.split('\t')[2]
    sys_call = line.split('\t')[-1]
    sys_call_func = '__do_' + sys_call
    syscall_table[glibc_func] = sys_call_func


def get_userd_syscall(test_case: Test):
    file_path = str(test_case.file_path)
    test_name = file_path[file_path.rfind(r'/') + 1: -2]
    TEST_CG = CG()
    if not os.path.exists(os.path.join(ltp_cg_dir, r'cg-' + test_name + r'.txt')):
        return set()
    TEST_CG.load_from_source(os.path.join(ltp_cg_dir, r'cg-' + test_name + r'.txt'))
    top_func_set = TEST_CG.get_top_func(test_name)
    ground_func_set = set()
    for top_func in top_func_set:
        ground_func_set = ground_func_set.union(TEST_CG.get_ground_func(top_func.function_name))
    # ground_func_set = TEST_CG.get_ground_func()
    used_syscall_set = set()
    for func in ground_func_set:
        used_syscall_set = used_syscall_set.union(GLIBC_CG.get_syscall(syscall_list, func.function_name))
    
    return used_syscall_set


def get_related_methods(test_case: Test):
    used_syscall_set = get_userd_syscall(test_case)
    related_method_set = set()
    for syscall in used_syscall_set:
        related_method_set = related_method_set.union(KERNEL_CG.get_all_call(syscall_table.get(syscall)))

    TA_tmp[test_case.file_path] = related_method_set
    return related_method_set

TA_tmp = {}

def total_stragety(test_cases: list[Test]):
    test_TA_map = {}
    for idx in range(len(test_cases)):
        test_case = test_cases[idx]
        if not test_case.file_path.endswith(r'.c'):
            test_TA_map[idx] = 0
            continue
        if TA_tmp.get(test_case.file_path) is None:
            related_methods_set = get_related_methods(test_case)
            test_TA_map[idx] = len(related_methods_set)
        else:
            test_TA_map[idx] = len(TA_tmp[test_case.file_path])
    
    sorted_map = dict(sorted(test_TA_map.items(), key=lambda x: x[1], reverse=True))
    sorted_list = list(sorted_map.keys())
    return sorted_list

def additional_stragety(test_cases: list[Test]):
    test_idx_map = {}
    for idx in range(len(test_cases)):
        test_case = test_cases[idx]
        test_idx_map[test_case.file_path] = idx
    slide_set = set()
    size = len(test_cases)
    sorted_list = []
    while size > 0:
        max_TA = -1
        max_TA_test = None
        max_related_method_set = set()
        for test_case in test_cases:
            related_methods_set = TA_tmp.get(test_case.file_path)
            if related_methods_set is None:
                related_methods_set = get_related_methods(test_case)
            additional_method_set = related_methods_set - slide_set
            if len(additional_method_set) > max_TA:
                max_TA = len(related_methods_set)
                max_TA_test = test_case
                max_related_method_set = related_methods_set
        
        if max_TA == 0:
            slide_set = set()
        else:
            slide_set = slide_set.union(max_related_method_set)
        sorted_list.append(test_idx_map[max_TA_test.file_path])
        test_cases.remove(max_TA_test)
        size -= 1
        
    return sorted_list


def do_exp(cia: CIAnalysis, stragety: str):
    ehelper = EHelper()
    apfd_res = []
    for ci_index in range(1, len(cia.ci_objs)):
        ci_obj = cia.ci_objs[ci_index]
        test_cases = ci_obj.get_all_testcases()
        faults_arr = []
        for i in range(len(test_cases)):
            if test_cases[i].is_failed():
                faults_arr.append(i)
        if len(faults_arr) == 0:
            continue

        try:
            if stragety == 'total':
                prioritized_list = total_stragety(test_cases)
            elif stragety == 'additional':
                prioritized_list = additional_stragety(test_cases)
            else:
                return 'Error Stragety!!!'
            apfd_v = ehelper.APFD(faults_arr, prioritized_list)
            logger.debug(f"stragety: {stragety}, commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}")
            apfd_res.append(apfd_v)
        except:
            traceback.print_exc()
    logger.info(f"stragety: {stragety}, avg apfd: {np.average(apfd_res)}")
    return f"stragety: {stragety}, avg apfd: {np.average(apfd_res)}"