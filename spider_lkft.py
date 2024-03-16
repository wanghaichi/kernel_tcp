from datetime import datetime
from pathlib import Path
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout
from liebes.analysis import CIAnalysis
import openpyxl
from liebes.ci_logger import logger
from liebes.GitHelper import GitHelper
from liebes.Glibc_CG import CallGraph as G_CG
from liebes.CallGraph import CallGraph as CG
import pickle
import pathlib

if __name__ == "__main__":

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

    for cg_file in pathlib.Path(ltp_cg_dir).glob('cg-*.txt'):
        TEST_CG = CG()
        TEST_CG.load_from_source(str(cg_file.resolve()))
        top_func_set = TEST_CG.get_top_func(cg_file.name[3: -4])
        ground_func_set = set()
        for top_func in top_func_set:
            ground_func_set = ground_func_set.union(TEST_CG.get_ground_func(top_func.function_name))
        # ground_func_set = TEST_CG.get_ground_func()
        used_syscall_set = set()
        for func in ground_func_set:
            used_syscall_set = used_syscall_set.union(GLIBC_CG.get_syscall(syscall_list, func.function_name))

        print(len(used_syscall_set))
        # for func in used_syscall_set:
        #     if syscall_table.get(func) is None:
        #         continue
        #     if KERNEL_CG.node_map.get(syscall_table[func]) is None:
        #         print(func)
        #     pass
    

    
    # coun = 0
    # for sys_call_func in syscall_table.values():
    #     if KERNEL_CG.node_map.get(sys_call_func) != None:
    #         coun += 1
    #     else:
    #         print(sys_call_func)
    
    # print(f'{coun} / {len(syscall_table)}')
        

