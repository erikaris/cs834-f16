import os
from pprint import pprint

import unicodecsv as csv
from bs4 import BeautifulSoup
from tabulate import tabulate

html_files = []
# traverse the directory to list all the html files in the directory
for root, dirs, files in os.walk(os.path.abspath('./articles')):
    for file in files:
        if file.endswith('.html'):
            filepath = os.path.join(root, file)
            html_files.append(filepath)

all_links = {}
all_anchor_text = {}
# process each html file
for idx, file in enumerate(html_files):
    # just for debugging
    print('{} of {}. Processing {}'.format(idx+1, len(html_files), file))
    print('=' * 30)

    # find all anchors
    soup = BeautifulSoup(open(file), 'html.parser')
    anchors = soup.find_all('a', href=True)
    print('Found {} anchors'.format(len(anchors)))

    for a in anchors:
        link = a['href']
        # anchor text
        text = a.string or ''

        # In this case, link is relative path points to other html file
        # just process non http link
        if not link.startswith('http'):
            try:
                # convert to absolute path
                link = os.path.join(os.path.dirname(file), link)
                link = os.path.abspath(link)
            except:
                pass

        # all_link : key is source, value is list of destination
        all_links.setdefault(file, [])
        # all_anchor_text : key is source, value is list of anchor text
        all_anchor_text.setdefault(file, [])

        # append only if:
        # - file != link
        # - all_links[file] do not contain link
        # - link is file --> ignore http
        if file != link and link not in all_links[file] and os.path.isfile(link):
            all_links[file].append(link)
            all_anchor_text[file].append(text)

link_freq = {}
link_text = {}
for src in all_links:
    # all destinations in each src
    dests = all_links[src]
    # all anchor text in each src
    texts = all_anchor_text[src]

    for idx, dest in enumerate(dests):
        link_freq.setdefault(dest, 0)
        link_freq[dest] += 1

        link_text.setdefault(dest, [])
        link_text[dest].append(texts[idx])

# convert dict to 2d list
link_freq_table = []
for link in link_freq:
    link_freq_table.append([link, link_freq[link]])

# sort list by freq (2nd column)
link_freq_table = sorted(link_freq_table, key=lambda x:x[1], reverse=True)

# append anchor texts in 3rd column
tmp_link_freq_table = []
for row in link_freq_table:
    # append anchor texts in 3rd column
    row += [u', '.join(set(link_text[row[0]]))]
    # convert full-path link to filename only
    row[0] = os.path.basename(row[0])
    tmp_link_freq_table.append(row)
link_freq_table = tmp_link_freq_table

# process only top 10 results
link_freq_table = link_freq_table[:10]

# write the output to csv file
out_file = os.path.join(os.getcwd(), '4_8-link_freq.csv')
with open(out_file, "wb") as f:
    writer = csv.writer(f)
    writer.writerow(["link", "frequency", "texts"])
    writer.writerows(link_freq_table)

# print the resulting table
print tabulate(link_freq_table, headers=["link", "frequency", "texts"])
