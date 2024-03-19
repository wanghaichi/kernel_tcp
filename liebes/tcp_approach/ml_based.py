"""
✅Test case description (natural language) 测试用例开始的注释部分
✅Test case age 从git历史来获取
✅Number of linked requirements  这个应该是该测试用例调用的测试方法
✅Number of linked defects (history)  （历史上fail的次数）
❌Severity of linked defects
❌Test case execution cost (time)
Project-specific features (e.g., market)

ML-Approach：

- SVM
- K-Nearest-Neighbor
- logistic regression
- neural networks
"""
from liebes.tree_parser import CodeAstParser
from sklearn import datasets
from sklearn.model_selection import train_test_split
from sklearn.svm import SVC
from sklearn.metrics import accuracy_score
from sklearn.neighbors import KNeighborsClassifier
from sklearn.linear_model import LogisticRegression

import torch
import torch.nn as nn
import torch.optim as optim
from sklearn.preprocessing import StandardScaler


class BaseMLModel:
    def __init__(self):
        self.X = None
        self.y = None
        self.model = None
        self.name = "BaseMLModel"
        pass

    def set_data(self, X, y):
        self.X = X
        self.y = y

    def predict(self, X):
        return self.model.predict(X)


class SVMModel(BaseMLModel):
    def __init__(self):
        super().__init__()
        self.name = "SVMModel"
        pass

    def train(self):
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        print(X_train.shape)
        print(X_test.shape)
        print(y_train.shape)
        print(y_test.shape)

        # Create an SVM classifier
        self.model = SVC(kernel='linear')

        # Train the model using the training data
        self.model.fit(X_train, y_train)

        # Make predictions on the test data
        y_pred = self.model.predict(X_test)

        # Calculate the accuracy of the model
        accuracy = accuracy_score(y_test, y_pred)
        print("SVM Accuracy:", accuracy)


class KNearestNeighborModel(BaseMLModel):
    def __init__(self):
        super().__init__()
        self.name = "KNearestNeighborModel"
        pass

    def train(self):
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        # Create a KNN classifier with k=3
        self.model = KNeighborsClassifier(n_neighbors=3)

        # Train the model using the training data
        self.model.fit(X_train, y_train)

        # Make predictions on the test data
        y_pred = self.model.predict(X_test)

        # Calculate the accuracy of the model
        accuracy = accuracy_score(y_test, y_pred)
        print("KNN Accuracy:", accuracy)
        pass


class LogisticRegressionModel(BaseMLModel):
    def __init__(self):
        super().__init__()
        self.name = "LogisticRegressionModel"
        pass

    def train(self):
        # Split the data into training and testing sets
        X_train, X_test, y_train, y_test = train_test_split(self.X, self.y, test_size=0.2, random_state=42)

        # Create a Logistic Regression classifier
        self.model = LogisticRegression(max_iter=1000)

        # Train the model using the training data
        self.model.fit(X_train, y_train)

        # Make predictions on the test data
        y_pred = self.model.predict(X_test)

        # Calculate the accuracy of the model
        accuracy = accuracy_score(y_test, y_pred)
        print("LogReg Accuracy:", accuracy)


def neural_networks():
    # Load the iris dataset
    iris = datasets.load_iris()
    X = iris.data
    y = iris.target

    # Normalize the input features
    scaler = StandardScaler()
    X = scaler.fit_transform(X)

    # Split the data into training and testing sets
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)

    # Convert the data to PyTorch tensors
    X_train = torch.tensor(X_train, dtype=torch.float32)
    y_train = torch.tensor(y_train, dtype=torch.long)
    X_test = torch.tensor(X_test, dtype=torch.float32)
    y_test = torch.tensor(y_test, dtype=torch.long)

    # Define the Neural Network model
    class NeuralNet(nn.Module):
        def __init__(self):
            super(NeuralNet, self).__init__()
            self.fc1 = nn.Linear(4, 10)
            self.fc2 = nn.Linear(10, 3)

        def forward(self, x):
            x = torch.relu(self.fc1(x))
            x = self.fc2(x)
            return x

    # Create an instance of the NeuralNet model
    model = NeuralNet()

    # Define the loss function and optimizer
    criterion = nn.CrossEntropyLoss()
    optimizer = optim.Adam(model.parameters(), lr=0.001)

    # Train the model
    num_epochs = 100
    batch_size = 10

    for epoch in range(num_epochs):
        for i in range(0, len(X_train), batch_size):
            batch_X = X_train[i:i + batch_size]
            batch_y = y_train[i:i + batch_size]

            # Forward pass
            outputs = model(batch_X)
            loss = criterion(outputs, batch_y)

            # Backward and optimize
            optimizer.zero_grad()
            loss.backward()
            optimizer.step()

        # Print the loss for every 10 epochs
        if (epoch + 1) % 10 == 0:
            print(f"Epoch {epoch + 1}/{num_epochs}, Loss: {loss.item()}")

    # Evaluate the model
    with torch.no_grad():
        outputs = model(X_test)
        _, predicted = torch.max(outputs.data, 1)
        accuracy = (predicted == y_test).sum().item() / len(y_test)
        print("Accuracy:", accuracy)
    pass


'''
extract comments from the top of each file. includes the copyright since we can not filter this.
'''


def extract_comments(code_snippet):
    ast_parser = CodeAstParser()
    ast_root = ast_parser.parse(code_snippet)
    comment_node = []
    for node in ast_root.children:
        if node.type == "comment":
            comment_node.append(node)
        else:
            break
    # # print(code_snippet)
    res = ""
    for n in comment_node:
        try:
            text = n.text.decode("utf-8")
            res += text
            res += "\n"
        except UnicodeDecodeError as e:
            pass

    # res = "\n".join([node.text.decode("utf-8") for node in comment_node])

    return res


if __name__ == "__main__":

    # ast_parser = CodeAstParser()
    # git_helper = GitHelper("/home/wanghaichi/ltp")
    #
    # failed_count = {}
    # raw_data = []
    # file_cache = {}
    # for i in range(len(cia.ci_objs)):
    #     ci_obj = cia.ci_objs[i]
    #
    #     start_time = ci_obj.instance.git_commit_datetime
    #     start_time.replace(tzinfo=None)
    #     temp = []
    #     for tc in ci_obj.get_all_testcases():
    #         # failed count number
    #         failed_number = failed_count.get(tc.file_path, 0)
    #
    #         # age number
    #         if tc.file_path in file_cache.keys():
    #             tc_time = file_cache[tc.file_path][0]
    #         else:
    #             tc_time = git_helper.get_first_commit_info(
    #                 tc.file_path.replace("test_cases/ltp/", "")).committed_datetime
    #         tc_time.replace(tzinfo=None)
    #
    #         age = (start_time.year - tc_time.year) * 12 + (start_time.month - tc_time.month)
    #
    #         # text feature
    #         if tc.file_path in file_cache.keys():
    #             file_desc = file_cache[tc.file_path][1]
    #         else:
    #             print(tc.file_path)
    #             try:
    #                 file_desc = extract_comments(Path(tc.file_path).read_text())
    #             except UnicodeDecodeError as e:
    #                 file_desc = ""
    #
    #         is_failed = 0
    #         if tc.is_failed():
    #             is_failed = 1
    #         temp.append([tc, failed_number, age, file_desc, is_failed])
    #
    #         # update cache
    #         if tc.file_path not in file_cache.keys():
    #             file_cache[tc.file_path] = (tc_time, file_desc)
    #
    #         # update failed count
    #         if tc.file_path not in failed_count:
    #             failed_count[tc.file_path] = 0
    #         if tc.is_failed():
    #             failed_count[tc.file_path] += 1
    #     raw_data.append(temp)
    #     if i % 10 == 0:
    #         print(i, " done", len(cia.ci_objs) - i, " left")
    # pickle.dump(raw_data, open("raw_data_cache.pkl", "wb"))
    # for l in raw_data:
    #     for item in l:
    #         print(item)
    #
    # exit(-1)

    # total commits are 491, choose previous 300 commits for training and the rest for testing
    # raw_data = pickle.load(open("raw_data_cache.pkl", "rb"))
    # raw_data = [x for x in raw_data if len(x) > 0]
    #
    # # prepare text embedding
    # total_text_corpus = ""
    # already_set = set()
    # for l in raw_data:
    #     for tc in l:
    #         if tc[0].file_path in already_set:
    #             continue
    #         total_text_corpus += tc[3]
    #         total_text_corpus += " "
    #         already_set.add(tc[0].file_path)
    # # total_text_corpus = [" ".join(x[3]) for x in raw_data]
    # # total_text_corpus = " ".join(total_text_corpus)
    #
    # print("start training text embedding...")
    # print(len(total_text_corpus))
    # text_embedding = TextEmbedding()
    # text_embedding.word_size = 300
    # text_embedding.embed(total_text_corpus)
    #
    # # text_embedding.load("text_embedding.bin", "tfidf.pkl")
    # text_embedding.save("text_embedding.bin", "tfidf.pkl")
    # print("prepared text embedding")
    #
    #
    # # one hot vec
    # def generate_one_hot_vector(size, number):
    #     vector = np.zeros(size)
    #     vector[number] = 1
    #     return vector
    #
    #
    # one_hot_size = 300
    #
    # passed_data = []
    # failed_data = []
    # print("start converting data to vector...")
    #
    # embed_cache = {}
    # for l in raw_data[:100]:
    #     for tc in l:
    #         # print(tc)
    #         if tc[0].file_path in embed_cache.keys():
    #             vec = embed_cache[tc[0].file_path]
    #         else:
    #             vec = text_embedding.embed_sentence(tc[3])
    #             embed_cache[tc[0].file_path] = vec
    #         vec = np.concatenate(
    #             (vec, generate_one_hot_vector(one_hot_size, tc[1]), generate_one_hot_vector(one_hot_size, tc[2])))
    #         if tc[4] == 0:
    #             passed_data.append(vec)
    #         else:
    #             failed_data.append(vec)
    # print(len(passed_data), len(failed_data))
    # print(passed_data[0].shape)
    # print(failed_data[0].shape)
    #
    # X = passed_data[:2000]
    # X.extend(failed_data)
    # y = [0] * len(passed_data[:2000])
    # y.extend([1] * len(failed_data))
    # X = np.array(X)
    # y = np.array(y)
    # models = [SVMModel(), KNearestNeighborModel(), LogisticRegressionModel()]
    # for m in models:
    #     m.set_data(X, y)
    #     m.train()
    #
    # e_helper = EHelper()
    # apfd_total = [0, 0, 0]
    # for l in raw_data[100:]:
    #     faults_arr = []
    #     predict_arr = []
    #     for i in range(len(l)):
    #         tc = l[i]
    #         # print(tc)
    #         if tc[0].file_path in embed_cache.keys():
    #             vec = embed_cache[tc[0].file_path]
    #         else:
    #             vec = text_embedding.embed_sentence(tc[3])
    #             embed_cache[tc[0].file_path] = vec
    #         vec = np.concatenate(
    #             (vec, generate_one_hot_vector(one_hot_size, tc[1]), generate_one_hot_vector(one_hot_size, tc[2])))
    #         predict_arr.append(vec)
    #         if tc[4] == 1:
    #             faults_arr.append(i)
    #     for i in range(len(models)):
    #         predict_res = models[i].predict(predict_arr)
    #         # get sorted index for res, based on it;s value, desc
    #         order_arr = np.argsort(predict_res)[::-1]
    #         apfd = e_helper.APFD(faults_arr, order_arr.tolist())
    #         print(f"model: {models[i].name}, apfd: {apfd}")
    #         apfd_total[i] += apfd
    # for i in range(len(models)):
    #     print(f"model: {models[i].name}, average apfd: {apfd_total[i] / len(raw_data[100:])}")
    # # TODO 按照时间，划分训练集，因为数据不平衡，所以需要sample部分正常的数据，和fail的数据对等。所有的数据加起来，failed的数据有300+个，
    # # 因此选定某个时间后，把所有的fail的数据都加进去，然后sample 300个正常的数据，然后训练。
    #
    # # text embedding 搞定了
    # # TC age 和 linked failed number 使用 one-hot encoding
    pass
