import unicodecsv as csv
import io
import os
import sys

import html2text
from tabulate import tabulate

# Assuming all arguments are file
files = []
for arg in range(1, len(sys.argv)):
    files.append(sys.argv[arg])

file_words_index = {}
all_words = set()

# Read all files
for file in files:
    # get text content
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    words = [word.lower() for word in text.split() if word.isalpha()]
    all_words |= set(words)
    file_words_index[file.split(os.pathsep)[-1]] = words

# Invert words and files
word_files_index = {}
for word in all_words:
    files = []
    for file, words in file_words_index.items():
        if word in words:
            files.append(file)
    word_files_index[word] = sorted(set(files))

# Convert to 2d array
table = []
for word in word_files_index:
    table.append([word, u', '.join(word_files_index[word])])

print tabulate(table, headers=["word", "files"])

# write the output to csv file
out_file = os.path.join(os.getcwd(), '5_8-inverted_index.csv')
with open(out_file, "wb") as f:
    writer = csv.writer(f)
    writer.writerow(["word", "files"])
    writer.writerows(table)
