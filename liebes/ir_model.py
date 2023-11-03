from rank_bm25 import BM25Okapi
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from gensim import corpora, models, similarities

import numpy as np


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
        temp = np.concatenate((np.array(corpus), np.array(queries)))
        tfidf_matrix = self.vectorization(temp)

        # 计算余弦相似度
        cosine_similarity_matrix = cosine_similarity(tfidf_matrix)
        similarity_matrix = cosine_similarity_matrix[: len(corpus), len(corpus):]
        return similarity_matrix


class Bm25Model(BaseModel):
    def __init__(self):
        super().__init__(name="Bm25Model")

    def get_similarity(self, corpus, queries):
        tokenized_corpus = [doc.split(" ") for doc in np.concatenate((np.array(corpus), np.array(queries)))]
        bm25 = BM25Okapi(tokenized_corpus)
        tokenized_query = [doc.split(" ") for doc in queries]
        score_matrix = np.array([bm25.get_scores(query) for query in tokenized_query])[:, : len(corpus)]
        return score_matrix


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
