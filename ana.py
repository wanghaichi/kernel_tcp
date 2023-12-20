import json
import pickle

from pathlib import Path

from liebes.CiObjects import CIObj, Build, TestCase
import Levenshtein
from liebes.test_path_mapping import mapping_config


def collect_path(root_path: Path, cur_path: Path):
    if cur_path.is_file():
        if cur_path.suffix in [".c", ".sh"]:
            p = str(cur_path.relative_to(root_path))
            k = p.replace(".c", "").replace(".sh", "_sh").replace("/", "_")
            return [(k, p)]
        return []
    res = []
    for s in cur_path.iterdir():
        res.extend(collect_path(root_path, s))
    return res


if __name__ == "__main__":

    total_set = set()
    data_path = Path("ciobjs/kernelci")
    for s in data_path.iterdir():
        if (s / "not_mapped.pkl").exists():
            not_map_set = pickle.load((s / "not_mapped.pkl").open("rb"))

            for item in not_map_set:
                flag = False
                for k in mapping_config.keys():
                    if item in k or k in item:
                        flag = True
                if not flag:
                    total_set.add(item)
    for i in total_set:
        print(i)
    print(len(total_set))
    exit(-1)


    temp = []

    for i in a:
        flag = False
        for k in mapping_config.keys():
            if i in k or k in i:
                flag = True
        if not flag:
            temp.append(i)
    m = pickle.load(Path("kselftests_path.pkl").open("rb"))
    s = set()
    for i in temp:
        flag = False
        for k in m.keys():
            if k in i or i in k:
                flag = True
        if not flag:
            s.add(i)
    res = []
    for i in s:
        min_distance = float('inf')
        most_similar = ""
        for k in m.keys():
            distance = Levenshtein.distance(i, k.replace("test_cases_selftests_", ""))
            if distance < min_distance:
                min_distance = distance
                most_similar = k
        res.append((i, m[most_similar]))
    sorted_list = sorted(res, key=lambda x: x[0])
    for k, v in sorted_list:
        print(f"\"{k}\": \"{v}\",")
    exit(-1)
    # r = collect_path(Path("./"), Path("test_cases/selftests"))
    # m = {}
    # for k, v in r:
    #     m[k] = v
    # pickle.dump(m, Path("kselftests_path.pkl").open("wb"))

    # print(f"\"{k}\": \"{v}\",")
    # for i in a:
    #     for k in b.keys():
    #         if i in k:
    #             print(f"\"{i}\": \"{b[i]}\",")
    exit(-1)
    r = Path("test_cases/selftests")
    res = []
    for s in r.iterdir():
        if not s.is_dir():
            continue
        for sub_path in s.iterdir():
            if sub_path.is_dir():
                continue
            if sub_path.suffix in [".c", ".sh"]:
                n = sub_path.name.replace(".c", "")
                n = n.replace(".sh", "_sh")

                res.append(f"{s.name}\"{n}\": \"{sub_path.relative_to(Path('test_cases'))}\"")

    print(res)
    exit(-1)

    data_path = Path("ciobjs/kernelci")
    for s in data_path.iterdir():
        if (s / "not_mapped.pkl").exists():
            not_map_set = pickle.load((s / "not_mapped.pkl").open("rb"))
            for item in not_map_set:
                print(item)

    # dataset_path = Path("dataset/total")
    # build_path = dataset_path / "tests"
    # builds_list = []
    # skip = 0
    #
    #
    # num_file = 0
    # for b in build_path.iterdir():
    #     if not b.suffix == ".json":
    #         continue
    #     num_file += 1
    #
    # num_cnt = 0
    # for b in build_path.iterdir():
    #     if not b.suffix == ".json":
    #         continue
    #     if Path(f"cache/{b.name}.pkl").exists():
    #         continue
    #     checkouts_map = []
    #     failed = 0
    #     total = 0
    #     text = b.read_text().split("\n")
    #     for line in text:
    #         line = line.strip()
    #         if len(line) == 0:
    #             continue
    #         d = json.loads(line)
    #         ci_obj = TestCase.load_from_json2(d)
    #         if ci_obj is None:
    #             failed += 1
    #             total += 1
    #             # print(d)
    #             continue
    #         checkouts_map.append(ci_obj)
    #         total += 1
    #     print(f"{b.name}, {failed} / {total}, {num_cnt} / {num_file} done.")
    #     num_cnt += 1
    #
    #     pickle.dump(checkouts_map, Path(f"cache/{b.name}.pkl").open("wb"))
    # print("DONE")
