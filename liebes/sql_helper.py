import json
import pickle

from pathlib import Path
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from tqdm import tqdm

from liebes.CiObjects import DBCheckout, CIAnalysis, Checkout, load_cia
from liebes.GitHelper import GitHelper
from sqlalchemy import and_, or_
from sqlalchemy import text


if __name__ == "__main__":
    # not_mapped_text = Path("lkft/output.txt").read_text().split("\n")
    # for line in not_mapped_text:
    #     if

    exit(-1)
    # Create an engine and session
    engine = create_engine('sqlite:///hzy.db', echo=False)
    # conn = engine.connect()
    # res = conn.execute(text("SELECT DISTINCT(git_repository_url) from checkout"))
    #
    # print(res.all())
    # exit(-1)




    Session = sessionmaker(bind=engine)
    session = Session()


    # # # git_helper = GitHelper(repo_path="/home/wanghaichi/sound")
    checkouts = session.query(DBCheckout).filter(
        and_(
            DBCheckout.git_repository_url == 'https://git.kernel.org/pub/scm/linux/kernel/git/krzk/linux.git',
            # DBCheckout.origin == "kernelci"
        )).all()

    # cia = CIAnalysis()
    # for c in tqdm(checkouts):
    #     cia.ci_objs.append(Checkout(c))
    # # cia.select("defconfig")
    # cia.filter_job("FILTER_UNKNOWN_CASE")
    # cia.filter_branches_with_few_testcases(minimal_testcases=500)
    # for ciobj in cia.ci_objs:
    #     ciobj.filter_builds_with_less_tests()
    # cia.map_file_path()
    # cia.statistic_data()
    # pickle.dump(cia, Path("krzk-linux.pkl").open("wb"))
    # exit(-1)

    cia = load_cia("krzk-linux.pkl")
    not_mapped_set = set()
    for t in cia.get_all_testcases():
        if t.file_path is None:
            not_mapped_set.add(t.instance.path)
    print(not_mapped_set)
    exit(-1)

    # cia.map_file_path()
    # pickle.dump(cia, Path("linux-rc_cia.pkl").open("wb"))
    # exit(-1)
    # for t in tqdm(cia.get_all_testcases()):
    #     t.map_test()
    # cia.statistic_data()
    # pickle.dump(cia, Path("linux-rc_cia.pkl").open("wb"))
    # exit(-1)



    # cia = load_cia("linux_kernelci_cia.pkl")
    #
    # cia.select("defconfig")
    # cia.filter_branches_with_few_testcases(minimal_testcases=3000)
    # cia.map_file_path()
    # pickle.dump(cia, Path(f"linux_kernelci_cia.pkl").open("wb"))
    # cia.statistic_data()

    for ciobj in cia.ci_objs:
        # ciobj.filter_builds_with_less_tests()
        print(f"============={ciobj.instance.git_commit_hash}=============")
        m = {}
        for build in ciobj.builds:
            print(f"\t{build.instance.config_name}: {len(build.get_all_testcases())}")
            m[build.instance.config_name] = set()
            for t in build.get_all_testcases():
                m[build.instance.config_name].add(t.file_path)

        l = [(k, v) for k, v in m.items()]
        l = sorted(l, key=lambda x: len(x[1]), reverse=True)
        print(f"{l[0][0]}: {len(l[0][1])} tests")
        used_set = set(l[0][1])
        for i in range(1, len(l)):
            u = l[i]
            cnt0 = 0
            cnt1 = 0
            for test_path in u[1]:
                if test_path not in used_set:
                    cnt0 += 1
                else:
                    cnt1 += 1
            print(f"{u[0]} : {cnt0} unique files, total {len(u[1])} files")
            used_set = used_set.union(u[1])
        print(f"=============END==============")
    exit(-1)
    # cia.statistic_data()

    cia.ci_objs = [cia.ci_objs[-3]]
    path_map = {}
    for t in cia.get_all_testcases():
        if t.file_path not in path_map:
            path_map[t.file_path] = set()
        path_map[t.file_path].add(t)
    for k, v in path_map.items():
        if len(v) > 1:
            tc = 0
            fc = 0
            for i in v:
                if i.is_pass():
                    tc += 1
                else:
                    fc += 1
            if True:
            # if tc > 0 and fc > 0:
                print(f"========={k} : {len(v)}, true: {tc}, false: {fc}========")
                for i in v:
                    print(f"\t{i.instance.path}: {i.is_pass()}")
                print(f"=========END========")

    # for ch in checkouts:
    #     print(len(ch.builds))

    # print("done")
    # print(len(records))
    # for r in records:
    #     print(r)
    # exit(-1)
    # for r in records:
    #     print(r)
    #     print(r.checkout)
    # session.close()
    # exit(-1)

    # Get the column names of the table
    # checkouts = session.query(Test).all()
    # cnt = 0
    # m = {}
    # # Print the column names
    # print(len(checkouts))
    # for c in tqdm(checkouts):
    #     if c.id not in m.keys():
    #         m[c.id] = []
    #     m[c.id].append(c)
    # cnt = 0
    # for k, v in m.items():
    #     if len(v) > 1:
    #         for i in v[1:]:
    #             session.delete(i)
    #             cnt += 1
    # session.commit()
    # print(f"delete {cnt} rows")
    # # Close the session
    # session.close()
