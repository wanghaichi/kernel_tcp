import os
from pathlib import Path

from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis
from liebes.reproduce import ReproUtil
from liebes.sql_helper import SQLHelper
import multiprocessing

if __name__ == '__main__':




    root = Path("/home/wanghaichi/repro_linuxs")

    reproutil = ReproUtil(
        home_dir="/home/wanghaichi",
        fs_image_root="file_images",
        port=1234,
        linux_dir="linux",
        ltp_dir="ltp",
        pid_index=-1,
    )


    def remove_gcda(root):
        files = Path(root).glob('**/*.gcda')

        # Delete each file
        for file in files:
            os.remove(file)

    def run(subversions):
        for subversion in subversions:
            print(subversion.absolute())
            cmd = "mkdir cov_all"
            reproutil.run_command(cmd, cwd=subversion.absolute())
            cmd = "cp *.tar.gz cov_all/"
            reproutil.run_command(cmd, cwd=subversion.absolute())
            for f in subversion.iterdir():
                if f.suffix == ".gz" or f.suffix == ".tar.gz":
                    # remove all *.gcda first
                    remove_gcda(subversion.absolute())
                    cmd = f"tar -xvf {f.name}"
                    reproutil.run_command(cmd, cwd=subversion.absolute())
                    tc_name = f.name.removesuffix('.tar.gz')
                    cmd = f" lcov -c -d ./ -t {tc_name} -o {tc_name}.info"
                    reproutil.run_command(cmd, cwd=subversion.absolute())
                    print(f"collect coverage for {tc_name} done, result is {tc_name}.info")

    to_list = []
    for subversion in root.iterdir():
        to_list.append(subversion)

    number_of_process = 10
    batch = len(to_list) // number_of_process
    processes = []

    for i in range(number_of_process):
        start = i * batch
        end = (i + 1) * batch
        if i == number_of_process - 1:
            end = len(to_list)
        p = multiprocessing.Process(target=run, args=(to_list[start: end],))
        processes.append(p)

    for p in processes:
        p.start()

    for p in processes:
        p.join()


    exit(-1)
    #
    # # Establish a database connection
    # connection = mysql.connector.connect(
    #     host="172.19.135.133",
    #     user="root",
    #     password="linux@133",
    #     database="lkft"
    # )
    #
    # # Create a cursor object
    # cursor = connection.cursor()
    # for i in range(10):
    #     query = f"INSERT INTO test_{i} SELECT t.* FROM test AS t JOIN testrun AS tr ON t.testrun_id = tr.id JOIN build AS b ON tr.build_id = b.id JOIN checkout AS c ON b.checkout_id = c.id WHERE c.id % 10 = {i}"
    #     cursor.execute(query)
    #     connection.commit()
    #     print(i)
    #
    # cursor.close()
    # connection.close()
    # pass
