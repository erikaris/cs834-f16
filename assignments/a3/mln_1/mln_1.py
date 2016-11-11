import io
import math
import os
from krovetzstemmer import Stemmer as KrovetzStemmer

import html2text
import matplotlib.pyplot as plt
import networkx as nx
import nltk


# Create graph function
def create_graph(stem_data, metric_name):
    stemmed_word_data = {}
    for stemmed_word, word_a, word_b, coef in stem_data:
        stemmed_word_data.setdefault(stemmed_word, [])
        stemmed_word_data[stemmed_word].append((word_a, word_b, coef))

    stemmed_word_clusters = {}
    for stemmed_word, data in stemmed_word_data.items():
        G = nx.MultiGraph()

        labels = {}
        for word_a, word_b, coef in data:
            G.add_edge(word_a, word_b, weight=coef, label=coef)
            labels[(word_a, word_b)] = coef

        # export connected components into list
        stemmed_word_clusters[stemmed_word] = list(nx.connected_components(G))

        nx.draw(G, with_labels=True)
        nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G), edge_labels=labels)

        filename = '{}_graph_{}.png'.format(metric_name, stemmed_word)
        print('Saving graph {}'.format(filename))
        plt.savefig(filename, format='PNG')
        plt.clf()

    return stemmed_word_clusters


# Print stem cluster function
def print_stem_cluster(stemmed_word_clusters, metric_name):
    print('\n')
    print('Clusters using metric {}'.format(metric_name))
    print('==================================')

    for stemmed_word, connected_nodes in stemmed_word_clusters.items():
        for connected_node in connected_nodes:
            print(u'{}\t: {}'.format(stemmed_word, ', '.join(connected_node)))


# List all files ===========================================================================================
html_files = []
for root, dirs, files in os.walk(os.path.abspath('/media/erikaris/DATA/ODU/Semester 3/intro_to_info_retrieval/assignments/a2/code_report/articles/z')):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            html_files.append(filepath)


file_words_index = {}
all_words = set()
window_text_number = 100

# Index all words and files ================================================================================
for idx, file in enumerate(html_files):
    print('{} of {}. Processing file {}'.format(idx+1, len(html_files), file))
    print('=' * 30)

    # get text only from each file -> remove all tags
    h = html2text.HTML2Text()
    h.ignore_links = True
    text = h.handle(u' '.join([line.strip() for line in io.open(file, "r", encoding="utf-8").readlines()]))

    # get all words from text by splitting by whitespace
    words = [word.lower() for word in text.split() if word.isalpha()]

    # make text window containing 50 - 100 words
    for w in range(1, int(len(words)/window_text_number)):
        start = (w-1)*window_text_number
        end = w*window_text_number
        if end > len(words): end = len(words)

        window_words = words[start:end]

        all_words |= set(window_words)
        file_words_index[os.path.basename(file) + '_part_' + str(w)] = window_words


# # Remove stopword to purify result ========================================================================
# nltk.download('stopwords')
# all_words = [word for word in all_words if word not in stopwords.words('english')]
#
#
# # Select random 10 words ==================================================================================
# all_words = random.sample(all_words, 10)


# Invert words and files index ============================================================================
word_files_index = {}
for idx, word in enumerate(all_words):
    print('{} of {}. Processing word {}'.format(idx + 1, len(all_words), word.encode('utf-8')))
    print('=' * 30)

    files = []
    for file, words in file_words_index.items():
        if word in words:
            files.append(file)
    word_files_index[word] = sorted(set(files))


# Stem words ==============================================================================================
krovetz = KrovetzStemmer()
stem_word_index = {}
for word, files in word_files_index.items():
    # Stem word using krovetz
    stemmed_word = krovetz.stem(word)

    # Group by stemmed word
    stem_word_index.setdefault(stemmed_word, [])
    stem_word_index[stemmed_word].append(word)


# Calculate coefficient ==================================================================================
coef_threshold = 0.0

dice_stemmed_word_data = []
mim_stemmed_word_data = []
emim_stemmed_word_data = []
chi_sqr_stemmed_word_data = []

counter = 0
for stemmed_word, words in stem_word_index.items():
    # create bigrams from words
    bigrams = list(nltk.bigrams(words))
    for word_a, word_b in bigrams:
        # Lookup filename in word_files_index
        files_a = word_files_index[word_a]
        files_b = word_files_index[word_b]
        files_a_sliced_b = list(set(files_b) & set(files_a))

        # Using dice coef
        dice_coef = float(len(files_a_sliced_b)) / (len(files_a) + len(files_b))
        if (dice_coef > coef_threshold):
            dice_stemmed_word_data.append((stemmed_word, word_a, word_b, dice_coef))

        # Using MIM coef
        mim_coef = float(len(files_a_sliced_b)) / (len(files_a) * len(files_b))
        if (mim_coef > coef_threshold):
            mim_stemmed_word_data.append((stemmed_word, word_a, word_b, mim_coef))

        # Using EMIM coef
        if len(files_a_sliced_b) > 0:
            emim_coef = len(files_a_sliced_b) * \
                        math.log(len(file_words_index) * len(files_a_sliced_b) / float(len(files_a) * len(files_b)))
        else:
            emim_coef = 0.0

        if (emim_coef > coef_threshold):
            emim_stemmed_word_data.append((stemmed_word, word_a, word_b, emim_coef))

        # Chi-square
        chi_sqr_coef = math.pow((len(files_a_sliced_b) - (float(len(files_a) * len(files_b)) / len(file_words_index))), 2) / \
                       float(len(files_a) * len(files_b))
        if (chi_sqr_coef > coef_threshold):
            chi_sqr_stemmed_word_data.append((stemmed_word, word_a, word_b, chi_sqr_coef))

    if len(bigrams) > 0: counter+=1
    if counter >= 10: break



# Create graph
dice_stemmed_word_clusters = create_graph(dice_stemmed_word_data, 'dice')
mim_stemmed_word_clusters = create_graph(mim_stemmed_word_data, 'mim')
emim_stemmed_word_clusters = create_graph(emim_stemmed_word_data, 'emim')
chi_sqr_stemmed_word_clusters = create_graph(chi_sqr_stemmed_word_data, 'chi_sqr')

# Print clusters
print_stem_cluster(dice_stemmed_word_clusters, 'dice')
print_stem_cluster(mim_stemmed_word_clusters, 'mim')
print_stem_cluster(emim_stemmed_word_clusters, 'emim')
print_stem_cluster(chi_sqr_stemmed_word_clusters, 'chi_sqr')
