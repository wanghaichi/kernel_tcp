import copy
import pickle
import time
from pathlib import Path
from termcolor import colored

from liebes.sql_helper import SQLHelper

from liebes.CiObjects import DBCheckout, Checkout
from liebes.analysis import CIAnalysis

if __name__ == "__main__":
    #
    # # root = "/home/wanghaichi/repro_linuxs"
    # # for sub_dir in Path(root).iterdir():
    # #     count = 0
    # #     for f in sub_dir.glob("**/*.gz"):
    # #         count += 1
    # #     print(sub_dir.name, count)
    # # exit(-1)
    # #
    # #
    # #
    # # n = set(['e1d809b3c5d1d9988350755454747a105dad331b','ac347a0655dbc7d885e217c89dddd16e2800bd58','18553507f60f4f51f071644621a58836eb59e28c','3ca112b71f35dd5d99fc4571a56b5fc6f0c15814','1b907d0507354b74a4f2c286380cd6059af79248','b57b17e88bf58860dad312d08db7d6708ee6d06d','e257da5715365b853439243f89cf5d8a9d382355','b85ea95d086471afb4ad062012a4d73cd328fa86','9bacdd8996c77c42ca004440be610692275ff9d0','791c8ab095f71327899023223940dd52257a4173','05aa69b096a089dc85391e36ccdce76961694e22','037266a5f7239ead1530266f7d7af153d2a867fa','eb3479bc23fafbc408558cd8450b35f07fad2a63','0f5cc96c367f2e780eb492cc9cab84e3b2ca88da','4892711acee0915a8a4ae02e1af3dc70ce000024','d2da77f431ac49b5763b88751a75f70daa46296c','2cc14f52aeb78ce3f29677c2de1f06c0e91471ab','c9a925b7bcd9552f19ba50519c6a49ed7ca61691','1b8af6552cb7c9bf1194e871f8d733a19b113230','968f35f4ab1c0966ceb39af3c89f2e24afedf878','4df7c5fde316820286dfa6d203a1005d7fbe007d','f2e8a57ee9036c7d5443382b6c3c09b51a92ec7e','c527f5606aa545233a4d2c6d5c636ed82b8633ef','a39b6ac3781d46ba18193c9dbb2110f31e9bffe9','a62aa88ba1a386e9b6953083b1ceb2fe027238b9','c8e97fc6b4c057a350a9e9a1ad625e10cc9c39ee','3b8a9b2e6809d281890dd0a1102dc14d2cd11caf','0e389834672c723435a44818ed2cabc4dad24429','177c2ffe69555dde28fad5ddb62a6d806982e53f','ceb6a6f023fd3e8b07761ed900352ef574010bcb','24f3a63e1fc36d5d240c1b3973c75618c20cf458','db5ccb9eb23189e99e244a4915dd31eedd8d428b','556e2d17cae620d549c5474b1ece053430cd50bc','c25b24fa72c734f8cd6c31a13548013263b26286','65163d16fcaef37733b5f273ffe4d00d731b34de','41bccc98fb7931d63d03f326a746ac4d429c1dd3','1bbb19b6eb1b8685ab1c268a401ea64380b8bbcb','54be6c6c5ae8e0d93a6c4641cb7528eb0b6ba478','0f1dd5e91e2ba3990143645faff2bcce2d99778e','c1ca10ceffbb289ed02feaf005bc9ee6095b4507'])
    # # o = set(['91ec4b0d11fe115581ce2835300558802ce55e6c','1ae78a14516b9372e4c90a89ac21b259339a3a3a','58390c8ce1bddb6c623f62e7ed36383e7fa5c02f','671e148d079f4d4eca0a98f7dadf1fe69d856374','d295b66a7b66ed504a827b58876ad9ea48c0f4a8','533c54547153d46c0bf99ac0e396bed71f760c03','e338142b39cf40155054f95daa28d210d2ee1b2d','8d15d5e1851b1bbb9cd3289b84c7f32399e06ac5','1639fae5132bc8a904af28d97cea0bedb3af802e','2214170caabbff673935eb046a7edf4621213931','3a8a670eeeaa40d87bd38a587438952741980c18','6cdbb0907a3c562723455e351c940037bdec9b7a','a901a3568fd26ca9c4a82d8bc5ed5b3ed844d451','03275585cabd0240944f19f33d7584a1b099a3a8','3290badd1bb8c9ea91db5c0b2e1a635178119856','7fcd473a6455450428795d20db7afd2691c92336','06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5','fdf0eaf11452d72945af31804e2a1048ee1b574c','18b44bc5a67275641fb26f2c54ba7eef80ac5950','ffabf7c731765da3dbfaffa4ed58b51ae9c2e650','251a94f1f66e909d75a774ac474a63bd9bc38382','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','25aa0bebba72b318e71fe205bfd1236550cc9534','ae545c3283dc673f7e748065efa46ba95f678ef2','4c75bf7e4a0e5472bd8f0bf0a4a418ac717a9b70','b320441c04c9bea76cbee1196ae55c20288fd7a6','28f20a19294da7df158dfca259d0e2b5866baaf9','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','1c59d383390f970b891b503b7f79b63a02db2ec5','b96a3e9142fdf346b05b20e867b4f0dfca119e96','53ea7f624fb91074c2f9458832ed74975ee5d64c','ef2a0b7cdbc5b84f7b3f6573b7687e72bede0964','4debf77169ee459c46ec70e13dc503bc25efd7d2','e0152e7481c6c63764d6ea8ee41af5cf9dfac5e9','92901222f83d988617aee37680cb29e1a743b5e4','3f86ed6ec0b390c033eae7f9c487a3fea268e027','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','744a759492b5c57ff24a6e8aabe47b17ad8ee964','dd1386dd3c4f4bc55456c88180f9f39697bb95c0','2a5a4326e58339a26cd1510259e7310b8c0980ff','535a265d7f0dd50d8c3a4f8b4f3a452d56bd160f','aed8aee11130a954356200afa3f1b8753e8a9482','ad8a69f361b9b9a0272ed66f04e6060b736d2788','8018e02a87031a5e8afcbd9d35133edd520076bb','830380e3178a103d4401689021eadddadbb93d6d','84186fcb834ecc55604efaf383e17e6b5e9baa50','750b95887e567848ac2c851dae47922cac6db946','be3ca57cfb777ad820c6659d52e60bbdd36bf5ff','90450a06162e6c71ab813ea22a83196fe7cff4bc'])
    # # print(o - n)
    # # print(n - o)
    # # exit(-1)
    #
    # # cia = pickle.load(open("cia-04-10.pkl", "rb"))
    # # for ci_obj in cia.ci_objs:
    # #     failed_cases = [x for x in ci_obj.get_all_testcases() if x.is_failed()]
    # # #     print(f"{ci_obj.instance.git_sha}: {len(failed_cases)}")
    # sql = SQLHelper()
    # checkouts = sql.session.query(DBCheckout).all()
    # #
    # cia = CIAnalysis()
    # cia.set_parallel_number(40)
    # for ch in checkouts:
    #     cia.ci_objs.append(Checkout(ch))
    # cia.reorder()
    # cia.filter_job("COMBINE_SAME_CASE")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("COMBINE_SAME_CONFIG")
    # cia.filter_job("CHOOSE_ONE_BUILD")
    # cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    # cia.statistic_data()
    # cia.ci_objs = cia.ci_objs[1:]
    # pickle.dump(cia, open("cia-04-24.pkl", "wb"))
    # exit(-1)
    #
    #
    #
    # failed_objs = []
    # next_objs = []
    # failed_objs_5 = []
    # failed_objs_10 = []
    # failed_objs_15 = []
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #     failed_count = len([x for x in ci_obj.get_all_testcases() if x.is_failed()])
    #     if failed_count > 0 and i > 0:
    #         failed_objs.append(cia.ci_objs[i - 1])
    #         next_objs.append(cia.ci_objs[i].instance.git_sha)
    #         if i > 5:
    #             failed_objs_5.append(cia.ci_objs[i - 5])
    #         if i > 10:
    #             failed_objs_10.append(cia.ci_objs[i - 10])
    #         if i > 15:
    #             failed_objs_15.append(cia.ci_objs[i - 15])
    #
    # print("=====0=====")
    # for ch in failed_objs:
    #     print(ch.instance.git_sha)
    # print("=====5=====")
    # for ch in failed_objs_5:
    #     print(ch.instance.git_sha)
    # print("=====10=====")
    # for ch in failed_objs_10:
    #     print(ch.instance.git_sha)
    # print("======15====")
    # for ch in failed_objs_15:
    #     print(ch.instance.git_sha)
    # print("===========")
    #
    # exit(-1)
    # cia.ci_objs = failed_objs
    # for ch in cia.ci_objs:
    #     print(ch.instance.git_sha)
    # print("===========")
    # for ch in next_objs:
    #     print(ch)
    # exit(-1)

    #
    # failed_objs = []
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #     failed_count = len([x for x in ci_obj.get_all_testcases() if x.is_failed()])
    #     if failed_count > 0 and i > 0:
    #         failed_objs.append(cia.ci_objs[i - 1])
    # cia.ci_objs = failed_objs

    versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1','33afd4b76393627477e878b3b195d606e585d816','825a0714d2b3883d4f8ff64f6933fb73ee3f1834','1a5304fecee523060f26e2778d9d8e33c0562df3','ad2fd53a7870a395b8564697bef6c329d017c6c9','838a854820eea0d21c6910cc3ab23b78d16aa1dd','7877cb91f1081754a1487c144d85dc0d2e2e7fc4','a4d7d701121981e3c3fe69ade376fe9f26324161','4973ca29552864a7a047ab8a15611a585827412f','e660abd551f1172e428b4e4003de887176a8a1fd','6a8cbd9253abc1bd0df4d60c4c24fa555190376d','b30d7a77c53ec04a6d94683d7680ec406b7f3ac8','995b406c7e972fab181a4bb57f3b95e59b8e5bf3','538140ca602b1c5f3870bef051c93b491045f70a','5133c9e51de41bfa902153888e11add3342ede18','8fc3b8f082cc2f5faa6eae315b938bc5e79c332e','c192ac7357683f78c2e6d6e75adfcc29deb8c4ae','5b8d6e8539498e8b2fa67fbcce3fe87834d44a7a','9f9116406120638b4d8db3831ffbc430dd2e1e95','122e7943b252fcf48b4d085dec084e24fc8bec45','024ff300db33968c133435a146d51ac22db27374','13b9372068660fe4f7023f43081067376582ef3c','cacc6e22932f373a91d7be55a9b992dc77f4c59b','374a7f47bf401441edff0a64465e61326bf70a82','c8afaa1b0f8bc93d013ab2ea6b9649958af3f1d3','a785fd28d31f76d50004712b6e0b409d5a8239d8','9e6c269de404bef2fb50b9407e988083a0805e3b','7d2f353b2682dcfe5f9bc71e5b61d5b61770d98e','97efd28334e271a7e1112ac4dca24d3feea8404b','6383cb42ac01e6fb9ef6a035a2288786e61bdddf','36534782b584389afd281f326421a35dcecde1ec','651a00bc56403161351090a9d7ddbd7095975324','1687d8aca5488674686eb46bf49d1d908b2672a1','4fb0dacb78c6a041bbd38ddd998df806af5c2c69','cd99b9eb4b702563c5ac7d26b632a628f5a832a5','87dfd85c38923acd9517e8df4afc908565df0961','b89b029377c8c441649c7a6be908386e74ea9420','2be6bc48df59c99d35aab16a51d4a814e9bb8c35','7733171926cc336ddf0c8f847eefaff569dbff86','65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4','7ba2090ca64ea1aa435744884124387db1fac70f','6099776f9f268e61fe5ecd721f994a8cfce5306f','a3c57ab79a06e333a869ae340420cb3c6f5921d3','23f108dc9ed26100b1489f6a9e99088d4064f56b','57d88e8a5974644039fbc47806bac7bb12025636','2cf0f715623872823a72e451243bbf555d10d032','95289e49f0a05f729a9ff86243c9aff4f34d4041','e017769f4ce20dc0d3fa3220d4d359dcc4431274','3a568e3a961ba330091cd031647e4c303fa0badb','2af9b20dbb39f6ebf9b9b6c090271594627d818e','305230142ae0637213bf6e04f6d9f10bbcb74af8']
    sql = SQLHelper()
    res = sql.session.query(DBCheckout).filter(DBCheckout.git_sha.in_(versions)).all()
    cnt_m = {}
    for ch in res:
        cia = CIAnalysis()
        cia.ci_objs.append(Checkout(ch))
        cia.filter_job("COMBINE_SAME_CASE")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cia.filter_job("COMBINE_SAME_CONFIG")
        cia.filter_job("CHOOSE_ONE_BUILD")
        cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
        cnt_m[cia.ci_objs[0].instance.git_sha] = len(cia.get_all_testcases())
    # for v in versions:
    #     if v not in cnt_m.keys():
    #         print(v, "??????")
    # exit(-1)
    root_res = "/home/wanghaichi/repro_results"
    root_cov = "/home/wanghaichi/repro_linuxs"
    previous = {}
    first = True
    while True:
        total_left = 0
        total = 0
        total_left_parsed = 0
        for version in versions:
            res_path = Path(root_res) / version
            cov_path = Path(root_cov) / version
            if not cov_path.exists():
                print(f"{version} not started!")
                continue
            finished_number = 0
            parsed_number = 0
            gzs = cov_path.glob("*.tar.gz")
            for f in gzs:
                finished_number += 1
            infos = cov_path.glob("*.info")
            for f in infos:
                parsed_number += 1
            if first:
                print(f"{version} progress: {finished_number} ({finished_number / cnt_m[version] * 100:.2f}%)/ {parsed_number} ({parsed_number / finished_number * 100 :.2f}%) / {cnt_m[version]} .")
            else:
                finished_changed = finished_number - previous[version]['finished']
                parsed_changed = parsed_number - previous[version]['parsed']
                finished_str = ""
                parsed_str = ""
                if finished_changed > 0:
                    finished_str = colored(f"+ {finished_changed}", "green")
                if parsed_changed > 0:
                    parsed_str = colored(f"+ {parsed_changed}", "green")
                print(f"{version} progress: {finished_number} {finished_str} ({finished_number / cnt_m[version] * 100:.2f}%)/ {parsed_number} {parsed_str} ({parsed_number / finished_number * 100 :.2f}%) / {cnt_m[version]} .")
            total_left += finished_number
            total += cnt_m[version]
            total_left_parsed += parsed_number

            previous[version] = {"finished": finished_number, "parsed": parsed_number}
        if first:
            print(
                f"{total_left} {(total_left / total * 100):.2f}% / {total_left_parsed} ({total_left_parsed / total_left * 100:.2f}%) / {total} ")
        else:
            finished_changed = total_left - previous['total_left']
            parsed_changed = total_left_parsed - previous['total_left_parsed']
            finished_str = ""
            parsed_str = ""
            if finished_changed > 0:
                finished_str = colored(f"+ {finished_changed}", "green")
            if parsed_changed > 0:
                parsed_str = colored(f"+ {parsed_changed}", "green")
            print(
                f"{total_left} {finished_str} {(total_left / total * 100):.2f}% / {total_left_parsed} {parsed_str} ({total_left_parsed / total_left * 100:.2f}%) / {total} ")
        previous['total_left'] = total_left
        previous['total'] = total
        previous['total_left_parsed'] = total_left_parsed

        first = False
        print("=====================================")
        time.sleep(60)
