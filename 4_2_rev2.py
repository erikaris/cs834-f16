import io
import os
import html2text
import unicodecsv as csv

html_files = []
# traverse the directory to list all the html files in the directory
for root, dirs, files in os.walk(os.path.abspath('./articles')):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            html_files.append(filepath)

corpus = []
voc_corpus = []
# process each html file
for idx, file in enumerate(html_files):
    print('{} of {}. Processing {}'.format(idx + 1, len(html_files), file))
    print('=' * 30)

    # get text only from each file -> remove all tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    # get all words from text by splitting by whitespace
    tokens = []
    for word in text.split():
        if word.isalnum():
            tokens.append(word)

    # corpus is cummulative of tokens
    corpus += tokens
    # voc is unique list of corpus
    vocs = set(corpus)

    # count the size of corpus and vocabularies in the docs[file]
    voc_corpus.append([idx+1, len(corpus), len(vocs)])

print('\n\n the size of corpus {}'.format(len(corpus)))
print('\n\n the size of vocabularies {}'.format(len(vocs)))

out_file = os.path.join(os.getcwd(), '4_2-voc_corpus.csv')
with open(out_file, "wb") as f:
    writer = csv.writer(f)
    writer.writerow(["docs", "corpus_size", "vocabulary_size"])
    writer.writerows(voc_corpus)


# Process reverse list
print('\n\n Processing reverse list...')
html_files.reverse()


corpus = []
voc_corpus = []
# process each html file
for idx, file in enumerate(html_files):
    print('{} of {}. Processing {}'.format(idx + 1, len(html_files), file))
    print('=' * 30)

    # get text only from each file -> remove all tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    # get all words from text by splitting by whitespace
    tokens = []
    for word in text.split():
        if word.isalnum():
            tokens.append(word)

    # corpus is cummulative of tokens
    corpus += tokens
    # voc is unique list of corpus
    vocs = set(corpus)

    # count the size of corpus and vocabularies in the docs[file]
    voc_corpus.append([idx+1, len(corpus), len(vocs)])

print('\n\n the size of corpus in reverse order {}'.format(len(corpus)))
print('\n\n the size of vocabularies in reverse order {}'.format(len(vocs)))

out_file = os.path.join(os.getcwd(), '4_2-voc_corpus_reverse.csv')
with open(out_file, "wb") as f:
    writer = csv.writer(f)
    writer.writerow(["docs", "corpus_size", "vocabulary_size"])
    writer.writerows(voc_corpus)
