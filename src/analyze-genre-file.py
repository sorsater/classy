'''
Analyzes a genre file by calculating number of songs in each genre.

Used for exploring if features could be used
'''

import sys
import json
from collections import Counter
import nltk
import os
import pprint
import numpy as np
import random
from matplotlib import pyplot as plt
import math
from w8m8 import progressbar

if len(sys.argv) < 4:
    print('Provide args: 1: json file, 2: feature (words,unique,chars), 3: genres after each other')
    file_name = 'billboard.json'
    feature = 'words'
    genres = ['country', 'rap']
else:
    file_name = sys.argv[1]
    feature = sys.argv[2]
    genres = sys.argv[3:]


data = json.load(open(file_name))
print('GENRES')
print(genres)
analyzer = {genre: {'chars': [], 'words': [], 'unique': []} for genre in genres}

# Analyze length of song/number of unique words
for idx, (artist, song, genre) in data.items():
    progressbar((int(idx)+1)/len(data))
    if not genre in genres:
        continue
    file_path = os.path.join('lyrics', '{}~{}'.format(artist.replace('/', ''), song.replace('/', '')))
    if os.path.exists(file_path):
        lyrics = open(file_path).read()

        tokenized_lyrics = nltk.wordpunct_tokenize(lyrics)
        num_chars = len(lyrics)
        num_words = len(tokenized_lyrics)
        num_unique = len(set(tokenized_lyrics))

        analyzer[genre]['chars'].append(num_chars)
        analyzer[genre]['words'].append(num_words)
        analyzer[genre]['unique'].append(num_unique)

print()
hist_data = []
bin_data = []
for genre in genres:
    hist_data.append(analyzer[genre][feature])
    bin_data += analyzer[genre][feature]

bins = np.linspace(math.ceil(min(bin_data)), math.floor(max(bin_data)), 20) # Number of bins

plt.xlim([min(bin_data)-5, max(bin_data)+5])
import matplotlib.patches as mpatches
import matplotlib.pyplot as plt
cols = ['green', 'red', 'blue', 'yellow', 'pink']
patches = []
for idx in range(len(genres)):
    plt.hist(hist_data[idx], bins=bins, alpha=0.5, color=cols[idx], label=genre[idx], normed=True)
    patches.append(mpatches.Patch(color=cols[idx], label=genres[idx]))

plt.title('Genres: {}'.format(', '.join(genres)))
plt.xlabel('num of: {}'.format(feature))
plt.legend(handles=patches)
plt.ylabel('Normalized count')

plt.show()
