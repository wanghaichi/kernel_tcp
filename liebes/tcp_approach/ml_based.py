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
    pass
