import json
import string
from HTMLParser import HTMLParser

import htmlmin as htmlmin
import requests


# HTMLEncoder is extent of HTMLParser
class HTMLEncoder(HTMLParser):
    _tags = []      # convention for private variable

    def handle_starttag(self, tag, attrs):
        # Append to array, with type 'starttag'
        self._tags.append(((tag, attrs), 'starttag'))

    def handle_endtag(self, tag):
        # Append to array, with type 'endtag'
        self._tags.append((tag, 'endtag'))

    def handle_data(self, data):
        # Append to array, with type 'data'
        self._tags.append((data, 'data'))

    def make_chars(self, number):
        num_char = int(number/len(string.lowercase))
        rem = number - (num_char * len(string.lowercase))

        chars = ''.join([string.lowercase[len(string.lowercase)-1] for i in range(0,num_char)]) + \
                string.lowercase[rem]

        return chars

    def encode(self, html):
        # Process normal html with HTMLParser
        self.feed(html)
        self.close()

        # After parsing is done, process array _tags
        tag_list = []
        minified_html = ''
        for data, type in self._tags:
            if type == 'starttag':
                (tag, attrs) = data

                if not tag in tag_list: # jika tag blm tercantum di tag list, maka append.
                    tag_list.append(tag)

                # Process attrs of tag, e.g:
                # [('href', 'http://...'), ('title', 'Some link')] become
                # <a href='http://...' title='Some link'>
                str_attrs = ' '.join(['{}="{}"'.format(name, val) for name, val in attrs])

                # Append encoded tag and it's attrs into var html
                encoded_tag = self.make_chars(tag_list.index(tag))  # convert index dari int menjadi char.
                minified_html += '<{}{}>'.format(
                    encoded_tag, (' ' if str_attrs else '') + str_attrs
                )
            elif type == 'endtag':
                # Append encoded end-tag into var html
                encoded_tag = self.make_chars(tag_list.index(tag))
                minified_html += '</{}>'.format(encoded_tag)
            elif type == 'data':
                # Append data into var html
                minified_html += data

        # Process json of definition as a comment
        definitions = '<!--{}-->'.format(   ## konversti tag list.
            json.dumps({ self.make_chars(key): val for key, val in enumerate(tag_list) })
        )

        # Return definition and minified html
        return definitions + minified_html      ## concatenate definition dengan minified.


# Capture input from keyboard
url = raw_input("Enter a URL: ")
url = url.strip()

# Crawl URL with requests, methods GET
resp = requests.get(url)

# Process only if status code 200
if resp.status_code == 200:
    # Instantiate the our html encoder
    encoder = HTMLEncoder()
    # Encode text
    html = resp.text.encode('utf-8').strip()
    enc_html = encoder.encode(html)

    print enc_html


else:
    print('Debug : Cannot open URL {}, Status code: {}'.format(url, resp.status_code))
