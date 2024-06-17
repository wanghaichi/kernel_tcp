import argparse
import multiprocessing
import pickle
from pathlib import Path

from liebes.CiObjects import DBCheckout, Checkout, Test, TestCaseType
from liebes.EHelper import EHelper
from liebes.analysis import CIAnalysis
from liebes.coverage_ana import CoverageHelper
from liebes.ltp_result import TCResult
from liebes.sql_helper import SQLHelper
from liebes.ci_logger import logger
import numpy as np
if __name__ == "__main__":
    # e_helper = EHelper()
    # v = 'ad2fd53a7870a395b8564697bef6c329d017c6c9'
    # cov_helper = CoverageHelper(v)
    # cov_helper.load_coverage4checkout()
    # cia = pickle.load(open(f"cia_cov_only_{v}.pkl", "rb"))
    # A = []
    # B = []
    # for fc in cia.get_all_testcases():
    #     k = cov_helper.get_coverage_name(fc.get_testcase_name())
    #     if k not in cov_helper.coverage_info.keys():
    #         continue
    #     cov_item = cov_helper.coverage_info[k]
    #     if fc.type != TestCaseType.C:
    #         continue
    #     if fc.get_suite_name() == "ltp":
    #         f = Path("/home/wanghaichi/repro_ltps") / e_helper.get_ltp_version(v) / fc.file_path.replace("test_cases/ltp/", "")
    #     else:
    #         f = Path("/home/wanghaichi/repro_linuxs") / v / fc.file_path.replace("test_cases/selftests/", "tools/testing/selftests/")
    #     if not f.exists():
    #         print(f)
    #         continue
    #     try:
    #         program_size = len(f.read_text())
    #     except Exception as e:
    #         print(f)
    #         continue
    #     A.append(program_size)
    #     cnt = 0
    #     for f, lines in cov_item.items():
    #         cnt += len(lines)
    #     B.append(cnt)
    # correlation_coefficient = np.corrcoef(A, B)[0, 1]
    # print(correlation_coefficient)
    # exit(-1)


    # ehelper = EHelper()
    # versions = ['91ec4b0d11fe115581ce2835300558802ce55e6c','1ae78a14516b9372e4c90a89ac21b259339a3a3a','58390c8ce1bddb6c623f62e7ed36383e7fa5c02f','671e148d079f4d4eca0a98f7dadf1fe69d856374','d295b66a7b66ed504a827b58876ad9ea48c0f4a8','533c54547153d46c0bf99ac0e396bed71f760c03','e338142b39cf40155054f95daa28d210d2ee1b2d','8d15d5e1851b1bbb9cd3289b84c7f32399e06ac5','1639fae5132bc8a904af28d97cea0bedb3af802e','2214170caabbff673935eb046a7edf4621213931','3a8a670eeeaa40d87bd38a587438952741980c18','6cdbb0907a3c562723455e351c940037bdec9b7a','a901a3568fd26ca9c4a82d8bc5ed5b3ed844d451','03275585cabd0240944f19f33d7584a1b099a3a8','3290badd1bb8c9ea91db5c0b2e1a635178119856','7fcd473a6455450428795d20db7afd2691c92336','06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5','fdf0eaf11452d72945af31804e2a1048ee1b574c','18b44bc5a67275641fb26f2c54ba7eef80ac5950','ffabf7c731765da3dbfaffa4ed58b51ae9c2e650','251a94f1f66e909d75a774ac474a63bd9bc38382','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','25aa0bebba72b318e71fe205bfd1236550cc9534','ae545c3283dc673f7e748065efa46ba95f678ef2','4c75bf7e4a0e5472bd8f0bf0a4a418ac717a9b70','b320441c04c9bea76cbee1196ae55c20288fd7a6','28f20a19294da7df158dfca259d0e2b5866baaf9','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','1c59d383390f970b891b503b7f79b63a02db2ec5','b96a3e9142fdf346b05b20e867b4f0dfca119e96','53ea7f624fb91074c2f9458832ed74975ee5d64c','ef2a0b7cdbc5b84f7b3f6573b7687e72bede0964','4debf77169ee459c46ec70e13dc503bc25efd7d2','e0152e7481c6c63764d6ea8ee41af5cf9dfac5e9','92901222f83d988617aee37680cb29e1a743b5e4','3f86ed6ec0b390c033eae7f9c487a3fea268e027','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','744a759492b5c57ff24a6e8aabe47b17ad8ee964','dd1386dd3c4f4bc55456c88180f9f39697bb95c0','2a5a4326e58339a26cd1510259e7310b8c0980ff','535a265d7f0dd50d8c3a4f8b4f3a452d56bd160f','aed8aee11130a954356200afa3f1b8753e8a9482','ad8a69f361b9b9a0272ed66f04e6060b736d2788','8018e02a87031a5e8afcbd9d35133edd520076bb','830380e3178a103d4401689021eadddadbb93d6d','84186fcb834ecc55604efaf383e17e6b5e9baa50','750b95887e567848ac2c851dae47922cac6db946','be3ca57cfb777ad820c6659d52e60bbdd36bf5ff','90450a06162e6c71ab813ea22a83196fe7cff4bc']
    # for v in versions:
    #     print(v, ehelper.get_ltp_version(v))
    # exit(-1)



    # versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1','33afd4b76393627477e878b3b195d606e585d816','825a0714d2b3883d4f8ff64f6933fb73ee3f1834','1a5304fecee523060f26e2778d9d8e33c0562df3','ad2fd53a7870a395b8564697bef6c329d017c6c9','838a854820eea0d21c6910cc3ab23b78d16aa1dd','7877cb91f1081754a1487c144d85dc0d2e2e7fc4','a4d7d701121981e3c3fe69ade376fe9f26324161','4973ca29552864a7a047ab8a15611a585827412f','e660abd551f1172e428b4e4003de887176a8a1fd','6a8cbd9253abc1bd0df4d60c4c24fa555190376d','b30d7a77c53ec04a6d94683d7680ec406b7f3ac8','995b406c7e972fab181a4bb57f3b95e59b8e5bf3','538140ca602b1c5f3870bef051c93b491045f70a','5133c9e51de41bfa902153888e11add3342ede18','8fc3b8f082cc2f5faa6eae315b938bc5e79c332e','c192ac7357683f78c2e6d6e75adfcc29deb8c4ae','5b8d6e8539498e8b2fa67fbcce3fe87834d44a7a','9f9116406120638b4d8db3831ffbc430dd2e1e95','122e7943b252fcf48b4d085dec084e24fc8bec45','024ff300db33968c133435a146d51ac22db27374','13b9372068660fe4f7023f43081067376582ef3c','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','c8afaa1b0f8bc93d013ab2ea6b9649958af3f1d3','a785fd28d31f76d50004712b6e0b409d5a8239d8','9e6c269de404bef2fb50b9407e988083a0805e3b','7d2f353b2682dcfe5f9bc71e5b61d5b61770d98e','97efd28334e271a7e1112ac4dca24d3feea8404b','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','651a00bc56403161351090a9d7ddbd7095975324','1687d8aca5488674686eb46bf49d1d908b2672a1','4fb0dacb78c6a041bbd38ddd998df806af5c2c69','cd99b9eb4b702563c5ac7d26b632a628f5a832a5','87dfd85c38923acd9517e8df4afc908565df0961','b89b029377c8c441649c7a6be908386e74ea9420','2be6bc48df59c99d35aab16a51d4a814e9bb8c35','7733171926cc336ddf0c8f847eefaff569dbff86','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','7ba2090ca64ea1aa435744884124387db1fac70f','6099776f9f268e61fe5ecd721f994a8cfce5306f','a3c57ab79a06e333a869ae340420cb3c6f5921d3','23f108dc9ed26100b1489f6a9e99088d4064f56b','57d88e8a5974644039fbc47806bac7bb12025636','2cf0f715623872823a72e451243bbf555d10d032','95289e49f0a05f729a9ff86243c9aff4f34d4041','e017769f4ce20dc0d3fa3220d4d359dcc4431274','3a568e3a961ba330091cd031647e4c303fa0badb','2af9b20dbb39f6ebf9b9b6c090271594627d818e','305230142ae0637213bf6e04f6d9f10bbcb74af8']
    # sql_helper = SQLHelper()
    # checkouts = sql_helper.session.query(DBCheckout).filter(DBCheckout.git_sha.in_(versions)).all()
    # d = checkouts[0].git_commit_datetime - checkouts[1].git_commit_datetime
    # print(d.total_seconds())
    # print(d.total_seconds() / 3600)
    #
    # exit(-1)

    # cia = CIAnalysis()
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # # for ch in checkouts:
    # #     checkout = Checkout(ch)
    # #     cia = CIAnalysis()
    # #     cia.ci_objs.append(checkout)
    # cia.reorder()
    # cia.set_parallel_number(40)
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.reorder()
    # m = {}
    # cnt = {}
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #     for j in range(i):
    #         previous_ci_obj = cia.ci_objs[j]
    #         diff = ci_obj.instance.git_commit_datetime - previous_ci_obj.instance.git_commit_datetime
    #         k = i - j
    #         if k not in m.keys():
    #             m[k] = 0
    #             cnt[k] = 0
    #         m[k] += diff.total_seconds()
    #         cnt[k] += 1
    #
    # for k, v in m.items():
    #     print(k, v / cnt[k] / 3600 / 24, "days")
    # exit(-1)


    # root = Path("/home/wanghaichi/repro_linuxs")
    # cnt = 0
    # for tc in checkout.get_all_testcases():
    #     if tc.get_testcase_name() in ["filecapstest", "breakpoints:step_after_suspend_test"]:
    #         continue
    #     if not (root / ch.git_sha / (tc.get_testcase_name() + "_coverage.info")).exists():
    #         cnt += 1
    #         # print(tc.get_testcase_name())
    # if cnt > 0:
    #     print(ch.git_sha, cnt)
    # print(cnt)
    # exit(-1)




    # cov_info = CoverageHelper('35fab9271b7e6d193b47005c4d07369714db4fd1')
    # cov_info.load_coverage4checkout()
    # for f, _ in cov_info.search_based_generator():
    #     print(f)
    # exit(-1)

    parser = argparse.ArgumentParser()

    parser.add_argument("--metric", type=str, default='total')
    parser.add_argument("--process", type=int)
    args = parser.parse_args()
    logger.info(args)

    # cia = pickle.load(open("cia-04-24.pkl", "rb"))


    e_helper = EHelper()
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #     # print(ci_obj.instance.git_sha)
    #     failed_cases = [x.get_testcase_name() for x in ci_obj.get_all_testcases() if x.is_failed()]
    #     if len(failed_cases) == 0:
    #         continue
    #     new_cia = CIAnalysis()
    #     new_cia.ci_objs.append(ci_obj)
    #     last_sha = cia.ci_objs[i-1].instance.git_sha
    #     pickle.dump(new_cia, open(f"cia_cov_only_{last_sha}.pkl", "wb"))
    # exit(-1)
    # versions = ['91ec4b0d11fe115581ce2835300558802ce55e6c','1ae78a14516b9372e4c90a89ac21b259339a3a3a','58390c8ce1bddb6c623f62e7ed36383e7fa5c02f','671e148d079f4d4eca0a98f7dadf1fe69d856374','d295b66a7b66ed504a827b58876ad9ea48c0f4a8','533c54547153d46c0bf99ac0e396bed71f760c03','e338142b39cf40155054f95daa28d210d2ee1b2d','8d15d5e1851b1bbb9cd3289b84c7f32399e06ac5','1639fae5132bc8a904af28d97cea0bedb3af802e','2214170caabbff673935eb046a7edf4621213931','3a8a670eeeaa40d87bd38a587438952741980c18','6cdbb0907a3c562723455e351c940037bdec9b7a','a901a3568fd26ca9c4a82d8bc5ed5b3ed844d451','03275585cabd0240944f19f33d7584a1b099a3a8','3290badd1bb8c9ea91db5c0b2e1a635178119856','7fcd473a6455450428795d20db7afd2691c92336','06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5','fdf0eaf11452d72945af31804e2a1048ee1b574c','18b44bc5a67275641fb26f2c54ba7eef80ac5950','ffabf7c731765da3dbfaffa4ed58b51ae9c2e650','251a94f1f66e909d75a774ac474a63bd9bc38382','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','25aa0bebba72b318e71fe205bfd1236550cc9534','ae545c3283dc673f7e748065efa46ba95f678ef2','4c75bf7e4a0e5472bd8f0bf0a4a418ac717a9b70','b320441c04c9bea76cbee1196ae55c20288fd7a6','28f20a19294da7df158dfca259d0e2b5866baaf9','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','1c59d383390f970b891b503b7f79b63a02db2ec5','b96a3e9142fdf346b05b20e867b4f0dfca119e96','53ea7f624fb91074c2f9458832ed74975ee5d64c','ef2a0b7cdbc5b84f7b3f6573b7687e72bede0964','4debf77169ee459c46ec70e13dc503bc25efd7d2','e0152e7481c6c63764d6ea8ee41af5cf9dfac5e9','92901222f83d988617aee37680cb29e1a743b5e4','3f86ed6ec0b390c033eae7f9c487a3fea268e027','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','744a759492b5c57ff24a6e8aabe47b17ad8ee964','dd1386dd3c4f4bc55456c88180f9f39697bb95c0','2a5a4326e58339a26cd1510259e7310b8c0980ff','535a265d7f0dd50d8c3a4f8b4f3a452d56bd160f','aed8aee11130a954356200afa3f1b8753e8a9482','ad8a69f361b9b9a0272ed66f04e6060b736d2788','8018e02a87031a5e8afcbd9d35133edd520076bb','830380e3178a103d4401689021eadddadbb93d6d','84186fcb834ecc55604efaf383e17e6b5e9baa50','750b95887e567848ac2c851dae47922cac6db946','be3ca57cfb777ad820c6659d52e60bbdd36bf5ff','90450a06162e6c71ab813ea22a83196fe7cff4bc']

    versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1','33afd4b76393627477e878b3b195d606e585d816','825a0714d2b3883d4f8ff64f6933fb73ee3f1834','1a5304fecee523060f26e2778d9d8e33c0562df3','ad2fd53a7870a395b8564697bef6c329d017c6c9','838a854820eea0d21c6910cc3ab23b78d16aa1dd','7877cb91f1081754a1487c144d85dc0d2e2e7fc4','a4d7d701121981e3c3fe69ade376fe9f26324161','4973ca29552864a7a047ab8a15611a585827412f','e660abd551f1172e428b4e4003de887176a8a1fd','6a8cbd9253abc1bd0df4d60c4c24fa555190376d','b30d7a77c53ec04a6d94683d7680ec406b7f3ac8','995b406c7e972fab181a4bb57f3b95e59b8e5bf3','538140ca602b1c5f3870bef051c93b491045f70a','5133c9e51de41bfa902153888e11add3342ede18','8fc3b8f082cc2f5faa6eae315b938bc5e79c332e','c192ac7357683f78c2e6d6e75adfcc29deb8c4ae','5b8d6e8539498e8b2fa67fbcce3fe87834d44a7a','9f9116406120638b4d8db3831ffbc430dd2e1e95','122e7943b252fcf48b4d085dec084e24fc8bec45','024ff300db33968c133435a146d51ac22db27374','13b9372068660fe4f7023f43081067376582ef3c','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','c8afaa1b0f8bc93d013ab2ea6b9649958af3f1d3','a785fd28d31f76d50004712b6e0b409d5a8239d8','9e6c269de404bef2fb50b9407e988083a0805e3b','7d2f353b2682dcfe5f9bc71e5b61d5b61770d98e','97efd28334e271a7e1112ac4dca24d3feea8404b','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','651a00bc56403161351090a9d7ddbd7095975324','1687d8aca5488674686eb46bf49d1d908b2672a1','4fb0dacb78c6a041bbd38ddd998df806af5c2c69','cd99b9eb4b702563c5ac7d26b632a628f5a832a5','87dfd85c38923acd9517e8df4afc908565df0961','b89b029377c8c441649c7a6be908386e74ea9420','2be6bc48df59c99d35aab16a51d4a814e9bb8c35','7733171926cc336ddf0c8f847eefaff569dbff86','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','7ba2090ca64ea1aa435744884124387db1fac70f','6099776f9f268e61fe5ecd721f994a8cfce5306f','a3c57ab79a06e333a869ae340420cb3c6f5921d3','23f108dc9ed26100b1489f6a9e99088d4064f56b','57d88e8a5974644039fbc47806bac7bb12025636','2cf0f715623872823a72e451243bbf555d10d032','95289e49f0a05f729a9ff86243c9aff4f34d4041','e017769f4ce20dc0d3fa3220d4d359dcc4431274','3a568e3a961ba330091cd031647e4c303fa0badb','2af9b20dbb39f6ebf9b9b6c090271594627d818e','305230142ae0637213bf6e04f6d9f10bbcb74af8']
    # for v in versions:
    #     cia = pickle.load(open(f"cia_cov_flaky_{v}.pkl", "rb"))
    #     print(v)
    #     print(cia.ci_objs[0].instance.git_commit_datetime)
    # exit(-1)
    # sql_helper = SQLHelper()
    # checkouts = sql_helper.session.query(DBCheckout).all()
    # cia = CIAnalysis()
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.set_parallel_number(40)
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #     if ci_obj.instance.git_sha in versions:
    #         new_cia = CIAnalysis()
    #         new_cia.ci_objs.append(ci_obj)
    #         pickle.dump(new_cia, open(f"cia_cov_flaky_{cia.ci_objs[i-1].instance.git_sha}.pkl", "wb"))
    # exit(-1)
    def run(sub_version, evaluated_versions):
        cov_info = CoverageHelper(sub_version)
        cov_info.load_coverage4checkout()
        ordered_arr = []
        if args.metric == "total":
            for f, _ in cov_info.total_cov_generator():
                ordered_arr.append(f)
        if args.metric == "additional":
            for f, _ in cov_info.additional_cov_generator():
                ordered_arr.append(f)
        if args.metric == "search":
            for f, _ in cov_info.search_based_generator():
                ordered_arr.append(f)
        if args.metric == "arp":
            for f, _ in cov_info.arp_generator():
                ordered_arr.append(f)
        for ei in range(len(evaluated_versions)):
            sub_version = evaluated_versions[ei]
            cia = pickle.load(open(f"cia_cov_only_{sub_version}.pkl", "rb"))
            ci_obj = cia.ci_objs[0]
            failed_cases = [x.get_testcase_name() for x in ci_obj.get_all_testcases() if x.is_failed()]
            fault_arr = []
            for fc in failed_cases:
                for i in range(len(ordered_arr)):
                    if cov_info.get_coverage_name(fc) == ordered_arr[i]:
                        fault_arr.append(i + 1)
            apfd_v = e_helper.APFD(fault_arr, list(range(1, len(ordered_arr) + 1)))
            logger.info(f"commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}, metric: {args.metric}, passed: {ei+1}")


    # exit(-1)
    if args.metric not in ["total", "additional", "search", "arp"]:
        print(f"no such metric: {args.metric}")
        exit(-1)

    # batch = len(versions) // args.process

    process_pool = multiprocessing.Pool(processes=args.process)

    # process_list = []

    # input_data = []

    # for i in range(args.process):
    #     start = i * batch
    #     end = (i + 1) * batch
    #     if i == args.process - 1:
    #         end = len(versions)
    #     input_data.append(versions[start: end])

    # ci_objs = []
    # for v in versions:
    #     cia = pickle.load(open(f"cia_cov_flaky_{v}.pkl", "rb"))
    #     ci_objs.append(cia.ci_objs[0])
    input_data = []

    for i in range(len(versions) - 3):
        input_data.append((versions[i], versions[i+1:i+4]))
    # print(input_data)
    results = process_pool.starmap(run, input_data)
    process_pool.close()
    process_pool.join()
    # for p in process_list:
    #     p.start()
    # for p in process_list:
    #     p.join()



    # for ci_obj in cia.ci_objs:
    #     cov_info = CoverageHelper(ci_obj.instance.git_sha)
    #     cov_info.load_coverage4checkout()
    #     ordered_arr = []
    #     if args.metric == "total":
    #         for f, _ in cov_info.total_cov_generator():
    #             ordered_arr.append(f)
    #     if args.metric == "additional":
    #         for f, _ in cov_info.additional_cov_generator():
    #             ordered_arr.append(f)
    #     if args.metric == "search":
    #         for f, _ in cov_info.search_based_generator():
    #             ordered_arr.append(f)
    #     if args.metric == "arp":
    #         for f, _ in cov_info.arp_generator():
    #             ordered_arr.append(f)
    #     failed_cases = [x.get_testcase_name() for x in ci_obj.get_all_testcases() if x.is_failed()]
    #     fault_arr = []
    #     for fc in failed_cases:
    #         for i in range(len(ordered_arr)):
    #             if cov_info.get_coverage_name(fc) == ordered_arr[i]:
    #                 fault_arr.append(i + 1)
    #     print(fault_arr)
    #     print(failed_cases)
    #     apfd_v = e_helper.APFD(fault_arr, list(range(1, len(ordered_arr) + 1)))
    #     logger.info(f"commit: {ci_obj.instance.git_sha}, apfd: {apfd_v}, metric: {args.metric}")
    # pass

    exit(-1)
    cov_info = CoverageHelper("35fab9271b7e6d193b47005c4d07369714db4fd1")
    cov_info.load_coverage4checkout()

    # cov_info.search_based_generator()
    for f, _ in cov_info.search_based_generator():
        print(f)
    # cov_info.arp_generator()
    # for f, cov_cnt in cov_info.arp_generator():
    #     print(f, cov_cnt)


    exit(-1)
    cia = pickle.load(open("cia_cov_04-30.pkl", "rb"))
    for i in range(len(cia.ci_objs)):
        ci_obj = cia.ci_objs[i]
        logger.info(f"{ci_obj.instance.git_sha}")
        cov_info = CoverageHelper(ci_obj.instance.git_sha)
        cov_info.load_coverage4checkout()

        for f, cov_cnt in cov_info.additional_cov_generator():
            print(f, cov_cnt)


        exit(-1)

        # cnt = 0
        # not_cov_names = []
        # for tc in ci_obj.get_all_testcases():
        #     cov_name = tc.get_testcase_name() + "_coverage"
        #     cov_name = cov_name.replace("-", "_")
        #     cov_name = cov_name.replace(":", "_")
        #     cov_name = cov_name.replace(".", "_")
        #
        #     if cov_name not in cov_info.coverage_info.keys():
        #         cnt += 1
        #         not_cov_names.append(cov_name)
        # logger.info(ci_obj.instance.git_sha)
        # logger.info(f"not found {cnt}")
        # logger.info(not_cov_names)





    # cov_helper = CoverageHelper("838a854820eea0d21c6910cc3ab23b78d16aa1dd")
    # cov_helper.load_coverage_info("/home/wanghaichi/repro_linuxs/838a854820eea0d21c6910cc3ab23b78d16aa1dd/cpuset_syscall_testset_coverage.info")
    # exit(-1)

    # versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1','33afd4b76393627477e878b3b195d606e585d816','825a0714d2b3883d4f8ff64f6933fb73ee3f1834','1a5304fecee523060f26e2778d9d8e33c0562df3','ad2fd53a7870a395b8564697bef6c329d017c6c9','838a854820eea0d21c6910cc3ab23b78d16aa1dd','7877cb91f1081754a1487c144d85dc0d2e2e7fc4','a4d7d701121981e3c3fe69ade376fe9f26324161','4973ca29552864a7a047ab8a15611a585827412f','e660abd551f1172e428b4e4003de887176a8a1fd','6a8cbd9253abc1bd0df4d60c4c24fa555190376d','b30d7a77c53ec04a6d94683d7680ec406b7f3ac8','995b406c7e972fab181a4bb57f3b95e59b8e5bf3','538140ca602b1c5f3870bef051c93b491045f70a','5133c9e51de41bfa902153888e11add3342ede18','8fc3b8f082cc2f5faa6eae315b938bc5e79c332e','c192ac7357683f78c2e6d6e75adfcc29deb8c4ae','5b8d6e8539498e8b2fa67fbcce3fe87834d44a7a','9f9116406120638b4d8db3831ffbc430dd2e1e95','122e7943b252fcf48b4d085dec084e24fc8bec45','024ff300db33968c133435a146d51ac22db27374','13b9372068660fe4f7023f43081067376582ef3c','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','c8afaa1b0f8bc93d013ab2ea6b9649958af3f1d3','a785fd28d31f76d50004712b6e0b409d5a8239d8','9e6c269de404bef2fb50b9407e988083a0805e3b','7d2f353b2682dcfe5f9bc71e5b61d5b61770d98e','97efd28334e271a7e1112ac4dca24d3feea8404b','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','651a00bc56403161351090a9d7ddbd7095975324','1687d8aca5488674686eb46bf49d1d908b2672a1','4fb0dacb78c6a041bbd38ddd998df806af5c2c69','cd99b9eb4b702563c5ac7d26b632a628f5a832a5','87dfd85c38923acd9517e8df4afc908565df0961','b89b029377c8c441649c7a6be908386e74ea9420','2be6bc48df59c99d35aab16a51d4a814e9bb8c35','7733171926cc336ddf0c8f847eefaff569dbff86','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','7ba2090ca64ea1aa435744884124387db1fac70f','6099776f9f268e61fe5ecd721f994a8cfce5306f','a3c57ab79a06e333a869ae340420cb3c6f5921d3','23f108dc9ed26100b1489f6a9e99088d4064f56b','57d88e8a5974644039fbc47806bac7bb12025636','2cf0f715623872823a72e451243bbf555d10d032','95289e49f0a05f729a9ff86243c9aff4f34d4041','e017769f4ce20dc0d3fa3220d4d359dcc4431274','3a568e3a961ba330091cd031647e4c303fa0badb','2af9b20dbb39f6ebf9b9b6c090271594627d818e','305230142ae0637213bf6e04f6d9f10bbcb74af8']
    # root = "/home/wanghaichi/repro_linuxs"
    # for v in versions:
    #     logger.info(v)
    #     cov_helper = CoverageHelper(v)
    #     cov_helper.load_coverage4checkout()
    #     # print(cov_helper.coverage_info)


    # log_path = "/data/wanghaichi/kernelTCP/logs/main-2024-04-12-14:29:49.txt"
    # root = Path("/data/wanghaichi/repro_results")
    # cnt = 0
    # verify_cnt = 0
    # file_set = set()
    # for line in Path(log_path).read_text().split("\n"):
    #     temp = line.split(" ")
    #     if len(temp) != 15:
    #         # print(len(temp))
    #         continue
    #     checkout = temp[-3]
    #     build_name = temp[-2]
    #     tc_name = temp[-1]
    #     tc_res_path = root / checkout / (tc_name + ".result")
    #     if tc_res_path.exists():
    #         cnt += 1
    #         suite_name = "ltp"
    #         if ":" in tc_name:
    #             suite_name = "selftest"
    #         result_info = TCResult.create(tc_name, suite_name, tc_res_path.read_text())
    #         if result_info.total_failed_cnt() > 0 or result_info.total_broken_cnt() > 0:
    #             file_set.add(tc_name)
    #             verify_cnt += 1
    #     else:
    #         print(checkout, build_name, tc_name)
    # print(cnt)
    # print(verify_cnt)
    # for f in file_set:
    #     print(f)
    # print(len(file_set))
    # exit(-1)

    # files = ["test_cases/selftests/net/srv6_hencap_red_l3vpn_test.sh",
    #          "test_cases/selftests/tc-testing/tdc.sh",
    #          "test_cases/selftests/net/unicast_extensions.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move21.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/statx/statx06.c",
    #          "test_cases/selftests/net/icmp_redirect.sh",
    #          "test_cases/selftests/net/reuseport_bpf.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind35.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/sendfile/sendfile07.c",
    #          "test_cases/selftests/net/l2_tos_ttl_inherit.sh",
    #          "test_cases/selftests/net/vrf-xfrm-tests.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmget/hugeshmget05.c",
    #          "test_cases/selftests/net/rxtimestamp.sh",
    #          "test_cases/selftests/x86/fsgsbase.c",
    #          "test_cases/selftests/net/bind_bhash.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/memcontrol02.c",
    #          "test_cases/selftests/net/test_vxlan_vnifiltering.sh",
    #          "test_cases/selftests/net/udpgso.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/functional/memcg_force_empty.sh",
    #          "test_cases/selftests/net/cmsg_ipv6.sh",
    #          "test_cases/selftests/net/fib_rule_tests.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmctl/hugeshmctl03.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/ustat/ustat02.c",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmget/hugeshmget03.c",
    #          "test_cases/selftests/net/test_ingress_egress_chaining.sh",
    #          "test_cases/selftests/net/fib-onlink-tests.sh",
    #          "test_cases/selftests/net/srv6_end_dt46_l3vpn_test.sh",
    #          "test_cases/selftests/net/mptcp/mptcp_connect.sh",
    #          "test_cases/selftests/user_events/dyn_test.c",
    #          "test_cases/selftests/net/reuseport_dualstack.c",
    #          "test_cases/selftests/net/sk_connect_zero_addr.c",
    #          "test_cases/ltp/testcases/kernel/sched/clisrv/run_sched_cliserv.sh",
    #          "test_cases/selftests/net/io_uring_zerocopy_tx.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/ipc/shmctl/shmctl03.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/io_pgetevents/io_pgetevents02.c",
    #          "test_cases/selftests/net/srv6_end_dt6_l3vpn_test.sh",
    #          "test_cases/selftests/x86/amx.c",
    #          "test_cases/selftests/openat2/resolve_test.c",
    #          "test_cases/selftests/net/reuseport_addr_any.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/io_uring/io_uring01.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/ipc/shmget/shmget02.c",
    #          "test_cases/selftests/net/sk_bind_sendto_listen.c",
    #          "test_cases/selftests/x86/mov_ss_trap.c",
    #          "test_cases/selftests/net/fin_ack_lat.sh",
    #          "test_cases/selftests/net/ndisc_unsolicited_na_test.sh",
    #          "test_cases/selftests/net/test_blackhole_dev.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/epoll_wait/epoll_wait04.c",
    #          "test_cases/selftests/cgroup/test_cpu.c",
    #          "test_cases/selftests/net/mptcp/mptcp_join.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move09.sh",
    #          "test_cases/selftests/net/stress_reuseport_listen.sh",
    #          "test_cases/selftests/net/cmsg_time.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind21.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmget/hugeshmget01.c",
    #          "test_cases/selftests/net/devlink_port_split.py",
    #          "test_cases/selftests/net/netdevice.sh",
    #          "test_cases/selftests/net/udpgro_fwd.sh",
    #          "test_cases/selftests/net/rps_default_mask.sh",
    #          "test_cases/selftests/net/udpgso_bench.sh",
    #          "test_cases/selftests/net/test_vxlan_under_vrf.sh",
    #          "test_cases/selftests/user_events/perf_test.c",
    #          "test_cases/ltp/testcases/kernel/sched/cfs-scheduler/starvation.c",
    #          "test_cases/selftests/net/setup_veth.sh",
    #          "test_cases/selftests/net/txtimestamp.sh",
    #          "test_cases/selftests/clone3/clone3.c",
    #          "test_cases/selftests/rtc/rtctest.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS06.sh",
    #          "test_cases/selftests/net/test_vxlan_mdb.sh",
    #          "test_cases/selftests/net/route_localnet.sh",
    #          "test_cases/selftests/net/drop_monitor_tests.sh",
    #          "test_cases/selftests/net/altnames.sh",
    #          "test_cases/selftests/net/amt.sh",
    #          "test_cases/selftests/x86/test_shadow_stack.c",
    #          "test_cases/selftests/x86/syscall_numbering.c",
    #          "test_cases/selftests/net/arp_ndisc_untracked_subnets.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/futex/futex_waitv01.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind34.sh",
    #          "test_cases/selftests/net/fib_tests.sh",
    #          "test_cases/selftests/futex/functional/futex_requeue.c",
    #          "test_cases/selftests/net/ip6_gre_headroom.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmget/hugeshmget02.c",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/functional/memcg_limit_in_bytes.sh",
    #          "test_cases/selftests/net/ioam6.sh",
    #          "test_cases/selftests/net/gro.sh",
    #          "test_cases/selftests/net/tun.c",
    #          "test_cases/selftests/firmware/fw_run_tests.sh",
    #          "test_cases/selftests/user_events/ftrace_test.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind36.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/time/time01.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/ustat/ustat01.c",
    #          "test_cases/selftests/net/srv6_end_next_csid_l3vpn_test.sh",
    #          "test_cases/selftests/net/tap.c",
    #          "test_cases/selftests/net/test_bridge_neigh_suppress.sh",
    #          "test_cases/ltp/testcases/kernel/containers/pidns/pidns05.c",
    #          "test_cases/selftests/openat2/rename_attack_test.c",
    #          "test_cases/selftests/net/reuseaddr_conflict.c",
    #          "test_cases/selftests/openat2/openat2_test.c",
    #          "test_cases/selftests/net/test_bridge_backup_port.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/cloneNS/fs_bind_cloneNS07.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/io/io_control01.c",
    #          "test_cases/selftests/net/netns-name.sh",
    #          "test_cases/selftests/net/test_vxlan_fdb_changelink.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/getrusage/getrusage04.c",
    #          "test_cases/selftests/net/srv6_end_x_next_csid_l3vpn_test.sh",
    #          "test_cases/selftests/net/vrf_strict_mode_test.sh",
    #          "test_cases/selftests/net/fcnal-test.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/bind/fs_bind22.sh",
    #          "test_cases/selftests/net/icmp.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fsx-linux/fsx-linux.c",
    #          "test_cases/ltp/testcases/kernel/controllers/cpuset/cpuset_hotplug_test/cpuset_hotplug_test.sh",
    #          "test_cases/selftests/net/mptcp/simult_flows.sh",
    #          "test_cases/selftests/ftrace/ftracetest",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/move/fs_bind_move22.sh",
    #          "test_cases/selftests/net/arp_ndisc_evict_nocarrier.sh",
    #          "test_cases/selftests/cgroup/test_memcontrol.c",
    #          "test_cases/ltp/testcases/kernel/fs/read_all/read_all.c",
    #          "test_cases/selftests/net/sctp_vrf.sh",
    #          "test_cases/ltp/testcases/kernel/fs/fs_fill/fs_fill.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/io_uring/io_uring02.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_perms/fs_perms.c",
    #          "test_cases/selftests/net/ip_defrag.sh",
    #          "test_cases/selftests/net/so_incoming_cpu.c",
    #          "test_cases/selftests/user_events/abi_test.c",
    #          "test_cases/selftests/net/traceroute.sh",
    #          "test_cases/selftests/net/srv6_end_dt4_l3vpn_test.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmctl/hugeshmctl02.c",
    #          "test_cases/selftests/net/srv6_hl2encap_red_l2vpn_test.sh",
    #          "test_cases/selftests/net/so_txtime.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/functional/memcg_memsw_limit_in_bytes_test.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/fanotify/fanotify22.c",
    #          "test_cases/ltp/testcases/kernel/fs/fs_bind/rbind/fs_bind_rbind39.sh",
    #          "test_cases/selftests/net/tcp_fastopen_backup_key.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/ioprio/ioprio_set03.c",
    #          "test_cases/selftests/x86/lam.c",
    #          "test_cases/selftests/gpio/gpio-mockup.sh",
    #          "test_cases/ltp/testcases/kernel/syscalls/accept/accept02.c",
    #          "test_cases/selftests/net/l2tp.sh",
    #          "test_cases/ltp/testcases/cve/meltdown.c",
    #          "test_cases/selftests/net/udpgro_bench.sh",
    #          "test_cases/selftests/net/gre_gso.sh",
    #          "test_cases/selftests/kexec/test_kexec_load.sh",
    #          "test_cases/selftests/net/fib_nexthop_multiprefix.sh",
    #          "test_cases/selftests/exec/execveat.c",
    #          "test_cases/selftests/net/udpgro_frglist.sh",
    #          "test_cases/selftests/net/run_netsocktests",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/memcontrol04.c",
    #          "test_cases/selftests/net/ip_local_port_range.sh",
    #          "test_cases/selftests/net/pmtu.sh",
    #          "test_cases/selftests/futex/run.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/cpuset/cpuset_inherit_test/cpuset_inherit_testset.sh",
    #          "test_cases/selftests/net/test_vxlan_nolocalbypass.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/functional/memcg_failcnt.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/memcontrol03.c",
    #          "test_cases/selftests/memfd/memfd_test.c",
    #          "test_cases/selftests/net/big_tcp.sh",
    #          "test_cases/selftests/net/bareudp.sh",
    #          "test_cases/selftests/net/test_bpf.sh",
    #          "test_cases/selftests/net/reuseaddr_ports_exhausted.sh",
    #          "test_cases/selftests/net/vrf_route_leaking.sh",
    #          "test_cases/selftests/net/psock_snd.sh",
    #          "test_cases/selftests/net/ipv6_flowlabel.sh",
    #          "test_cases/selftests/net/cmsg_so_mark.sh",
    #          "test_cases/ltp/testcases/kernel/mem/hugetlb/hugeshmdt/hugeshmdt01.c",
    #          "test_cases/ltp/testcases/kernel/syscalls/recvmmsg/recvmmsg01.c",
    #          "test_cases/selftests/net/srv6_end_flavors_test.sh",
    #          "test_cases/ltp/testcases/kernel/controllers/memcg/regression/memcg_test_3.c",
    #          "test_cases/selftests/net/fib_nexthop_nongw.sh", ]
    #
    # already_f = {}
    # for f in Path("/home/wanghaichi/repro_results").rglob("**/*.result"):
    #     if f.stem not in already_f.keys():
    #         already_f[f.stem] = []
    #     already_f[f.stem].append(f.absolute())
    # for f in files:
    #     tc = Test()
    #     tc.file_path = f
    #     if tc.get_testcase_name() in already_f.keys():
    #         for res_i in already_f[tc.get_testcase_name()]:
    #             res = TCResult.create(tc.get_testcase_name(), tc.get_suite_name(), Path(res_i).read_text())
    #             if res.total_failed_cnt() > 0:
    #                 logger.info(f"{tc.get_testcase_name()} failed at {res_i}")
    #     else:
    #         logger.info(f"{tc.get_testcase_name()} not found")
    # exit(-1)
    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).all()
    # cia = CIAnalysis()
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # # cia = pickle.load(open("cia-04-10.pkl", "rb"))
    # failed_testcases = set()
    # failed_str = set()
    #
    # for ci_obj in cia.ci_objs:
    #     for b in ci_obj.builds:
    #         for tc in b.get_all_testcases():
    #             if tc.is_failed():
    #                 failed_testcases.add(tc.file_path)
    #                 failed_str.add(f"{tc.instance.id} {ci_obj.instance.git_sha} {b.label} {tc.get_testcase_name()}")
    # # for ftc in failed_testcases:
    # #     logger.info(ftc)
    # for fs in failed_str:
    #     logger.info(fs)
    # logger.info(len(failed_testcases))
    # exit(-1)
    #
    # repro_root = Path("/home/wanghaichi/repro_results")
    # failed_version = set()
    # failed_path = set()
    # failed_case = set()
    # failed_case_m = {}
    # for ci_obj in cia.ci_objs:
    #     failed_cnt = 0
    #     failed_total = 0
    #     broken_cnt = 0
    #
    #     for tc in cia.get_all_testcases():
    #         if tc.is_failed():
    #             res_path = repro_root / ci_obj.instance.git_sha / (tc.get_testcase_name() + ".result")
    #             if res_path.exists():
    #                 if res_path.exists():
    #                     pass
    #                     failed_total += 1
    #                     tc_result = TCResult.create(tc.get_testcase_name(), tc.get_suite_name(), res_path.read_text())
    #                     if tc_result.total_failed_cnt() > 0:
    #                         # print(f"{ci_obj.instance.git_sha} {tc.get_testcase_name()} failed")
    #                         failed_version.add(ci_obj.instance.git_sha)
    #                         failed_path.add(res_path.absolute())
    #                         failed_case.add(tc.get_testcase_name())
    #                         failed_cnt += 1
    #                         failed_case_m[tc.get_testcase_name()] = failed_case_m.get(tc.get_testcase_name(), 0) + 1
    #                     elif tc_result.total_broken_cnt() > 0:
    #                         broken_cnt += 1
    #                     else:
    #                         pass
    #                         # print(ltp_result.total_pass_cnt())
    #                         # print(res_path.absolute())
    #                 else:
    #                     print(f"{tc.get_testcase_name()} not found")
    #                     # print(res_path.absolute())
    #                 # print(f"{tc.get_testcase_name()} is self test" )
    # print(len(failed_version))
    # for p in failed_path:
    #     print(p)
    # print(len(failed_case))
    # for k, v in failed_case_m.items():
    #     print(k, v)
    # pass
