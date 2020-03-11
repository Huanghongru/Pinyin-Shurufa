import os
import re
import json

def load_pinyin_dict(fname='data/pinyin2kanji.dict'):
    kanji2pinyin = {}
    with open(fname, 'r') as fin:
        for line in fin.readlines():
            line = line.split()
            for kanji in line[1:]:
                kanji2pinyin[kanji] = line[0]
    return kanji2pinyin

def normalize(text):
    # eliminate commas and other non-kanji
    pattern = r'[0-9\s+\.\!\/_,$%^*()?;；:-【\-】+\"\']+|[+——！，;:。？、~@#〔〕－＋～％￥%……&*（／）：；]+'

    tmps = re.sub(pattern, ' ', text).split()

    # eliminates rare kanji
    kanji2pinyin = load_pinyin_dict()

    def remove_rare(t):
        out_t = ""
        for kanji in t:
            out_t += kanji if kanji in kanji2pinyin.keys() else ' '
        return out_t.split()

    texts = []
    for text in tmps:
        texts += remove_rare(text)
    return texts

def read_news(fname):
    text = []
    with open(fname, 'r', encoding='utf-8') as fin:
        for line in fin.readlines():
            try:
                data = json.loads(line)
                text += normalize(data['title'])
                text += normalize(data['html'])
            except Exception as e:
                print(e)
                print("bad line", line)
    return text

def make_dataset():
    corpus = open("data/corpus.dat", "w")

    total, bad_examples = 0., 0.
    for data_file in os.listdir('data'):
        if data_file.split('.')[-1] != 'txt':
            continue
        texts = read_news(os.path.join('data', data_file))
        for text in texts:
            if len(text) < 2:
                bad_examples += 1
                continue
            corpus.write("/" + text + "\n")

        total += len(texts)
        print("preprocessed {}".format(data_file))
    print("Total corpus: {}\t Bad examples: {} Effective rate: {}".format(
        total, bad_examples, (total - bad_examples) / total))

    corpus.close()

make_dataset()
