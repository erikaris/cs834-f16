import json
import nltk as nltk
from tabulate import tabulate
import unicodecsv as csv
from prettyprint import prettyprint
import networkx as nx
import matplotlib.pyplot as plt

dice_coef_threshold = 0.01
stem_clusters = []

# Read result of 1_2_index.txt
with open('1_2_index.txt', 'rb') as f1:
    word_files_index = json.loads(f1.read())

    # Read result of 3_stemmed_words.csv
    with open('3_stemmed_words.csv', 'rb') as f3:
        for stemmed_word, words in csv.reader(f3):
            words = words.split(', ')

            # create bigrams from words
            bigrams = list(nltk.bigrams(words))
            for word_a, word_b in bigrams:
                # Lookup filename in word_files_index
                files_a = word_files_index[word_a]
                files_b = word_files_index[word_b]
                files_a_sliced_b = list(set(files_b) & set(files_a))

                dice_coef = float(2 * len(files_a_sliced_b)) / (len(files_a) + len(files_b))

                if(dice_coef > dice_coef_threshold):
                    stem_clusters.append((stemmed_word, word_a, word_b, dice_coef))


stem_clusters = sorted(stem_clusters, key=lambda x: x[3], reverse=True)
# print tabulate(stem_clusters, headers=['stemmed_word', 'word_a', 'word_b', 'dice_coef'])

filename = '4_dice_coeficient.csv'
with open(filename, 'wb') as f:
    print('Writing to file {}'.format(filename))

    writer = csv.writer(f)
    for stemmed_word, word_a, word_b, dice_coef in stem_clusters:
        writer.writerow((stemmed_word, word_a, word_b, dice_coef))


# Create graph
stemmed_word_data = {}
for stemmed_word, word_a, word_b, dice_coef in stem_clusters:
    stemmed_word_data.setdefault(stemmed_word, [])
    stemmed_word_data[stemmed_word].append((word_a, word_b, dice_coef))

stemmed_word_clusters = {}
for stemmed_word, data in stemmed_word_data.items():
    G=nx.MultiGraph()

    labels = {}
    for word_a, word_b, dice_coef in data:
        G.add_edge(word_a, word_b, weight=dice_coef, label=dice_coef)
        labels[(word_a, word_b)] = dice_coef

    # export connected components into list
    stemmed_word_clusters[stemmed_word] = list(nx.connected_components(G))

    nx.draw(G, with_labels=True)
    nx.draw_networkx_edge_labels(G, pos=nx.spring_layout(G), edge_labels=labels)

    filename = '4_graph_{}.png'.format(stemmed_word)
    print('Saving graph {}'.format(filename))
    plt.savefig(filename, format='PNG')
    plt.clf()

print('Draw graphics done!')

print('Print stem clusters...')

for stemmed_word, connected_nodes in stemmed_word_clusters.items():
    for connected_node in connected_nodes:
        print(u'{}\t: {}'.format(stemmed_word, ', '.join(connected_node)))

print('Print stem clusters done')