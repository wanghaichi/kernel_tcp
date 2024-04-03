import time
from pathlib import Path

if __name__ == "__main__":
    versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1', '33afd4b76393627477e878b3b195d606e585d816',
                '825a0714d2b3883d4f8ff64f6933fb73ee3f1834', '1a5304fecee523060f26e2778d9d8e33c0562df3',
                'ad2fd53a7870a395b8564697bef6c329d017c6c9', '838a854820eea0d21c6910cc3ab23b78d16aa1dd',
                '7877cb91f1081754a1487c144d85dc0d2e2e7fc4', 'a4d7d701121981e3c3fe69ade376fe9f26324161',
                '4973ca29552864a7a047ab8a15611a585827412f', 'e660abd551f1172e428b4e4003de887176a8a1fd',
                '6a8cbd9253abc1bd0df4d60c4c24fa555190376d', 'b30d7a77c53ec04a6d94683d7680ec406b7f3ac8',
                '995b406c7e972fab181a4bb57f3b95e59b8e5bf3', '538140ca602b1c5f3870bef051c93b491045f70a',
                '5133c9e51de41bfa902153888e11add3342ede18', '8fc3b8f082cc2f5faa6eae315b938bc5e79c332e',
                'c192ac7357683f78c2e6d6e75adfcc29deb8c4ae', '5b8d6e8539498e8b2fa67fbcce3fe87834d44a7a',
                '9f9116406120638b4d8db3831ffbc430dd2e1e95', '122e7943b252fcf48b4d085dec084e24fc8bec45',
                '024ff300db33968c133435a146d51ac22db27374', '13b9372068660fe4f7023f43081067376582ef3c',
                'cacc6e22932f373a91d7be55a9b992dc77f4c59b', '374a7f47bf401441edff0a64465e61326bf70a82',
                'c8afaa1b0f8bc93d013ab2ea6b9649958af3f1d3', 'a785fd28d31f76d50004712b6e0b409d5a8239d8',
                '9e6c269de404bef2fb50b9407e988083a0805e3b', '7d2f353b2682dcfe5f9bc71e5b61d5b61770d98e',
                '97efd28334e271a7e1112ac4dca24d3feea8404b', '6383cb42ac01e6fb9ef6a035a2288786e61bdddf',
                '36534782b584389afd281f326421a35dcecde1ec', '651a00bc56403161351090a9d7ddbd7095975324',
                '1687d8aca5488674686eb46bf49d1d908b2672a1', '4fb0dacb78c6a041bbd38ddd998df806af5c2c69',
                'cd99b9eb4b702563c5ac7d26b632a628f5a832a5', '87dfd85c38923acd9517e8df4afc908565df0961',
                'b89b029377c8c441649c7a6be908386e74ea9420', '2be6bc48df59c99d35aab16a51d4a814e9bb8c35',
                '7733171926cc336ddf0c8f847eefaff569dbff86', '65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4',
                '7ba2090ca64ea1aa435744884124387db1fac70f', '6099776f9f268e61fe5ecd721f994a8cfce5306f',
                'a3c57ab79a06e333a869ae340420cb3c6f5921d3', '23f108dc9ed26100b1489f6a9e99088d4064f56b',
                '57d88e8a5974644039fbc47806bac7bb12025636', '2cf0f715623872823a72e451243bbf555d10d032',
                '95289e49f0a05f729a9ff86243c9aff4f34d4041', 'e017769f4ce20dc0d3fa3220d4d359dcc4431274',
                '3a568e3a961ba330091cd031647e4c303fa0badb', '2af9b20dbb39f6ebf9b9b6c090271594627d818e',
                '305230142ae0637213bf6e04f6d9f10bbcb74af8']

    root_res = "/home/wanghaichi/repro_results"
    root_cov = "/home/wanghaichi/repro_linuxs"
    total = 1650
    while True:
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
            print(f"{version} progress: {finished_number} / {parsed_number} / 1650.")
        time.sleep(5)