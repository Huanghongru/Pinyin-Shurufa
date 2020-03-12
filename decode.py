import os
import math
from language_model import LanguageModel

def load_pinyin_dict(file_path="data/pinyin2kanji.dict"):
    pinyin2kanji = {}
    max_len = 0
    with open(file_path, 'r') as fin:
        for line in fin.readlines():
            line = line.strip().split()
            pinyin2kanji[line[0]] = [kanji for kanji in line[1:]]
            max_len = max(max_len, len(line[1:]))
    return max_len, pinyin2kanji

def decode(pinyins):
    """
    Use Viterbi to decode the pinyin sequence.
    """
    lm = LanguageModel.load_from_trained()
    max_l, pinyin2kanji = load_pinyin_dict()
    pinyins = pinyins.split()

    # dp[i][j] := (a, b) the minimum length of path from
    #   pinyin sequence[0:i] with the i-th pinyin decoded
    #   as kanji j is a and its previous kanji index at i-1
    #   pinyin is b
    dp = [[[float('inf'), 0] for _ in range(max_l)] for _ in range(len(pinyins)+1)]
    dp[0][0] = [0., -1]

    m = len(pinyins)
    for i in range(1, m+1):
        cur_kanjis = pinyin2kanji[pinyins[i-1]]
        for j, cur_kanji in enumerate(cur_kanjis):
            if i > 1:
                pre_kanjis = pinyin2kanji[pinyins[i-2]]
                for k, pre_kanji in enumerate(pre_kanjis):
                    w = -math.log(lm.get(cur_kanji, pre_kanji))
                    if dp[i-1][k][0] + w < dp[i][j][0]:
                        dp[i][j] = [dp[i-1][k][0] + w, k]
            else:
                pre_kanji = "/"
                w = -math.log(lm.get(cur_kanji, pre_kanji))
                if dp[i-1][0][0] + w < dp[i][j][0]:
                    dp[i][j] = [dp[i-1][0][0] + w, 0]
    """
    for i in range(1, m+1):
        for j in range(len(pinyin2kanji[pinyins[i-1]])):
            print("{}: {}".format(pinyin2kanji[pinyins[i-1]][j], dp[i][j]), end=' ')
        print("\n")
    """

    idx, pre_idx, min_len = 0, 0, float('inf')
    for j, kanji in enumerate(pinyin2kanji[pinyins[-1]]):
        if dp[-1][j][0] < min_len:
            min_len, pre_idx = dp[-1][j]
            idx = j

    res = ""
    for i in range(-1, -m-1, -1):
        res += pinyin2kanji[pinyins[i]][idx]
        _, idx = dp[i][idx]
    return res[::-1]

pinyins = [
    "tian qing se deng yan yu wo zai deng han pi",
    "qing hua wu zhong du",
    "qing hua ci",
    "dong ren de qing hua",
]
for pinyin in pinyins:
    print(pinyin)
    print(decode(pinyin))
