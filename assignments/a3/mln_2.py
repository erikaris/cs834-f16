import json
import os
import random
import html2text
import io
import math
import nltk

from krovetzstemmer import Stemmer as KrovetzStemmer
from nltk.corpus import stopwords


class AssociationMeasure:
    _document_words_index = {}
    _window_words_index_cache = {}
    _word_windows_index_cache = {}

    def __init__(self, dir_name):
        '''
        List all files in dir_name, and create document-words index
        :param dir_name:
        '''

        self._document_words_index = json.loads(io.open(dir_name).read())

    def get_window_words_index(self, window_size=None):
        '''
        Get window-words index
        :param window_size: number of words in a window, None or False if use document
        :return:
        '''

        # Re-build word_windows_index if window_size is not exists in _word_windows_index_cache
        if window_size not in self._window_words_index_cache:
            if not window_size:
                window_words_index = self._document_words_index
            else:
                window_words_index = {}
                for document, words in self._document_words_index.items():
                    for w in range(1, int(len(words) / window_size)):
                        start = (w - 1) * window_size
                        end = w * window_size
                        if end > len(words): end = len(words)

                        window_words = words[start:end]
                        window_words_index[document + '_part_' + str(w)] = window_words

            # Cache word_windows_index for each window_size
            self._window_words_index_cache[window_size] = window_words_index


        return self._window_words_index_cache[window_size]

    def get_all_words(self, window_words_index):
        '''
        Get all words in a window-words index
        :param window_words_index:
        :return:
        '''

        all_words = []
        for window, words in window_words_index.items():
            all_words += words

        all_words = set(all_words)
        return all_words

    def get_stemmed_words_index(self, window_words_index):
        '''
        Get stemmed-words index from window-words index
        :param window_words_index:
        :return:
        '''

        all_words = self.get_all_words(window_words_index)
        stem_words_index = {}

        krovetz = KrovetzStemmer()
        for word in all_words:
            # Stem word using krovetz
            stemmed_word = krovetz.stem(word)

            # Group by stemmed word
            stem_words_index.setdefault(stemmed_word, [])
            stem_words_index[stemmed_word].append(word)

        return stem_words_index

    def get_word_windows_index(self, window_size=None):
        '''
        Get word-windows index
        :param window_size: number of words in a window, None or False if use document
        :return:
        '''

        return json.loads(io.open('../6_1/1_2_index.txt').read())

        # # Re-build word_windows_index if window_size is not exists in _word_windows_index_cache
        # if window_size not in self._word_windows_index_cache:
        #     window_words_index = self.get_window_words_index(window_size)
        #     all_words = self.get_all_words(window_words_index)
        #
        #     word_windows_index = {}
        #     for idx, word in enumerate(all_words):
        #         print('{} of {}. Indexing word {}'.format(idx + 1, len(all_words), word.encode('utf-8')))
        #         print('=' * 30)
        #
        #         files = []
        #         for file, words in window_words_index.items():
        #             if word in words:
        #                 files.append(file)
        #         word_windows_index[word] = sorted(set(files))
        #
        #
        #     # Cache word_windows_index for each window_size
        #     self._word_windows_index_cache[window_size] = word_windows_index
        #
        #
        # return self._word_windows_index_cache[window_size]

    def dice(self, word_a, word_b, window_size=None):
        '''
        Use dice coefficient
        :param word_1:
        :param word_2:
        :param window_size:
        :return:
        '''

        # Create window-word index
        word_windows_index = self.get_word_windows_index(window_size)

        # Lookup filename in word_files_index
        files_a = word_windows_index[word_a]
        files_b = word_windows_index[word_b]
        files_a_sliced_b = list(set(files_b) & set(files_a))

        dice_coef = float(len(files_a_sliced_b)) / (len(files_a) + len(files_b))
        return dice_coef

    def mim(self, word_a, word_b, window_size=None):
        '''
        User Mutual Information Measure
        :param word_a:
        :param word_b:
        :param window_size:
        :return:
        '''

        # Create window-word index
        word_windows_index = self.get_word_windows_index(window_size)

        # Lookup filename in word_files_index
        files_a = word_windows_index[word_a]
        files_b = word_windows_index[word_b]
        files_a_sliced_b = list(set(files_b) & set(files_a))

        mim_coef = float(len(files_a_sliced_b)) / (len(files_a) * len(files_b))
        return mim_coef

    def emim(self, word_a, word_b, window_size=None):
        '''
        Use Expected Mutual Information Measure
        :param word_a:
        :param word_b:
        :param window_size:
        :return:
        '''

        # Get window-words and word-windows index
        window_words_index = self.get_window_words_index(window_size)
        word_windows_index = self.get_word_windows_index(window_size)

        # Lookup filename in word_files_index
        files_a = word_windows_index[word_a]
        files_b = word_windows_index[word_b]
        files_a_sliced_b = list(set(files_b) & set(files_a))

        if len(files_a_sliced_b) > 0:
            emim_coef = len(files_a_sliced_b) * \
                        math.log(len(window_words_index) * len(files_a_sliced_b) / float(len(files_a) * len(files_b)))
        else:
            emim_coef = 0.0

        return emim_coef

    def chi_square(self, word_a, word_b, window_size=None):
        '''
        Chi-Square Measure
        :param word_a:
        :param word_b:
        :param window_size:
        :return:
        '''

        # Get window-words and word-windows index
        window_words_index = self.get_window_words_index(window_size)
        word_windows_index = self.get_word_windows_index(window_size)

        # Lookup filename in word_files_index
        files_a = word_windows_index[word_a]
        files_b = word_windows_index[word_b]
        files_a_sliced_b = list(set(files_b) & set(files_a))

        chi_sqr_coef = math.pow((len(files_a_sliced_b) -
                                 (float(len(files_a) * len(files_b)) / len(window_words_index))), 2) / \
                       float(len(files_a) * len(files_b))
        return chi_sqr_coef


def get_most_associates(most_associated):
    most_associated_sorted = {}
    for word, associates in most_associated.items():
        associates = sorted(associates, key=lambda x: x[1], reverse=True)
        if len(associates) > 10: associates = associates[:10]

        most_associated_sorted[word] = associates


    return most_associated_sorted


if __name__ == '__main__':
    selected_words = ['abolishes', 'access', 'accommodate', 'accredited', 'sky',
                      'railroad', 'calendar', 'airplane', 'airplane', 'bicycle']

    measure = AssociationMeasure('../6_1/1_2_file_words_index.txt')

    # Get all words and create all possible bigrams
    all_word = measure.get_word_windows_index().keys()
    all_bigrams = bigrams = list(nltk.bigrams(all_word))

    # Calculate coocurence
    most_associated_all_d = {}
    most_associated_all_m = {}
    most_associated_all_e = {}
    most_associated_all_c = {}

    # most_associated_5_d = {}
    # most_associated_5_m = {}
    # most_associated_5_e = {}
    # most_associated_5_c = {}

    print all_word
    for word in selected_words:
        for word_a, word_b in all_bigrams:
            if word == word_a or word == word_b:
                dice_window_size_all = measure.dice(word_a, word_b)
                mim_window_size_all = measure.mim(word_a, word_b)
                emim_window_size_all = measure.emim(word_a, word_b)
                chi_square_window_size_all = measure.chi_square(word_a, word_b)

                # Use window-size = 5
                dice_window_size_5 = measure.dice(word_a, word_b, 5)
                mim_window_size_5 = measure.mim(word_a, word_b, 5)
                emim_window_size_5 = measure.emim(word_a, word_b, 5)
                chi_square_window_size_5 = measure.chi_square(word_a, word_b, 5)

                most_associated_all_d.setdefault(word, [])
                most_associated_all_m.setdefault(word, [])
                most_associated_all_e.setdefault(word, [])
                most_associated_all_c.setdefault(word, [])

                # most_associated_5_d.setdefault(word, [])
                # most_associated_5_m.setdefault(word, [])
                # most_associated_5_e.setdefault(word, [])
                # most_associated_5_c.setdefault(word, [])

                most_associated_all_d[word].append((word_a if word_b == word else word_b, dice_window_size_all))
                most_associated_all_m[word].append((word_a if word_b == word else word_b, mim_window_size_all))
                most_associated_all_e[word].append((word_a if word_b == word else word_b, emim_window_size_all))
                most_associated_all_c[word].append((word_a if word_b == word else word_b, chi_square_window_size_all))

                # most_associated_5_d[word].append((word_a if word_b == word else word_b, dice_window_size_5))
                # most_associated_5_m[word].append((word_a if word_b == word else word_b, mim_window_size_5))
                # most_associated_5_e[word].append((word_a if word_b == word else word_b, emim_window_size_5))
                # most_associated_5_c[word].append((word_a if word_b == word else word_b, chi_square_window_size_5))


        # Sort ascending and get top 10
        most_associated_all_d = get_most_associates(most_associated_all_d)
        most_associated_all_m = get_most_associates(most_associated_all_m)
        most_associated_all_e = get_most_associates(most_associated_all_e)
        most_associated_all_c = get_most_associates(most_associated_all_c)

        # most_associated_5_d = get_most_associates(most_associated_5_d)
        # most_associated_5_m = get_most_associates(most_associated_all_d)
        # most_associated_5_e = get_most_associates(most_associated_5_e)
        # most_associated_5_e = get_most_associates(most_associated_5_e)

        print most_associated_all_d








    # # a. Find 10 words randomly =================================================================
    # stemmed_words_index = measure.get_stemmed_words_index(measure.get_window_words_index())
    #
    # # List only non-stop-words
    # nltk.download('stopwords')
    # stemmed_words= [stemmed_word for stemmed_word, words in stemmed_words_index.items()
    #                 if stemmed_word not in stopwords.words('english')]
    #
    # # Find 10 stemmed-words randomly
    # stemmed_words = random.sample(stemmed_words, 10)
    #
    #
    # # b. Calculate co-occurence measure with window_size = 5 and window_size = full-document ===
    # for word in stemmed_words:
    #     # get words in stemmed-word-class
    #     words = stemmed_words_index[word]
    #     # create bigrams for words
    #     bigrams = list(nltk.bigrams(words))
    #
    #     for word_a, word_b in bigrams:
    #         # Use window-size = all document
    #         dice_window_size_all = measure.dice(word_a, word_b)
    #         mim_window_size_all = measure.mim(word_a, word_b)
    #         emim_window_size_all = measure.emim(word_a, word_b)
    #         chi_square_window_size_all = measure.chi_square(word_a, word_b)
    #
    #         # Use window-size = 5
    #         dice_window_size_5 = measure.dice(word_a, word_b, 5)
    #         mim_window_size_5 = measure.mim(word_a, word_b, 5)
    #         emim_window_size_5 = measure.emim(word_a, word_b, 5)
    #         chi_square_window_size_5 = measure.chi_square(word_a, word_b, 5)
    #
    #         print(u'Word class {} : {} - {} :'.format(word, word_a, word_b))
    #
    #         print('\tUsing dice coefficient')
    #         print('\t\tWindow size = all --> {}'.format(dice_window_size_all))
    #         print('\t\tWindow size = {} --> {}'.format(5, dice_window_size_5))
    #
    #         print('\tUsing MIM coefficient')
    #         print('\t\tWindow size = all --> {}'.format(mim_window_size_all))
    #         print('\t\tWindow size = {} --> {}'.format(5, mim_window_size_5))
    #
    #         print('\tUsing EMIM coefficient')
    #         print('\t\tWindow size = all --> {}'.format(emim_window_size_all))
    #         print('\t\tWindow size = {} --> {}'.format(5, emim_window_size_5))
    #
    #         print('\tUsing Chi-square coefficient')
    #         print('\t\tWindow size = all --> {}'.format(chi_square_window_size_all))
    #         print('\t\tWindow size = {} --> {}'.format(5, chi_square_window_size_5))
