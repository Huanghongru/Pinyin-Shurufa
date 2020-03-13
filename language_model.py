import os
import math
import pickle
import argparse
import collections

class LanguageModel(object):
    """ A traditional language model. """

    def __init__(self, ngram, freq=None):
        self.ngram = ngram
        if freq is None:
            self.freq = collections.Counter()
            self.total_single_cnt = 0
        else:
            self.freq = freq
            self.total_single_cnt = 0
            for k, v in self.freq.items():
                if len(k) == 1:
                    self.total_single_cnt += v

        if not os.path.exists('models'):
            os.mkdir('models')

        self.checkpoint = os.path.join("models", "{}-lm.pkl".format(ngram))

    @staticmethod
    def load_from_trained(model_path="models/2-lm.pkl"):
        with open(model_path, 'rb') as f:
            freq = pickle.load(f)

        ngram = int(model_path.split('-')[0][-1])
        return LanguageModel(ngram, freq)
    
    def save(self):
        with open(self.checkpoint, 'wb') as f:
            pickle.dump(self.freq, f, pickle.HIGHEST_PROTOCOL)

    def update(self, sentence):
        """
        update the Language Model with the input sentence.

        Args:
            sentence(str): a sentence.
        """
        l = len(sentence)
        for n in range(1, self.ngram + 1):
            for i in range(0, l - n + 1):
                self.freq[sentence[i:i+n]] += 1

    def get(self, target, condition):
        """ 
        Return the probability P(w_t | w_{1,...,t-1}).
        where `condition` = w_{1, ..., t-1}, 
              `target` = {w_t}

        Just use the simple interpolation smoothing here.
        
        Args:
            condition(str): a series of kanji, length equal to ngram-1
            target(str): a single kanji
        Return:
            p(float): the probability
        """
        if self.ngram == 2:
            lambda_ = 0.8
            xy = self.freq[condition + target]
            x = self.freq[condition] if self.freq[condition] else 1
            y = self.freq[target] if self.freq[target] else 1
            p = lambda_ * xy / x + (1 - lambda_) * x / self.total_single_cnt
        else:
            lambda_ = 0.4
            beta = 0.4
            xyz = self.freq[condition + target]
            xy = self.freq[condition] if self.freq[condition] else 1.
            yz = self.freq[condition[-1] + target]
            y = self.freq[condition[-1]] if self.freq[condition[-1]] else 1.
            z = self.freq[target] if self.freq[target] else 1.
            t = self.total_single_cnt

            # print("{}\t{}\t{}\t{}\t{}".format(xyz, xy, yz, y, z))
            p = lambda_ * xyz / xy + beta * yz / y + (1 - lambda_ - beta) * z / t
        return p

    def __getitem__(self, tokens):
        return self.freq[tokens]


def train(datafile="data/corpus.dat"):
    lm = LanguageModel(ngram=3)
    
    with open(datafile, 'r') as df:
        for i, line in enumerate(df.readlines()):
            lm.update(line.strip())

            if i % 100000 == 0:
                print("learned {} lines".format(i))
        lm.save()

def main():
    train()
    lm = LanguageModel.load_from_trained()
    print(len(lm.freq.keys()))
    print(lm['大雪'])

if __name__ == '__main__':
    main()
