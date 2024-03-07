import math
import numpy as np
import zlib
from scipy.spatial import distance


class DistanceMetric:
    def __init__(self):
        pass

    def normalized_compression_distance(self, sequence_a, sequence_b):
        sequence_a = sequence_a.encode("utf8")
        sequence_b = sequence_b.encode("utf8")
        concatenated_sequence = sequence_a + sequence_b
        compressed_concatenated = zlib.compress(concatenated_sequence)
        compressed_a = zlib.compress(sequence_a)
        compressed_b = zlib.compress(sequence_b)

        ncd = (len(compressed_concatenated) - min(len(compressed_a), len(compressed_b))) / max(len(compressed_a),
                                                                                               len(compressed_b))
        return ncd

    def euclidean_string_distance(self, s1, s2):
        len_diff = abs(len(s1) - len(s2))
        if len(s1) < len(s2):
            s1 += '\0' * len_diff
        elif len(s1) > len(s2):
            s2 += '\0' * len_diff
        point1 = [ord(char) for char in s1]
        point2 = [ord(char) for char in s2]
        squared_diff = sum((p1 - p2) ** 2 for p1, p2 in zip(point1, point2))
        return math.sqrt(squared_diff)

    def jaccard_distance_function(self, set1, set2):
        set1 = set(set1)
        set2 = set(set2)
        intersection = len(set1.intersection(set2))
        union = len(set1.union(set2))

        distance = 1 - intersection / union
        return distance

    def manhattan_string_distance(self, s1, s2):
        len_diff = abs(len(s1) - len(s2))
        if len(s1) < len(s2):
            s1 += '\0' * len_diff
        elif len(s1) > len(s2):
            s2 += '\0' * len_diff
        point1 = [ord(char) for char in s1]
        point2 = [ord(char) for char in s2]

        distance = 0
        for i in range(len(point1)):
            distance += abs(point1[i] - point2[i])
        return distance

    def edit_distance(self, s1, s2):
        m, n = len(s1), len(s2)
        dp = [[0] * (n + 1) for _ in range(m + 1)]

        for i in range(m + 1):
            dp[i][0] = i
        for j in range(n + 1):
            dp[0][j] = j

        for i in range(1, m + 1):
            for j in range(1, n + 1):
                if s1[i - 1] == s2[j - 1]:
                    dp[i][j] = dp[i - 1][j - 1]
                else:
                    dp[i][j] = min(dp[i - 1][j] + 1, dp[i][j - 1] + 1, dp[i - 1][j - 1] + 1)

        return dp[m][n]

    def hanming_distance(self, s1, s2):
        len_diff = abs(len(s1) - len(s2))
        if len(s1) < len(s2):
            s1 += '\0' * len_diff
        elif len(s1) > len(s2):
            s2 += '\0' * len_diff
        distance = 0
        for i in range(len(s1)):
            if s1[i] != s2[i]:
                distance += 1
        return distance


    def jensen_shannon_distance(self, p, q):

        p = np.array(p)
        q = np.array(q)
        js_divergence = distance.jensenshannon(p, q)
        return js_divergence


