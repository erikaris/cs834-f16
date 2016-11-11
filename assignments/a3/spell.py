import re
from collections import Counter

import sys


class Spell:
    def __init__(self, train_file):
        self.document = open(train_file).read()
        self.to_words()
        self.count_words()

    def to_words(self):
        self.words = re.findall(r'\w+', self.document.lower())

    def count_words(self):
        self.word_count = Counter(self.words)

    def probability(self, word):
        "Probability of `word`."
        word = word.lower()
        N = sum(self.word_count.values())
        return self.word_count[word] / N

    def edits1(self, word):
        "All edits that are one edit away from `word`."
        word = word.lower()
        letters = 'abcdefghijklmnopqrstuvwxyz'
        splits = [(word[:i], word[i:]) for i in range(len(word) + 1)]
        deletes = [L + R[1:] for L, R in splits if R]
        transposes = [L + R[1] + R[0] + R[2:] for L, R in splits if len(R) > 1]
        replaces = [L + c + R[1:] for L, R in splits if R for c in letters]
        inserts = [L + c + R for L, R in splits for c in letters]
        return set(deletes + transposes + replaces + inserts)

    def edits2(self, word):
        "All edits that are two edits away from `word`."
        word = word.lower()
        return (e2 for e1 in self.edits1(word) for e2 in self.edits1(e1))

    def known(self, words):
        "The subset of `words` that appear in the dictionary of WORDS."
        return set(w for w in words if w in self.word_count)

    def candidates(self, word):
        "Generate possible spelling corrections for word."
        word = word.lower()
        return (self.known([word]) or self.known(self.edits1(word)) or self.known(self.edits2(word)) or [word])

    def correction(self, word):
        "Most probable spelling correction for word."
        word = word.lower()
        candidates = self.candidates(word)
        return max(candidates, key=self.probability)


if __name__ == '__main__':
    spell = Spell('big.txt')

    if len(sys.argv) != 2:
        print('python spell.py <word>')
        exit()

    word = sys.argv[1]
    spelled_word = spell.correction(word)

    print('{} --> {}'.format(word, spelled_word))