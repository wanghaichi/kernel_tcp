import argparse
import json
import multiprocessing
# import multiprocessing
import pickle
from datetime import datetime
from typing import Dict

from sympy import covering_product
from tqdm import tqdm

from liebes.CiObjects import *
from liebes.EHelper import EHelper
from liebes.GitHelper import GitHelper
from liebes.analysis import CIAnalysis
from liebes.coverage_ana import CoverageHelper
from liebes.ir_model import *
from liebes.sql_helper import SQLHelper
from liebes.tokenizer import *
import numpy as np
from concurrent.futures import ThreadPoolExecutor, as_completed

from sklearn import svm
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import StandardScaler, MinMaxScaler


class MLTcpTestCase:
    def __init__(self):
        self.is_failed: bool = False
        self.path: str = ""
        self.file_path: str = ""
        self.file_type: TestCaseType = TestCaseType.UNKNOWN

        self.score_coverage: int = 0
        self.test_path_similarity: float = 0
        self.test_content_similarity: float = 0

        self.history_score: float = 0
        self.age_score: int = 0

    def to_dict(self):
        """Convert MLTcpTestCase object into a dictionary for JSON serialization."""
        return {
            "is_failed": self.is_failed,
            "path": self.path,
            "file_path": self.file_path,
            "file_type": self.file_type.value,
            "score_coverage": self.score_coverage,
            "test_path_similarity": self.test_path_similarity,
            "test_content_similarity": self.test_content_similarity,
            "history_score": self.history_score,
            "age_score": self.age_score
        }

    @staticmethod
    def from_dict(data: dict):
        """Create an MLTcpTestCase instance from a dictionary."""
        test_case = MLTcpTestCase()
        test_case.is_failed = data.get("is_failed", False)
        test_case.path = data.get("path", "")
        test_case.file_path = data.get("file_path", "")
        test_case.file_type = TestCaseType(data.get("file_type", 0))
        test_case.score_coverage = data.get("score_coverage", 0)
        test_case.test_path_similarity = data.get("test_path_similarity", 0)
        test_case.test_content_similarity = data.get("test_content_similarity", 0)
        test_case.history_score = data.get("history_score", 0)
        test_case.age_score = data.get("age_score", 0)
        return test_case
    # def __init__(self):
    #     self.is_failed = False
    #     self.path = ""
    #     self.file_path = ""
    #     self.file_type = 0
    #     self.score_coverage = 0
    #     self.test_path_similarity = 0
    #     self.test_content_similarity = 0
    #     self.history_score = 0
    #     self.age_score = 0
    #     pass


class MLTcpVersion:
    def __init__(self):
        self.coverage_version: str = ""
        self.version: str = ""
        self.test_cases: List[MLTcpTestCase] = []
        self.his_map: Dict[str, float] = {}
        self.id: int = 0

    def to_dict(self):
        """Convert MLTcpVersion object into a dictionary for JSON serialization."""
        return {
            "coverage_version": self.coverage_version,
            "version": self.version,
            "test_cases": [test_case.to_dict() for test_case in self.test_cases],
            "his_map": self.his_map,
            "id": self.id
        }

    @staticmethod
    def from_dict(data: dict):
        """Create an MLTcpVersion instance from a dictionary (reverse of to_dict)."""
        version = MLTcpVersion()
        version.coverage_version = data.get("coverage_version", "")
        version.version = data.get("version", "")
        version.test_cases = [MLTcpTestCase.from_dict(test_case) for test_case in data.get("test_cases", [])]
        version.his_map = data.get("his_map", {})
        version.id = data.get("id", 0)
        return version

    # def __init__(self):
    #     self.coverage_version = ""
    #     self.version = ""
    #     self.test_cases = []
    #     self.his_map = {}
    #     self.id = 0

    def calculate_coverage_score(self):
        cov_info = CoverageHelper(self.coverage_version)
        cov_info.load_coverage4checkout()
        changed_files = git_helper.get_changed_files(m.coverage_version, m.version)
        scores = {}
        for k, v in cov_info.coverage_info.items():
            total_covered = 0
            for cf in changed_files:
                if cf in v.keys():
                    total_covered += len(v[cf])
            scores[k] = total_covered
        for tc in self.test_cases:
            if cov_info.get_coverage_name(tc.path) in scores.keys():
                tc.score_coverage = scores[cov_info.get_coverage_name(tc.path)]
        pass

    def calculate_test_similarity(self):
        tokenizer = AstTokenizer()
        changed_files = git_helper.get_changed_files(m.coverage_version, m.version)
        changed_tokens = []
        changed_paths = []
        for f in changed_files:
            contents = git_helper.get_file_content_by_commit(self.version, f)
            if contents is None:
                continue
            if Path(f).suffix == ".c":
                changed_tokens.extend(tokenizer.get_tokens_c(contents))
            elif Path(f).suffix == ".sh":
                changed_tokens.extend(tokenizer.get_tokens_sh(contents))
            path_tokens = f.lower().replace("/", " ").replace(".", " ").replace("_", " ").split(" ")
            changed_paths.extend(path_tokens)
        changed_tokens_str = " ".join(changed_tokens)
        changed_paths_str = " ".join(changed_paths)
        tc_tokens = []
        path_tokens = []
        for tc in self.test_cases:
            if not Path(tc.file_path).exists():
                tc_tokens.append("")
                path_tokens.append(tc.file_path.lower().replace("/", " ").replace(".", " ").replace("_", " "))
                continue
            tokens = tokenizer.get_tokens(Path(tc.file_path).read_text(errors='ignore'), tc.file_type)
            tc_tokens.append(" ".join(tokens))
            path_tokens.append(tc.file_path.lower().replace("/", " ").replace(".", " ").replace("_", " "))
        model = TfIdfModel()
        # try:
        similarity = model.get_similarity(tc_tokens, [changed_tokens_str])
        # except Exception as e:
        #     print(e)
        #     print(self.version)
        #     print(tc_tokens)
        #     # print(changed_tokens_str)
        #     exit(-1)
        #     print(e)
        #     print(tc_tokens)
        #     print(changed_tokens_str)
        #     exit(-1)
        for tc, s in zip(self.test_cases, similarity):
            tc.test_content_similarity = s[0]
        similarity = model.get_similarity(path_tokens, [changed_paths_str])
        for tc, s in zip(self.test_cases, similarity):
            tc.test_path_similarity = s[0]
        # for tc in self.test_cases:
        #     print(tc.test_path_similarity, tc.test_content_similarity)

    def calculate_history_score(self, pre_his_map: Dict[str, float]):
        alpha = 0.9
        for tc in self.test_cases:
            pre_score = 0 if tc.path not in pre_his_map.keys() else pre_his_map[tc.path]
            tc.history_score = 1 if tc.is_failed else 0
            tc.history_score = alpha * tc.history_score + (1 - alpha) * pre_score
            self.his_map[tc.path] = tc.history_score
        for k in pre_his_map.keys():
            if k not in self.his_map.keys():
                self.his_map[k] = (1 - alpha) * pre_his_map[k]
        pass

    def calculate_age_score(self, pre_his_map: Dict[str, float]):
        for tc in self.test_cases:
            tc.age_score = 0 if tc.path not in pre_his_map.keys() else 1
        pass

    # def calculate_all(self):
    #     self.calculate_coverage_score()
    #     self.calculate_test_similarity()
    #     self.calculate_history_score()
    #     self.calculate_age_score()


class MLTcp:
    def __init__(self):
        self.versions: List[MLTcpVersion] = []


    def to_dict(self):
        """Convert MLTcp object into a dictionary for JSON serialization."""
        return {
            "versions": [version.to_dict() for version in self.versions]
        }

    def get_all_test_cases(self):
        test_cases = []
        for version in self.versions:
            test_cases.extend(version.test_cases)
        return test_cases

    @staticmethod
    def load_version_from_file(file_path: str):
        data = json.load(Path(file_path).open("r"))
        version = MLTcpVersion.from_dict(data)
        return version

    def sort_by_version(self):
        self.versions.sort(key=lambda x: x.id)
        pass
    # def load_version_from_file(self, file_path: str) -> MLTcpVersion:
    #     """Load the MLTcp object from a JSON file."""
    #     with open(file_path, "r") as file:
    #         data = json.load(file)
    #         self.versions = [MLTcpVersion(**version) for version in data["versions"]]


# Define a function to calculate scores
def calculate_scores(m: MLTcpVersion):
    m.calculate_coverage_score()
    m.calculate_test_similarity()
    text = dump_ml_tcp_to_json(m)
    Path(f"mlcache/{m.version}.json").write_text(text)
    # print(m.version)
    # for i in range(5):
    #     t = m.test_cases[i]
    #     print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    # pickle.dump(m, open(f"/home/wanghaichi/kernelTCP/mlcache/{m.version}.pkl", "wb"))
    # print("after")
    # nm = pickle.load(open(f"/home/wanghaichi/kernelTCP/mlcache/{m.version}.pkl", "rb"))
    # for i in range(5):
    #     t = nm.test_cases[i]
    #     print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    return m
    # print(m.version)
    # for i in range(5):
    #     t = m.test_cases[i]
    #     print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    # return m


# Function to serialize MLTcp object into JSON
def dump_ml_tcp_to_json(ml_tcp: MLTcpVersion) -> str:
    return json.dumps(ml_tcp.to_dict(), indent=4)


def train_model(mltcp: MLTcp):
    split_index = 30
    test_cases = []
    for v in mltcp.versions[:split_index]:
        test_cases.extend(v.test_cases)

    # Step 1: Extract features and labels
    X = []  # Feature matrix
    y = []  # Labels

    for test_case in test_cases:
        features = [
            test_case.score_coverage,
            test_case.test_path_similarity,
            test_case.test_content_similarity,
            # test_case.history_score,
            test_case.age_score
        ]
        X.append(features)
        y.append(1 if test_case.is_failed else 0)

    # for i in range(len(y)):
    #     if y[i] == 1:
    #         print(X[i])
    # exit(-1)

    X = np.array(X)  # Convert to numpy array for training
    y = np.array(y)

    # Step 2: Normalize features
    scaler = StandardScaler()  # For features that are continuous but not bounded
    X[:, 1:] = scaler.fit_transform(X[:, 1:])  # Standard scale features that are already between 0-1

    # Normalize score_coverage to [0, 1] using MinMaxScaler
    score_scaler = MinMaxScaler()
    X[:, 0:1] = score_scaler.fit_transform(X[:, 0:1])

    # Step 3: Split data into training and testing sets

    # Step 4: Train the SVM model
    model = svm.SVC(kernel='linear', probability=True )  # You can choose 'linear', 'poly', 'rbf', etc.
    model.fit(X, y)

    for v in mltcp.versions[split_index:]:
        X_test = []  # Feature matrix for test cases in validation set
        probabilities = []  # To store probabilities

        faults = []
        for i in range(len(v.test_cases)):
            test_case = v.test_cases[i]
            features = [
                test_case.score_coverage,
                test_case.test_path_similarity,
                test_case.test_content_similarity,
                # test_case.history_score,
                test_case.age_score
            ]
            X_test.append(features)
            if test_case.is_failed:
                faults.append(i)

        X_test = np.array(X_test)
        X_test[:, 1:] = scaler.transform(X_test[:, 1:])  # Standard scale features that are already between 0-1
        X_test[:, 0:1] = score_scaler.transform(X_test[:, 0:1])  # Normalize score_coverage to [0, 1]

        # Step 5: Predict the probabilities of failure for each test case in the validation set
        predicted_probs = model.predict_proba(X_test)[:, 1]  # Probabilities of class 1 (failure)

        # Step 6: Sort the test cases based on predicted probabilities (descending order)
        sorted_indices = np.argsort(predicted_probs)[::-1]  # Sort indices in descending order
        apfd = EHelper().APFD(faults, sorted_indices.tolist())
        print(f"APFD for version {v.version}: {apfd:.10f}")
        # calculate the score for tc in X
        # # Step 2: Normalize features
        # scaler = StandardScaler()  # For features that are continuous but not bounded
        # X[:, 1:] = scaler.fit_transform(X[:, 1:])  # Standard scale features that are already between 0-1
        #
        # # Normalize score_coverage to [0, 1] using MinMaxScaler
        # score_scaler = MinMaxScaler()
        # X[:, 0:1] = score_scaler.fit_transform(X[:, 0:1])


    # # # Step 5: Evaluate the model
    # # accuracy = model.score(X_test, y_test)
    # # print(f"Accuracy: {accuracy * 100:.2f}%")
    #
    # # Step 6: Predict the probability of failure (chance of failure)
    # x_new = np.array([0, 0.1, 0.2, 0, 0])  # Example features for a new test case
    #
    # # Normalize the new data point in the same way as training data
    # x_new[0:1] = score_scaler.transform(x_new[0:1].reshape(-1, 1))  # Normalize score_coverage
    # x_new[1:] = scaler.transform(x_new[1:].reshape(1, -1))  # Standard scale other features
    #
    # # Predict the probability of failure
    # probability = model.predict_proba([x_new])[0, 1]  # Probability of class 1 (failure)
    # print(f"Probability of failure for the new test case: {probability:.2f}")
    # # Step 6: Use the model to make predictions
    # predictions = model.predict(X_test)
    # print("Predictions:", predisctions)
    # return model, score_scaler, scaler

if __name__ == "__main__":

    # mltcp = pickle.load(open("mltcp.pkl", "rb"))
    # print(len(mltcp.versions))
    # for v in mltcp.versions:
    #     for t in v.test_cases:
    #         if t.is_failed:
    #             print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity, t.history_score,
    #                   t.age_score)
    # exit(-1)
    # # Prepare the data for the model
    # X = []  # Input features (the five scores)
    # y = []  # Labels (is_failed)
    # for v in mltcp.versions:
    #     for test_case in v.test_cases:
    #         X.append([test_case.score_coverage, test_case.test_path_similarity, test_case.test_content_similarity,
    #                   test_case.history_score, test_case.age_score])
    #         y.append(1 if test_case.is_failed else 0)
    #
    # X = np.array(X)
    # y = np.array(y)
    #
    # # Split data into training and testing sets
    # X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.3, random_state=42)
    #
    # # Initialize and train the SVM classifier
    # svm = SVC(kernel='linear')  # You can try other kernels like 'rbf' or 'poly'
    # svm.fit(X_train, y_train)
    #
    # # Make predictions on the test set
    # y_pred = svm.predict(X_test)
    #
    # # Evaluate the model
    # print("Classification Report:")
    # print(classification_report(y_test, y_pred))
    #
    # exit(-1)

    git_helper = GitHelper("/home/wanghaichi/linux")

    pre_versions = ['35fab9271b7e6d193b47005c4d07369714db4fd1', '33afd4b76393627477e878b3b195d606e585d816',
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

    versions = ['91ec4b0d11fe115581ce2835300558802ce55e6c', '1ae78a14516b9372e4c90a89ac21b259339a3a3a',
                '58390c8ce1bddb6c623f62e7ed36383e7fa5c02f', '671e148d079f4d4eca0a98f7dadf1fe69d856374',
                'd295b66a7b66ed504a827b58876ad9ea48c0f4a8', '533c54547153d46c0bf99ac0e396bed71f760c03',
                'e338142b39cf40155054f95daa28d210d2ee1b2d', '8d15d5e1851b1bbb9cd3289b84c7f32399e06ac5',
                '1639fae5132bc8a904af28d97cea0bedb3af802e', '2214170caabbff673935eb046a7edf4621213931',
                '3a8a670eeeaa40d87bd38a587438952741980c18', '6cdbb0907a3c562723455e351c940037bdec9b7a',
                'a901a3568fd26ca9c4a82d8bc5ed5b3ed844d451', '03275585cabd0240944f19f33d7584a1b099a3a8',
                '3290badd1bb8c9ea91db5c0b2e1a635178119856', '7fcd473a6455450428795d20db7afd2691c92336',
                '06c2afb862f9da8dc5efa4b6076a0e48c3fbaaa5', 'fdf0eaf11452d72945af31804e2a1048ee1b574c',
                '18b44bc5a67275641fb26f2c54ba7eef80ac5950', 'ffabf7c731765da3dbfaffa4ed58b51ae9c2e650',
                '251a94f1f66e909d75a774ac474a63bd9bc38382', 'cacc6e22932f373a91d7be55a9b992dc77f4c59b',
                '374a7f47bf401441edff0a64465e61326bf70a82', '25aa0bebba72b318e71fe205bfd1236550cc9534',
                'ae545c3283dc673f7e748065efa46ba95f678ef2', '4c75bf7e4a0e5472bd8f0bf0a4a418ac717a9b70',
                'b320441c04c9bea76cbee1196ae55c20288fd7a6', '28f20a19294da7df158dfca259d0e2b5866baaf9',
                '6383cb42ac01e6fb9ef6a035a2288786e61bdddf', '36534782b584389afd281f326421a35dcecde1ec',
                '1c59d383390f970b891b503b7f79b63a02db2ec5', 'b96a3e9142fdf346b05b20e867b4f0dfca119e96',
                '53ea7f624fb91074c2f9458832ed74975ee5d64c', 'ef2a0b7cdbc5b84f7b3f6573b7687e72bede0964',
                '4debf77169ee459c46ec70e13dc503bc25efd7d2', 'e0152e7481c6c63764d6ea8ee41af5cf9dfac5e9',
                '92901222f83d988617aee37680cb29e1a743b5e4', '3f86ed6ec0b390c033eae7f9c487a3fea268e027',
                '65d6e954e37872fd9afb5ef3fc0481bb3c2f20f4', '744a759492b5c57ff24a6e8aabe47b17ad8ee964',
                'dd1386dd3c4f4bc55456c88180f9f39697bb95c0', '2a5a4326e58339a26cd1510259e7310b8c0980ff',
                '535a265d7f0dd50d8c3a4f8b4f3a452d56bd160f', 'aed8aee11130a954356200afa3f1b8753e8a9482',
                'ad8a69f361b9b9a0272ed66f04e6060b736d2788', '8018e02a87031a5e8afcbd9d35133edd520076bb',
                '830380e3178a103d4401689021eadddadbb93d6d', '84186fcb834ecc55604efaf383e17e6b5e9baa50',
                '750b95887e567848ac2c851dae47922cac6db946', 'be3ca57cfb777ad820c6659d52e60bbdd36bf5ff',
                '90450a06162e6c71ab813ea22a83196fe7cff4bc']

    all_versions = versions
    mltcp = MLTcp()

    for v in all_versions:
        m = MLTcp.load_version_from_file(f"mlcache/{v}.json")
        mltcp.versions.append(m)
    mltcp.versions = mltcp.versions[1:]
    # print(len([x for x in mltcp.versions[0].test_cases if x.is_failed]))
    # print(len([x for x in mltcp.get_all_test_cases() if x.is_failed]))
    # print(len(mltcp.get_all_test_cases()))
    # for t in mltcp.get_all_test_cases():
    #     if t.is_failed:
    # exit(-1)
    #
    #
    for i in tqdm(range(len(mltcp.versions))):
        m = mltcp.versions[i]
        # m.calculate_coverage_score()
        # m.calculate_test_similarity()
        if i == 0:
            m.calculate_history_score({})
            m.calculate_age_score({})
        else:
            m.calculate_history_score(mltcp.versions[i - 1].his_map)
            m.calculate_age_score(mltcp.versions[i - 1].his_map)

    print("start to train svm model ")
    train_model(mltcp)

    exit(-1)

    # all_versions = versions[:4]
    all_versions = versions
    # all_versions = pre_versions + versions
    sql_helper = SQLHelper()
    # checkouts = sql_helper.session.query(DBCheckout).all()
    checkouts = sql_helper.session.query(DBCheckout).filter(DBCheckout.git_sha.in_(all_versions)).all()
    cia = CIAnalysis()
    for ch in tqdm(checkouts):
        cia.ci_objs.append(Checkout(ch))
    cia.reorder()
    cia.set_parallel_number(40)
    cia.filter_job("COMBINE_SAME_CASE")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    cia.filter_job("COMBINE_SAME_CONFIG")
    cia.filter_job("CHOOSE_ONE_BUILD")
    cia.filter_job("FILTER_FAIL_CASES_IN_LAST_VERSION")
    cia.filter_job("FILTER_SMALL_BRANCH", minimal_testcases=20)
    # cia.statistic_data()
    # c = 0
    # for t in cia.get_all_testcases():
    #     if t.is_failed():
    #         c += 1
    # print(c)
    # print(len(cia.get_all_testcases()))
    # print("done")
    #
    # exit(-1)

    mltcp = MLTcp()
    # for a, b in zip(pre_versions, versions):
    #     m = MLTcpVersion()
    #     m.coverage_version = a
    #     m.version = b
    #     mltcps.append(m)

    for i in range(len(cia.ci_objs)):
        # print(len(cia.ci_objs[i].get_all_testcases()))
        # print(len([x for x in cia.ci_objs[i].get_all_testcases() if x.is_failed()]))
        m = MLTcpVersion()
        m.coverage_version = pre_versions[i]
        m.version = cia.ci_objs[i].instance.git_sha
        m.id = i
        for tc in cia.ci_objs[i].get_all_testcases():
            if tc.type != TestCaseType.C and tc.type != TestCaseType.SH:
                continue
            t = MLTcpTestCase()
            t.path = tc.get_testcase_name()
            t.is_failed = tc.is_failed()
            t.file_path = tc.file_path
            t.file_type = tc.type
            m.test_cases.append(t)
        mltcp.versions.append(m)
        # print(len(mltcp.versions[i].test_cases))
        # print(len([x for x in mltcp.versions[i].test_cases if x.is_failed]))
    # exit(-1)
    logger.info("Start calculating coverage scores")

    # with ThreadPoolExecutor(max_workers=4) as executor:
    #     futures = []
    #
    #     # Submit the calculate_coverage_score task for each test case
    #     for m in mltcp.versions:
    #         futures.append(executor.submit(calculate_scores, m))
    #     res = []
    #     # Wait for all tasks to complete and handle results if necessary
    #     for future in as_completed(futures):
    #         res.append(future.result())  # You can handle the result if needed, e.g., logging or updating
    #     for m in res:
    #         print(m.version)
    #         for i in range(5):
    #             t = m.test_cases[i]
    #             print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)

    # exit(-1)
    #
    # with multiprocessing.Manager() as manager:
    #     shared_versions = manager.list()  # Create a shared list for modified versions
    #     with multiprocessing.Pool(processes=4) as pool:
    #         results = pool.map(calculate_scores, mltcp.versions)
    #     # for r in shared_versions:
    #     #     print(r.version)
    #     #     for i in range(5):
    #     #         t = r.test_cases[i]
    #     #         print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)

    # exit(-1)
    #
    # # Create a pool of workers
    with multiprocessing.Pool(processes=8) as pool:
        # Map the task function to the inputs
        pool.map(calculate_scores, mltcp.versions)
        # for r in results:
        #     print(r.version)
        #     for i in range(5):
        #         t = r.test_cases[i]
        #         print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    # new_versions = []
    # for m in mltcp.versions:
    #     new_versions.append(pickle.load(open(f"/home/wanghaichi/kernelTCP/mlcache/{m.version}.pkl", "rb")))
    print("done")
    # for v in new_versions:
    #     for i in range(5):
    #         t = v.test_cases[i]
    #         print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    exit(-1)
    for v in results:

        for t in v.test_cases:
            if t.score_coverage > 0 or t.test_path_similarity > 0:
                print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)
    exit(-1)
    # if t.is_failed:
    #     print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity)

    # # Use ProcessPoolExecutor for parallel processing
    # with ProcessPoolExecutor(max_workers=51) as executor:
    #     futures = {executor.submit(calculate_scores, mltcp.versions[i]): i for i in range(len(mltcp.versions))}
    #     for future in tqdm(as_completed(futures), total=len(futures)):
    #         m = future.result()
    #         new_versions.append(m)

    # Sort the list by the 'id' attribute in ascending order
    sorted_versions = sorted(results, key=lambda x: x.id)
    mltcp.versions = sorted_versions

    logger.info("Start calculating history and age scores")

    for i in tqdm(range(len(mltcp.versions))):
        m = mltcp.versions[i]
        # m.calculate_coverage_score()
        # m.calculate_test_similarity()
        if i == 0:
            m.calculate_history_score({})
            m.calculate_age_score({})
        else:
            m.calculate_history_score(mltcp.versions[i - 1].his_map)
            m.calculate_age_score(mltcp.versions[i - 1].his_map)
    print(len(mltcp.versions))
    for v in mltcp.versions:
        for t in v.test_cases:
            if t.is_failed:
                print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity, t.history_score,
                      t.age_score)
    pickle.dump(mltcp, open("mltcp1.pkl", "wb"))

    print("dump done")

    mltcp = pickle.load(open("mltcp1.pkl", "rb"))
    for v in mltcp.versions:
        for t in v.test_cases:
            if t.is_failed:
                print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity, t.history_score,
                      t.age_score)
    print("done")
    # i = 0
    # for m in mltcps:
    #     for t in m.test_cases:
    #         print(t.path, t.score_coverage, t.test_path_similarity, t.test_content_similarity, t.history_score,
    #               t.age_score)
    #         i += 1
    #         if i >= 500:
    #             exit(-1)

    # print(changed_files[:10])
    #
    # print(total_covered)
    # exit(-1)
    # cov_info.
    #

    pass
