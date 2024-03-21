import json
from datetime import datetime

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *
import numpy as np
from liebes.llvm_process import LLVMHelper

if __name__ == '__main__':
    llvm_helper = LLVMHelper(root_path=r'/home/duyiheng/projects/ltp_projects/ltp_20240129/ltp-20240129')
    llvm_helper.generate_bitcode()

