import operator

from nltk.stem import SnowballStemmer
from nltk.tokenize import word_tokenize, sent_tokenize

import os


def get_documents(path):
    all_files = []
    for root, dirs, files in os.walk(path):
        for name in files:
            all_files.append(os.path.join(root, name).replace('\\\\', '\\'))

    for file in all_files:
        assert os.path.exists(file)

    return all_files


def read_doc(doc):
    with open(doc, 'r', encoding='UTF-8') as f:
        return f.read()


def process_docs(docs):
    stemmer = SnowballStemmer("english")
    stems_per_doc = []
    words_per_sent_per_doc = []
    st_per_doc = []

    for doc in docs:
        text = read_doc(doc)
        sent_tokenized = sent_tokenize(text, "english")
        st_per_doc.append(sent_tokenized)
        words_per_sentence = list(map(word_tokenize, sent_tokenized))

        list_of_words = []
        for words in words_per_sentence:
            words = list(filter(lambda x: True if x.isalnum() else False, words))
            list_of_words += words

        new_list_of_words = []
        for word in list_of_words:
            new_list_of_words.append(stemmer.stem(word))
        stems_per_doc.append(new_list_of_words)  # we want them to repeat here, so we can count the most common ones.

        words_per_sent_per_doc.append(words_per_sentence)

    return stems_per_doc, words_per_sent_per_doc, st_per_doc


def calc_tf(stems_per_doc):
    from collections import Counter
    counters_per_doc = []
    for stems in stems_per_doc:
        counters_per_doc.append(Counter(stems))

    return counters_per_doc

    # most_commons.append(counter.most_common(10))
    # return most_commons


def union_list_of_lists(lol):
    big = []
    for lst in lol:
        big += list(set(lst))

    return list(set(big))


def calc_idf(stems, position):
    import math
    n = len(stems)
    words_in_doc = list(set(stems[position]))

    k_w = {}

    for word in words_in_doc:
        k_word = 0
        for stem in stems:
            if word in stem:
                k_word += 1
        k_w[word] = math.log(n / k_word)

    return k_w


def first_part(cps, doc):
    docs = get_documents(cps)
    stems_per_doc, words_per_sent_per_doc, sentences_per_doc = process_docs(docs)

    if doc not in docs:
        print('Document path not in corpus!')
        exit()

    position = docs.index(doc)
    counter = calc_tf(stems_per_doc)[position]
    tf_dict = dict((x, y) for x, y in counter.most_common())

    idf_dict = calc_idf(stems_per_doc, position)

    tf_idf_dict = {}

    for stem in tf_dict:
        tf_idf_dict[stem] = tf_dict[stem] * idf_dict[stem]

    best10 = sorted(tf_idf_dict)
    best10.sort(key=tf_idf_dict.get, reverse=True)
    best10 = best10[:10]

    print(', '.join(best10))

    return stems_per_doc[position], words_per_sent_per_doc[position], tf_idf_dict, sentences_per_doc[position]


def second_part(sentences, words, tf_idf_dict):
    new_senteces = []
    for sentence in words:
        sentence = list(filter(lambda x: True if x.isalnum() else False, sentence))
        new_senteces.append(sentence)

    stems_per_sentence = []
    for sentence in new_senteces:
        new_list_of_words = []
        for word in sentence:
            new_list_of_words.append(SnowballStemmer("english").stem(word))
        stems_per_sentence.append(new_list_of_words)
        # unique stems per sentence

    score_per_sentence = []
    for stems in stems_per_sentence:
        scores = []
        for stem in stems:
            if stem in tf_idf_dict:
                scores.append(tf_idf_dict[stem])
        scores.sort()
        score_per_sentence.append(sum(scores[-10:]))

    score_per_sentence = list(enumerate(score_per_sentence))

    score_per_sentence.sort(key=lambda x: (x[1], -x[0]), reverse=True)

    sentences_order = list(map(lambda x: x[0], score_per_sentence))[:5]
    sentences_order.sort()

    final = []
    for n in sentences_order:
        final.append(sentences[n])

    print(' '.join(final))


def main():
    corpus = input()
    assert os.path.exists(corpus)
    file_name = input()
    assert os.path.exists(file_name)
    file_names = [file_name]
    # corpus = 'C:\\Users\\smitric\\Desktop\\psiml\\TFIDF\\public\\corpus'
    # file_names = [  # corpus + '\\goose\\Chinese goose.txt',
    #     # corpus + '\\impressionism\\Impressionism.txt',
    #     # corpus + '\\Joe\\Joe Manchin.txt',
    #     # corpus + '\\quantum\\Quantum teleportation.txt',
    #     # corpus + '\\skiing\\Speed skiing.txt',
    #     # corpus + '\\quantum\\Quantum of Solace.txt',
    #     corpus + '\\Joe\\Kaarma-Jõe.txt',
    #     # corpus + '\\goose\\other\\Short goose.txt',
    #     # corpus + '\\goose\\other\\Tricky goose.txt',
    #     # corpus + '\\goose\\other\\Weirdly named goose.txt'
    # ]

    import sys

    sys.stdout.reconfigure(encoding='utf-8')

    for file_name in file_names:
        stems, words, tf_idf_dict, sentences = first_part(corpus, file_name)
        second_part(sentences, words, tf_idf_dict)


if __name__ == '__main__':
    main()
