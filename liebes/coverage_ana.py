import pickle
from pathlib import Path

from tqdm import tqdm

from liebes.ci_logger import logger
import random
import copy
from liebes.tcp_approach.metric_manager import DistanceMetric


class CoverageHelper:
    def __init__(self, kernel_version):
        self.kernel_version = kernel_version
        self.test_case_name = None
        self.coverage_info = {}
        pass

    def load_coverage_info(self, file_path):
        info_content = Path(file_path).read_text(encoding='utf-8', errors='ignore')
        if info_content.strip() == "":
            Path(file_path).unlink()
            return
        self.extract(info_content)

    def remove_common_coverage(self):
        # this approach will remove all same coverage that is covered by all test cases
        common_coverage = {}
        for k, v in self.coverage_info.items():
            for file_path, lines in v.items():
                common_coverage[file_path] = lines
            break
        for _, v in self.coverage_info.items():
            for file_path, lines in v.items():
                if file_path not in common_coverage.keys():
                    continue
                common_coverage[file_path] = list(set(common_coverage[file_path]).intersection(set(lines)))
        common_coverage = {k: v for k, v in common_coverage.items() if len(v) > 0}
        # remove common coverage from all the test cases
        for _, v in self.coverage_info.items():
            for file_path, lines in v.items():
                if file_path not in common_coverage.keys():
                    continue
                v[file_path] = list(set(lines) - set(common_coverage[file_path]))
        # done

    def extract(self, raw_coverage_info):
        file_path = None
        tc_name = None
        cov_map = {}
        for line in raw_coverage_info.split("\n"):
            if (tc_name is not None) and (tc_name in self.coverage_info.keys()):
                logger.debug(f"test case {tc_name} already exists in coverage info, skip the rest.")
                return
            if line.startswith("TN") and tc_name is None:
                temp = line.split(":")
                tc_name = temp[1]
            if line.startswith("SF"):
                file_path = line.split(":")[1]
                file_path = file_path.split(self.kernel_version)
                file_path = file_path[1]
                file_path = file_path.removeprefix("/")
                cov_map[file_path] = []
            if line.startswith("DA"):
                if file_path is None:
                    continue
                temp = line.split(":")
                temp = temp[1].split(",")
                if len(temp) < 2:
                    logger.info(f"error line: {line}")
                    continue
                # judge if temp[1] is int
                if temp[1].startswith("-"):
                    temp[1] = temp[1][1:]
                if not temp[1].isdigit():
                    logger.info(f"error line: {line}")
                    continue
                if int(temp[1]) > 0:
                    cov_map[file_path].append(int(temp[0]))
            if line == "end_of_record":
                file_path = None
        if tc_name is None or tc_name == "":
            idx = 0
            tc_name = f"unknown_{idx}"
            while tc_name in self.coverage_info.keys():
                idx += 1
                tc_name = f"unknown_{idx}"
            logger.error(f"no test case name found in coverage info, use {tc_name} instead.")
        self.coverage_info[tc_name] = cov_map
        pass

    def compare_two_coverages(self, tc_name1, tc_name2):
        if tc_name1 not in self.coverage_info.keys() or tc_name2 not in self.coverage_info.keys():
            logger.error("test case not found in coverage info")
            return None
        cov1 = self.coverage_info[tc_name1]
        cov2 = self.coverage_info[tc_name2]

        all_keys = set(cov1.keys()).union(set(cov2.keys()))
        # lines covered by a but not b
        a_b_res = {}
        # lines covered by b but not a
        b_a_res = {}

        for file_path in all_keys:
            a_covered = set()
            b_covered = set()
            if file_path in cov1.keys():
                a_covered = set(cov1[file_path])
            if file_path in cov2.keys():
                b_covered = set(cov2[file_path])
            a_b_res[file_path] = list((a_covered - b_covered))
            b_a_res[file_path] = list((b_covered - a_covered))
        a_b_res = {k: v for k, v in a_b_res.items() if len(v) > 0}
        b_a_res = {k: v for k, v in b_a_res.items() if len(v) > 0}
        return [a_b_res, b_a_res]

    def total_cov_generator(self):
        file_list = []
        cov_count = []
        for k, v in self.coverage_info.items():
            file_list.append(k)
            cnt = 0
            for _, lines in v.items():
                cnt += len(lines)
            cov_count.append(cnt)
        # print(file_list)
        # print(cov_count)
        sorted_file_list = [(x, cnt) for cnt, x in
                            sorted(zip(cov_count, file_list), key=lambda pair: pair[0], reverse=True)]
        for f, cnt in sorted_file_list:
            yield f, cnt

    def get_additional_cov(self, base_cov, additional_cov):
        res = 0
        for k, v in additional_cov.items():
            if k not in base_cov.keys():
                res += len(v)
            else:
                diff = len(set(v) - set(base_cov[k]))
                res += diff
        return res

    def combine_cov(self, base_cov, additional_cov):
        for k, v in additional_cov.items():
            if k not in base_cov.keys():
                base_cov[k] = copy.deepcopy(v)
            else:
                base_cov[k] = list(set(base_cov[k]).union(set(v)))
        return base_cov

    def additional_cov_generator(self):
        # random choose one, or select the one with the highest coverage

        candidate = [x for x in self.coverage_info.keys()]
        # random
        # r_idx = random.randint(0, len(candidate) - 1)
        # first_one = candidate[r_idx]
        # candidate.pop(r_idx)
        # file_list = [first_one]
        # base_cov = copy.deepcopy(self.coverage_info[first_one])
        # use the one with the highest coverage
        file_list = []
        base_cov = {}
        while len(candidate) > 0:
            max_cov_idx = -1
            max_cov_cnt = -1
            for i in range(len(candidate)):
                increment_cov = self.get_additional_cov(base_cov, self.coverage_info[candidate[i]])
                if increment_cov > max_cov_cnt:
                    max_cov_cnt = increment_cov
                    max_cov_idx = i
            choose_one = candidate.pop(max_cov_idx)
            base_cov = self.combine_cov(base_cov, self.coverage_info[choose_one])
            yield choose_one, max_cov_cnt
            # file_list.append((choose_one, max_cov_cnt))
        # for f, cnt in file_list:
        #     yield f, cnt

    def load_coverage4checkout(self):
        checkout_path = Path("/home/wanghaichi/repro_linuxs/") / self.kernel_version
        if not checkout_path.exists() or not checkout_path.is_dir():
            logger.error("checkout path not found.")
            return
        previous_cache = checkout_path / "total_coverage.pkl"
        if previous_cache.exists():
            self.coverage_info = pickle.load(previous_cache.open("rb"))
        pr_len = len(self.coverage_info.keys())

        total_number = sum(1 for _ in checkout_path.glob("*.info"))

        # for file in tqdm(checkout_path.glob("*.info"), total=total_number):
        for file in checkout_path.glob("*.info"):
            # if file.name == "x86:ioperm_64_coverage.info":
            #     print("???")
            if file.name.removesuffix(".info") in self.coverage_info.keys():
                logger.debug(f"{file.name} is already in coverage info, skip.")
                continue
            try:
                self.load_coverage_info(file)
            except Exception as e:
                logger.info(f"{file.absolute()} needs to be remove")
                file.unlink()

        self.remove_unknown_keys()
        self.optimize()
        diff = len(self.coverage_info.keys()) - pr_len
        if diff != 0:
            self.remove_common_coverage()
            logger.info(f"loaded {diff} new test cases coverage.")
            logger.info(f"update coverage cache at {previous_cache.absolute()}.")
            pickle.dump(self.coverage_info, previous_cache.open("wb"))
        logger.info(f"successfully load all coverage info for {self.kernel_version}.")

    def optimize(self):
        # remove the keys that has no covered lines
        keys_to_remove = {}
        for k, v in self.coverage_info.items():
            keys_to_remove[k] = []
            for f, cov_lines in v.items():
                if len(cov_lines) == 0:
                    keys_to_remove[k].append(f)
        for k, v in keys_to_remove.items():
            for f in v:
                self.coverage_info[k].pop(f)

    def remove_unknown_keys(self):
        temp = {}
        for k, v in self.coverage_info.items():
            if k.startswith("unknown"):
                continue
            temp[k] = v
        self.coverage_info = temp

    @staticmethod
    def get_coverage_name(tc_name):
        cov_name = tc_name + "_coverage"
        cov_name = cov_name.replace("-", "_")
        cov_name = cov_name.replace(":", "_")
        cov_name = cov_name.replace(".", "_")
        return cov_name

    def arp_generator(self):
        dm = DistanceMetric()

        # 1. convert all coverage info sets
        coverage_sets = {}
        candidates = []
        for tc_name, cov_i in self.coverage_info.items():
            candidates.append(tc_name)
            coverage_sets[tc_name] = set()
            for file_name, cov_lines in cov_i.items():
                for l in cov_lines:
                    coverage_sets[tc_name].add(file_name + ":" + str(l))

        # generate all jaccard score
        jaccard_scores = {}
        if Path(f"cov_jaccard_{self.kernel_version}.pkl").exists():
            jaccard_scores = pickle.load(Path(f"cov_jaccard_{self.kernel_version}.pkl").open("rb"))
        else:
            print("not found!!!")
            exit(-1)

        # if self.kernel_version not in jaccard_scores:
        #     jaccard_scores[self.kernel_version] = {}
        # updated = False
        # total = len(candidates) * len(candidates)
        # cur = 0

        # for tc_name1 in candidates:
        #     for tc_name2 in candidates:
        #         cur += 1
        #         # if cur % 10000 == 0 or cur == total:
        #         #     print(f"{cur} / {total} {self.kernel_version}")
        #         if tc_name1 == tc_name2:
        #             continue
        #         if (tc_name1 + "_" + tc_name2) in jaccard_scores[self.kernel_version].keys():
        #             continue
        #         score = dm.jaccard_distance_function(coverage_sets[tc_name1], coverage_sets[tc_name2])
        #         jaccard_scores[self.kernel_version][tc_name1 + "_" + tc_name2] = score
        #         jaccard_scores[self.kernel_version][tc_name2 + "_" + tc_name1] = score
        #         updated = True
        # if updated:
        #     pickle.dump(jaccard_scores, Path(f"cov_jaccard_{self.kernel_version}.pkl").open("wb"))
        already_sorted = []
        # 2 select a random one as the first one
        first_one = random.randint(0, len(candidates) - 1)
        already_sorted.append(candidates[first_one])
        yield candidates[first_one], 1.0
        del candidates[first_one]
        # 3. calculate the jaccard score for each run
        while len(candidates) > 0:
            max_score = -1
            max_idx = -1
            for i in range(len(candidates)):
                minimal_score = 100000000
                for already_item in already_sorted:
                    score = jaccard_scores[self.kernel_version][already_item + "_" + candidates[i]]
                    if score < minimal_score:
                        minimal_score = score
                if minimal_score > max_score:
                    max_score = minimal_score
                    max_idx = i
            already_sorted.append(candidates[max_idx])
            yield candidates[max_idx], max_score
            del candidates[max_idx]

    def search_based_generator(self):
        number_of_population = 100
        # number_of_population = 100
        number_of_iteration = 300
        # number_of_iteration = 5
        ratio_of_crossover = 0.8
        ratio_of_mutation = 0.1

        # optimize coverage to speed up.

        # separate the coverage for each file, based on the lines.
        line_of_file = {}
        for tc_name, cov in self.coverage_info.items():
            for file_name, lines in cov.items():
                max_line = max(lines)
                min_line = min(lines)
                if file_name not in line_of_file.keys():
                    line_of_file[file_name] = [min_line, max_line]
                else:
                    previous = line_of_file[file_name]
                    if min_line < previous[0]:
                        previous[0] = min_line
                    if max_line > previous[1]:
                        previous[1] = max_line
        separation_cov_info = {}
        separation_number = 10
        file_name_m = {}
        file_cnt = 0
        for tc_name, cov in self.coverage_info.items():
            separation_cov_info[tc_name] = set()
            for file_name, lines in cov.items():
                if file_name not in file_name_m:
                    file_name_m[file_name] = file_cnt
                    file_cnt += 1
                scope = line_of_file[file_name]
                min_line = scope[0]
                max_line = scope[1]
                distance = (max_line - min_line) // separation_number
                if distance == 0:
                    distance = 1
                for l in lines:
                    cov_number = (l - min_line) // distance
                    separation_cov_info[tc_name].add(f"{file_name_m[file_name]}:{cov_number}")

        candidates = [x for x in self.coverage_info.keys()]

        def stochastic_universal_sampling(populations, number_of_population):
            fitness = []
            apc = []
            for i in range(len(populations)):
                apc.append(average_percentage_coverage(populations[i]))
            positions = sorted(range(len(apc)), key=lambda i: apc[i], reverse=True)
            for i in range(len(positions)):
                fitness.append(1.0 * (positions[i]) / (len(positions) - 1))
            total_fitness = sum(fitness)
            distance = total_fitness / len(fitness)

            start_point = random.uniform(0, distance)
            points = [start_point + i * distance for i in range(number_of_population)]

            selections = []
            current_index = 0
            cumulative_fitness = fitness[0]

            for point in points:
                while cumulative_fitness < point:
                    current_index += 1
                    cumulative_fitness += fitness[current_index]

                selections.append(populations[current_index])
            return selections

        def average_percentage_coverage(ordered_list):
            # for fitness function
            # filename_line-number
            already_covered_items = set()
            first_covered_orders = 0
            for i in range(len(ordered_list)):

                cov_items = separation_cov_info[candidates[i]]
                for cov_i in cov_items:
                    if cov_i not in already_covered_items:
                        first_covered_orders += (i + 1)
                    already_covered_items.add(cov_i)
                # for filename, lines in cov_item.items():
                #     for l in lines:
                #         k = filename + ":" + str(l)
            res = 1.0 - (first_covered_orders / (len(ordered_list) * len(already_covered_items))) + 1.0 / (
                    2 * len(ordered_list))
            return res

        def crossover(list1, list2):
            cross_len = random.randint(1, len(list1) - 1)
            # print(cross_len)
            new_list_1 = []
            new_list_2 = []
            for i in range(cross_len):
                new_list_1.append(list2[i])
            for i in range(len(list1)):
                if list1[i] not in new_list_1:
                    new_list_1.append(list1[i])

            for i in range(cross_len):
                new_list_2.append(list1[i])
            for i in range(len(list2)):
                if list2[i] not in new_list_2:
                    new_list_2.append(list2[i])
            return new_list_1, new_list_2

        def mutation(s):
            new_list = list(s)
            random_pos_1 = random.randint(0, len(s) - 1)
            random_pos_2 = random.randint(0, len(s) - 1)
            temp = new_list[random_pos_1]
            new_list[random_pos_1] = new_list[random_pos_2]
            new_list[random_pos_2] = temp
            return new_list

        def init_population():
            total_items = len(self.coverage_info.keys())
            init_arr = list(range(1, total_items + 1))
            populations = []
            for i in range(number_of_population):
                temp = list(init_arr)
                random.shuffle(temp)
                populations.append(temp)
            return populations

        populations = init_population()

        for _ in tqdm(range(number_of_iteration)):
            new_candidates = []
            for i in range(len(populations)):
                p = random.random()
                if p < ratio_of_crossover:
                    pos_2 = -1
                    while pos_2 == i:
                        pos_2 = random.randint(0, len(populations) - 1)
                    new_1, new_2 = crossover(populations[i], populations[pos_2])
                    new_candidates.append(new_1)
                    new_candidates.append(new_2)
                    continue
                p -= ratio_of_crossover
                if p < ratio_of_mutation:
                    new_1 = mutation(populations[i])
                    new_candidates.append(new_1)
                    continue
                # do nothing
            populations.extend(new_candidates)
            populations = stochastic_universal_sampling(populations, number_of_population)
        max_apc_value = -1
        res = None
        for individual in populations:
            apc = average_percentage_coverage(individual)
            if apc > max_apc_value:
                max_apc_value = apc
                res = individual
        # print(res)
        # print(len(candidates))
        for i in res:
            yield candidates[i-1], -1

        # a = [1, 2, 3, 4, 5, 6]
        # b = [2, 1, 4, 6, 5, 3]
        # print(a)
        # print(b)
        # new_a, new_b = crossover(a, b)
        # print(new_a)
        # print(new_b)
        # n = list(a)
        # for i in range(5):
        #     n = mutation(n)
        #     print(n)

        pass
