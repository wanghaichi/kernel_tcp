from datetime import datetime
from pathlib import Path
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout
from liebes.analysis import CIAnalysis
from multiprocessing import Pool
from liebes.GitHelper import GitHelper


if __name__ == "__main__":
    def load_parallel(instance):
        return Checkout(instance)




