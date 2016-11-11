import os
import html2text as html2text
import io

import prettyprint as prettyprint

html_files = []
# traverse the directory to list all the html files in the directory
for root, dirs, files in os.walk(os.path.abspath('../articles')):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            html_files.append(filepath)


file_words_index = {}
all_words = set()

# process each html file
for idx, file in enumerate(html_files):
    print('{} of {}. Processing file {}'.format(idx+1, len(html_files), file))
    print('=' * 30)

    # get text only from each file -> remove all tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    # get all words from text by splitting by whitespace
    words = [word.lower() for word in text.split() if word.isalpha()]
    all_words |= set(words)
    file_words_index[os.path.basename(file)] = words


# Select 1000 top words
all_words = sorted(list(all_words))
all_words = all_words[:1000]


word_files_index = {}

# Invert words and files
for idx, word in enumerate(all_words):
    print('{} of {}. Processing word {}'.format(idx + 1, len(all_words), word.encode('utf-8')))
    print('=' * 30)

    files = []
    for file, words in file_words_index.items():
        if word in words:
            files.append(file)
    word_files_index[word] = sorted(set(files))


filename = '1_2_index.txt'
with open(filename, 'wb') as f:
    print('Writing to file {}'.format(filename))

    str_word_files_index = prettyprint.pp_str(word_files_index)
    f.write(str_word_files_index)

    print('Done!')