"""
General embedding class for all embedding methods,
includes code embedding, text embedding
"""
import pickle
import string
from gensim.models import Word2Vec
from gensim.utils import simple_preprocess
from nltk.tokenize import sent_tokenize, word_tokenize
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Embedding:
    def __init__(self):
        pass

    def embed(self, code_snippet: str):
        """
        code embedding method
        :param code_snippet: code snippet
        :return: code embedding
        """
        raise NotImplementedError

    def query(self, word):
        """
        query method
        :param word: str or number
        :return: word embedding
        """
        raise NotImplementedError


class NumberEmbedding(Embedding):
    def __init__(self):
        super().__init__()

    def embed(self, number: int):
        """
        number embedding method
        :param number: number
        :return: number embedding
        """
        raise NotImplementedError


class CodeEmbedding(Embedding):
    def __init__(self):
        super().__init__()

    def embed(self, code_snippet: str):
        """
        code embedding method
        :param code_snippet: code snippet
        :return: code embedding
        """
        raise NotImplementedError


class TextEmbedding(Embedding):
    def __init__(self):
        super().__init__()
        # only need execute once
        # import nltk
        # nltk.set_proxy("http://172.19.135.130:5000")
        # nltk.download('punkt')
        self.model = None
        self.word_size = 300
        self.oov = "<OOV>"

        self.tf_idf_model = TfidfVectorizer()

    def convert_sen_to_token_list(self, sentence):
        # Tokenize the text into sentences
        sentences = sent_tokenize(sentence)
        # Tokenize the sentences into words
        tokenized_sentences = [word_tokenize(sentence) for sentence in sentences]
        # Remove punctuation
        filtered_sentences = [[token for token in sentence if token not in string.punctuation] for sentence in
                              tokenized_sentences]
        preprocessed_sentences = [simple_preprocess(" ".join(sent)) for sent in filtered_sentences]
        return preprocessed_sentences

    def embed(self, text: str):
        """
        text embedding method
        :param text: text
        :return: text embedding
        """
        # text = "Hello! How are you? I hope you're doing well."  # 100

        # # Define a list of sentences or documents
        # sentences = [
        #     ["I", "love", "coding"],
        #     ["Python", "is", "awesome"],
        #     ["Machine", "learning", "is", "fascinating"],
        #     ["Natural", "language", "processing", "is", "challenging"]
        # ]
        # Preprocess the sentences
        preprocessed_sentences = self.convert_sen_to_token_list(text)
        # build tf-idf model
        corpus = [" ".join(sent) for sent in preprocessed_sentences]
        # Initialize and fit the TF-IDF vectorizer
        self.tf_idf_model.fit(corpus)

        # Train the Word2Vec model
        # sg = 0 : CBOW, sg = 1 : Skip-gram
        self.model = Word2Vec(preprocessed_sentences, vector_size=self.word_size, window=5, sg=0, min_count=1)
        # generate embedding for OOV word:
        oov_vec = np.zeros(self.word_size)
        # self.model.build_vocab(preprocessed_sentences, update=True)
        for word, _ in self.model.wv.key_to_index.items():
            embedding = self.model.wv[word]
            # print(embedding)
            oov_vec += embedding
        # print(oov_vec)
        # print(len(self.model.wv.key_to_index))
        oov_vec /= len(self.model.wv.key_to_index)
        self.model.wv[self.oov] = oov_vec

    def embed_sentence(self, sentence: str):
        if len(sentence) == 0:
            return np.zeros(self.word_size)
        # Tokenize the text into sentences
        sentences = self.convert_sen_to_token_list(sentence)
        tf_idf_input = [" ".join(sent) for sent in sentences]
        tf_idf_input = " ".join(tf_idf_input)
        tfidf_vec = self.get_tf_idf_vec(tf_idf_input)

        res = np.zeros(self.word_size)

        for words in sentences:
            for word in words:
                if word in tfidf_vec.keys():
                    res += self.query(word) * tfidf_vec[word]
                else:
                    # TODO the OOV word is just ignored, should we do something else?
                    # print("????")
                    pass
        return res

    def get_tf_idf_vec(self, sentence: str):
        # Transform a sentence into its TF-IDF vector
        # sentence = "This is an example sentence."
        vector = self.tf_idf_model.transform([sentence])
        features = self.tf_idf_model.get_feature_names_out()
        return {features[i]: vector[0, i] for i in range(len(features))}

    def query(self, word: str):
        if self.model is None:
            raise ValueError("Model is not trained yet, call embed method first.")

        word = word.lower()
        # Get the embedding vector for a specific word
        if word in self.model.wv.key_to_index.keys():
            return self.model.wv[word]
        else:
            return self.model.wv[self.oov]

    def save(self, file_path: str, tf_idf_file_path: str):
        self.model.save(file_path)
        with open(tf_idf_file_path, 'wb') as f:
            pickle.dump(self.tf_idf_model, f)

    def load(self, file_path: str, tf_idf_file_path: str):
        self.model = Word2Vec.load(file_path)
        self.word_size = self.model.vector_size
        self.oov = "<OOV>"

        self.tf_idf_model = pickle.load(open(tf_idf_file_path, "rb"))
