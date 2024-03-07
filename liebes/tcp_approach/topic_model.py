from gensim import corpora
from gensim.models import LdaModel
from gensim.utils import simple_preprocess


class TopicModel:
    def __init__(self, number_of_topics=20):
        self.model = None
        self.dictionary = None
        self.number_of_topics = number_of_topics
        pass

    def train(self, documents):
        # # Sample documents
        # documents = [
        #     "The cat chased the mouse",
        #     "The dog barked at the mailman",
        #     "The mouse ran away from the cat and the dog",
        #     "The mailman delivered the package"
        # ]

        # Preprocess the documents
        processed_docs = [simple_preprocess(doc) for doc in documents]

        # Create a dictionary from the preprocessed documents
        self.dictionary = corpora.Dictionary(processed_docs)

        # Create a corpus (bag-of-words representation) from the dictionary
        corpus = [self.dictionary.doc2bow(doc) for doc in processed_docs]

        # Train the LDA model
        self.model = LdaModel(corpus=corpus, id2word=self.dictionary, num_topics=self.number_of_topics)

        # # Get the topics and their associated words
        # topics = self.model.print_topics(num_topics=num_topics)
        #
        # # Print the topics and their associated words
        # for topic in topics:
        #     print(topic)

    def get_topic(self, sentence):
        # Transform the sentences into topic distributions
        # sentence = "I love playing sports"

        sentence1_bow = self.dictionary.doc2bow(sentence.lower().split())

        sentence_topic_dist = self.model[sentence1_bow]

        return sentence_topic_dist


if __name__ == "__main__":
    pass
    #
    # information_manager = TestCaseInformationManager(cia, git_helper=GitHelper("/home/wanghaichi/ltp"))
    # distance_manager = DistanceMetric()
    # ehelper = EHelper()
    # apfd_arr = []
    # for ci_obj, tokens in information_manager.extract():
    #     all_cases = ci_obj.get_all_testcases()
    #     faults_arr = []
    #     for i in range(len(all_cases)):
    #         if all_cases[i].is_failed():
    #             faults_arr.append(i)
    #     if len(faults_arr) == 0:
    #         continue
    #
    #     topic_model = TopicModel()
    #     documents = []
    #     for k, v in tokens.items():
    #         documents.append(" ".join(v))
    #     topic_model.train(documents)
    #     topic_value = {}
    #     for k, v in tokens.items():
    #         tv = topic_model.get_topic(" ".join(v))
    #         temp = [0] * topic_model.number_of_topics
    #         for t in tv:
    #             temp[t[0]] = t[1]
    #         topic_value[k] = temp
    #
    #     distance_arr = np.zeros((len(all_cases), len(all_cases)))
    #     for i in range(len(all_cases)):
    #         for j in range(i + 1, len(ci_obj.get_all_testcases())):
    #             # print(topic_value[all_cases[i].file_path])
    #             # print(topic_value[all_cases[j].file_path])
    #             distance = distance_manager.jensen_shannon_distance(
    #                 topic_value[all_cases[i].file_path],
    #                 topic_value[all_cases[j].file_path]
    #             )
    #             distance_arr[i][j] = distance_arr[j][i] = distance
    #     # fill the array
    #     # print(distance_arr)
    #     # process of ARP
    #     distance_arr = np.array(distance_arr)
    #
    #     choose_one = random.randint(0, len(all_cases) - 1)
    #
    #     prioritized_list = [choose_one]
    #     candidate_list = [i for i in range(len(all_cases))]
    #     candidate_list.remove(choose_one)
    #     print("start to prio")
    #     while len(candidate_list) > 0:
    #         distance_slice = distance_arr[prioritized_list][:, candidate_list]
    #         min_distance = np.min(distance_slice, axis=0)
    #         max_index = np.argmax(min_distance)
    #         prioritized_list.append(candidate_list[max_index])
    #         candidate_list.remove(candidate_list[max_index])
    #     # calculate
    #
    #     apfd = ehelper.APFD(faults_arr, prioritized_list)
    #
    #     logger.info(f"apfd {ci_obj.instance.git_sha}: {apfd}")
    #     apfd_arr.append(apfd)
    #     # print(prioritized_list)
    #     # exit(-1)
    # print(f"avg apfd: {np.mean(apfd_arr)}")
    # exit(-1)