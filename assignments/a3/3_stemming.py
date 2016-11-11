import json
from krovetzstemmer import Stemmer as KrovetzStemmer
import unicodecsv as csv
from prettyprint import prettyprint


# Instantiate krovetz stemmer
krovetz = KrovetzStemmer()


# Read result of 1_index
with open('1_2_index.txt', 'rb') as f:
    str_word_files_index = f.read()
    word_files_index =  json.loads(str_word_files_index)

    stem_word_index = {}
    for word, files in word_files_index.items():
        # Stem word using krovetz
        stemmed_word = krovetz.stem(word)

        # Group by stemmed word
        stem_word_index.setdefault(stemmed_word, [])
        stem_word_index[stemmed_word].append(word)


    for stemmed_word, words in stem_word_index.items():
        print(u'{}: {}'.format(stemmed_word, ', '.join(words)))


    print ''
    filename = '3_stemmed_words.csv'
    with open(filename, 'wb') as f:
        print('Writing to file {}'.format(filename))

        writer = csv.writer(f)
        for stemmed_word, words in stem_word_index.items():
            writer.writerow((stemmed_word, ', '.join(words)))

        print('Done!')