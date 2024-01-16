from pathlib import Path
from liebes.sql_helper import SQLHelper
from liebes.CiObjects import DBCheckout, DBBuild, DBTestRun, DBTest, Checkout
from liebes.analysis import CIAnalysis
import openpyxl

if __name__ == "__main__":
    sql = SQLHelper("/home/wanghaichi/kernelTCP/lkft/lkft.db")
    checkouts = sql.session.query(DBCheckout).order_by(DBCheckout.git_commit_datetime.desc()).limit(10).all()
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

    # # ch = Checkout(first_checkout
    cia.set_parallel_number(10)
    # # cia.select()
    # cia.filter_job("FILTER_UNKNOWN_CASE")
    # cia.filter_job("FILTER_NOFILE_CASE")
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_ALLFAIL_CASE")
    # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # # cia.filter_job("")

    workbook = openpyxl.Workbook()
    sheet = workbook.active
    sheet.column_dimensions['A'].width = 50
    sheet.column_dimensions['B'].width = 40
    data = [['', 'build_id', 'build_name', 'total_case', 'fail_case', 'c_case', 'sh_case', 'py_case']]
    for ch in cia.ci_objs:
        print('=========================================== ' + ch.instance.git_sha + ' ===========================================')
        data.append([ch.instance.git_sha])
        for build in ch.builds:
            fail_case_sum, c_case_sum, sh_case_sum, py_case_sum = 0, 0, 0, 0
            for t in build.get_all_testcases():
                # print(t)
                if t.status == 1:
                    # fail_case_sum += 1
                    # if t.file_path.endswith(r'.c'):
                    #     c_case_sum += 1
                    # elif t.file_path.endswith(r'.sh'):
                    #     sh_case_sum += 1
                    # elif t.file_path.endswith(r'.py'):
                    #     py_case_sum += 1
            

                    print(t.instance.id + '      ' + t.instance.file_path)
            # case_sum = len(build.get_all_testcases())
            # fail_pro = f'{fail_case_sum}/{case_sum}'
            # tmp = ['', build.instance.id, build.instance.build_name, case_sum, fail_case_sum, c_case_sum, sh_case_sum, py_case_sum]
            # data.append(tmp)
            # print('Fail Case: {}          C File: {}          SH File: {}          PY File: {}'.format(fail_pro, c_case_sum, sh_case_sum, py_case_sum).ljust(10))
    
    # for row in data:
    #     sheet.append(row)
    # workbook.save("fail_case_statistics.xlsx")


