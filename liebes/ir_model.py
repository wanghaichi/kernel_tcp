from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim import corpora, models, similarities
import numpy as np
from collections import Counter
import re


class BaseModel:
    def __init__(self, name="BaseVirtualIrModel"):
        self.name = name
        pass

    def get_similarity(self, corpus, queries):
        # corpus是语料库，这里是tokenizer后的testcases，定义为一个1xN的矩阵，每个元素为一个token，类似以下：
        # corpus = [
        # 'This is the first document.',
        # 'This document is the second document.',
        # 'And this is the third one.',
        # 'Is this the first document?'
        # ]

        # queries在这里为kernel diff，与corpus结构一样

        # 返回结果为一个N*M的相似度矩阵，N为corpus的大小，M为queries的大小，元素Rij表示第i个query与第j个corpus的相似度
        # 结果用np.sum(result, axis=1)进行聚合，可以得到一个N*1的矩阵，表示每个预料对所有查询的相似度汇总
        pass


class TfIdfModel(BaseModel):

    def __init__(self):
        super().__init__(name="TfIdfModel")
        # 创建一个TfidfVectorizer对象
        self.vectorizer = TfidfVectorizer()

    def vectorization(self, corpus):
        tfidf_matrix = self.vectorizer.fit_transform(corpus)
        return tfidf_matrix.toarray()

    def get_similarity(self, corpus, queries):
        # temp = np.concatenate((np.array(corpus), np.array(queries)))
        # tfidf_matrix = self.vectorization(temp)
        tfidf_matrix = self.vectorization(corpus)
        query_vector = self.vectorizer.transform(queries)

        # 计算余弦相似度
        # cosine_similarity_matrix = cosine_similarity(tfidf_matrix)
        # similarity_matrix = cosine_similarity_matrix[: len(corpus), len(corpus):]
        similarity_matrix = np.transpose(cosine_similarity(query_vector, tfidf_matrix))
        return similarity_matrix


class Bm25Model(BaseModel):

    def __init__(self, k1=2, k2=2, b=0.75):
        super().__init__(f"Bm25Model-k1-{k1}-k2-{k2}-b-{b}")
        self.corpus = None
        self.doc_num = 0
        self.avg_doc_len = 0
        self.tf = []
        self.idf = {}
        self.k1 = k1
        self.k2 = k2
        self.b = b

    def init(self, corpus):
        corpus = [re.findall(r'\b\w+\b', doc) for doc in corpus]
        self.corpus = corpus
        self.doc_num = len(corpus)
        self.avg_doc_len = sum([len(doc) for doc in corpus]) / self.doc_num
        df = {}
        for doc in self.corpus:
            tmp = {}
            for word in doc:
                tmp[word] = tmp.get(word, 0) + 1
            self.tf.append(tmp)
            for key in tmp.keys():
                df[key] = df.get(key, 0) + 1

        for key, value in df.items():
            self.idf[key] = np.log((self.doc_num - value + 0.5) / (value + 0.5))

    def get_score(self, index, query):
        score = 0.0
        doc_len = len(self.tf[index])
        qf = Counter(query)
        for q in qf:
            if q not in self.tf[index]:
                continue
            score += self.idf[q] * (self.tf[index][q] * (self.k1 + 1) / (
                    self.tf[index][q] + self.k1 * (1 - self.b + self.b * doc_len / self.avg_doc_len))) * (
                             qf[q] * (self.k2 + 1) / (qf[q] + self.k2))

        return score

    def get_doc_score(self, query):
        score_list = []
        for i in range(self.doc_num):
            score_list.append(self.get_score(i, query))

        return score_list

    def get_similarity(self, corpus, queries):

        self.init(corpus)
        tokenized_query = [re.findall(r'\b\w+\b', doc) for doc in queries]
        similarity_matrix = []
        for q in tokenized_query:
            similarity_matrix.append(self.get_doc_score(q))

        return np.transpose(np.array(similarity_matrix))


class LSIModel(BaseModel):
    def __init__(self, num_topics=2):
        super().__init__(name=f"LSIModel-topic-{num_topics}")
        self.num_topics = num_topics

    def get_similarity(self, corpus, queries):
        tokenized_corpus = [doc.split(' ') for doc in np.concatenate((np.array(corpus), np.array(queries)))]
        dictionary = corpora.Dictionary(tokenized_corpus)

        doc_term_matrix = [dictionary.doc2bow(tokens) for tokens in tokenized_corpus]

        lsi_model = models.LsiModel(doc_term_matrix, id2word=dictionary, num_topics=self.num_topics)
        similarity_matrix = np.array(similarities.MatrixSimilarity(lsi_model[doc_term_matrix]))

        return similarity_matrix[0: len(corpus), len(corpus):]


class LDAModel(BaseModel):
    def __init__(self, num_topics=2):
        super().__init__(name=f"LDAModel-topic-{num_topics}")
        self.num_topics = num_topics

    def get_similarity(self, corpus, queries):
        tokenized_corpus = [doc.split(' ') for doc in np.concatenate((np.array(corpus), np.array(queries)))]
        dictionary = corpora.Dictionary(tokenized_corpus)

        doc_term_matrix = [dictionary.doc2bow(tokens) for tokens in tokenized_corpus]

        lsi_model = models.LdaModel(doc_term_matrix, id2word=dictionary, num_topics=self.num_topics)
        similarity_matrix = np.array(similarities.MatrixSimilarity(lsi_model[doc_term_matrix]))

        return similarity_matrix[0: len(corpus), len(corpus):]


class RandomModel(BaseModel):
    def __init__(self):
        super().__init__(name="RandomModel")

    def get_similarity(self, corpus, queries):
        return np.random.random((len(corpus), len(queries)))
