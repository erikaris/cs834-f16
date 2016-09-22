import hashlib
import os
from urlparse import urljoin

import errno
import requests as requests
import time
from bs4 import BeautifulSoup
from requests.exceptions import InvalidSchema


def open_url(level, idx, url, outdir):
    url = url.strip()

    # Hashing URL as a output file
    outfile = os.path.join(outdir, hashlib.md5(url).hexdigest() + '.html')
    listfile = os.path.join(outdir, 'urls.csv')

    # Crawl URL with requests, methods GET
    print('Debug : {}.{} Opening URL {}'.format(level+1, idx+1, url))

    try:
        resp = requests.get(url)

        # Process only if status code 200
        if resp.status_code == 200:
            print('Debug : {}.{} URL {} is opened'.format(level+1, idx+1, url))

            html = resp.text

            # Save html to outfile
            with open(outfile, 'w') as of:
                of.write(html.encode('utf-8'))
                print('Debug : {} is saved into {}'.format(url, outfile))

            # Save url to list
            with open(listfile, 'a') as f:
                f.write(url + '\n')

            # Parse HTML with beautiful soup
            soup = BeautifulSoup(html, 'html.parser')
            # Find all anchors, <a> tag
            links = soup.find_all('a')

            # Get href attribute from tag <a>
            hrefs = []
            for link in links:
                href = link.get('href')

                # Make url absolute
                # Sometimes url in tag <a> is not a full url, without schema and host
                # e.g: <a href="/folder/a.html">...</a>
                href = urljoin(url, href)

                hrefs.append(href)

            return hrefs
        else:
            print('Debug : {}.{} Cannot open URL {}, Status code: {}'.format(level+1, idx+1, url,
                                                                             resp.status_code))
    except:
        pass


# Capture input from keyboard
url = raw_input("Enter a URL: ")

depth = raw_input("Enter crawl depth or level: ")
depth = int(depth)

outdir = raw_input("Enter output directory: ")
# Make directory if not exists
try:
    os.makedirs(outdir)
except OSError as exc:
    if exc.errno != errno.EEXIST:
        raise

links = [url, ]

level = -1
while level < depth:
    # Prepare childre_links to save newly founded links
    children_links = []
    for idx, link in enumerate(links):
        # open_url will return new list of links founded in link
        new_links = open_url(level, idx, link, outdir)
        if new_links:
            print('Debug : Found {} links'.format(len(new_links)))
            children_links = children_links + new_links

        # Sleep for 5 seconds
        print('Debug : Sleep for 5 seconds')
        time.sleep(5)

    # After all links are processed, set links with children_links and increase level
    links = children_links
    level += 1
