import io
import sys

import html2text as html2text
import krovetzstemmer
from nltk import PorterStemmer

# Instantiate porter stemmer
porter = PorterStemmer()
krovetz = krovetzstemmer.Stemmer()

if len(sys.argv) < 6:
    print('Usage :')
    print('python 4_6.py <file_1> ... <file_5>')

# Assuming all arguments are file
files = []
for arg in range(1, len(sys.argv)):
    files.append(sys.argv[arg])

# Get contents of each file
results = {}
for idx, file in enumerate(files):
    print('{} of {}. Processing {}'.format(idx + 1, len(files), file))
    print('=' * 30)

    # get text content
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    # remove whitespace
    words = []
    for word in text.split():
        if word.isalpha():
            words.append(word.lower())
    text = u' '.join(words)

    porter_result = []
    krovetz_result = []
    for c in words:
        porter_result.append(porter.stem(c))
        krovetz_result.append(krovetz.stem(c))

    results[file] = {}
    results[file]['original'] = text
    results[file]['porter'] = u' '.join(porter_result)
    results[file]['krovetz'] = u' '.join(krovetz_result)

# print results
txt_results = []
for file in results:
    txt_results.append(u'Stemmer result of {}'.format(file))
    txt_results.append(u'{}'.format('=' * 60))
    txt_results.append(u'Original text \t= {}\n'.format(results[file]['original']))
    txt_results.append(u'Porter result \t= {}\n'.format(results[file]['porter']))
    txt_results.append(u'Krovetz result \t= {}\n'.format(results[file]['krovetz']))

    num_stems_porter = len(set(results[file]['porter'].split()))
    txt_results.append(u'Number of stems produced by Porter \t= {}\n'.format(num_stems_porter))

    num_stems_krovetz = len(set(results[file]['krovetz'].split()))
    txt_results.append(u'Number of stems produced by Krovetz \t= {}\n'.format(num_stems_krovetz))
    txt_results.append(u'\n')

    print(u'\n'.join(txt_results))

    # also write to file
    f = io.open('4_6-result.txt', "w", encoding="utf-8")
    for txt_result in txt_results:
        f.write(txt_result + '\n')
