'''
Analyzes a genre file by calculating number of songs in each genre.

Used for exploring if features could be used
'''

import sys
import json
from collections import Counter
import os
import nltk
import numpy as np
import random
from matplotlib import pyplot as plt
import matplotlib.patches as mpatches
import math
from w8m8 import progressbar
import argparse

alpha = 0.6
colors = ['green', 'red', 'blue', 'yellow', 'pink', 'black']
folder_name = 'plots'
all_genres = ['country', 'electronic', 'pop', 'rap', 'rock', 'rob']

if not os.path.exists(folder_name):
    os.makedirs(folder_name)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file', default='billboard.json', help='File to analyze')
    parser.add_argument('--type', default='words', choices=['chars', 'words', 'unique'], help='Type to analyze')
    parser.add_argument('--genres', nargs='*', default='all', help='Genres to consider')

    return parser.parse_args()

def read_data(args):
    data = json.load(open(args.file))
    analyzer = {genre: {'chars': [], 'words': [], 'unique': []} for genre in args.genres}

    cntr = 0
    # Analyze length of song/number of unique words
    for idx, (artist, song, genre) in data.items():
        progressbar((int(idx)+1)/len(data))
        if not genre in args.genres:
            continue
        file_path = os.path.join('lyrics', '{}~{}'.format(artist.replace('/', ''), song.replace('/', '')))
        if os.path.exists(file_path):
            lyrics = open(file_path).read()
            tokenized_lyrics = nltk.wordpunct_tokenize(lyrics)

            analyzer[genre]['chars'].append(len(lyrics))
            analyzer[genre]['words'].append(len(tokenized_lyrics))
            analyzer[genre]['unique'].append(len(set(tokenized_lyrics)))

            cntr += 1
    print()
    print('Analyzed {} songs'.format(cntr))

    hist_data = []
    bin_data = []
    for genre in args.genres:
        hist_data.append(analyzer[genre][args.type])
        bin_data += analyzer[genre][args.type]

    return hist_data, bin_data

def plot_data(args, hist_data, bin_data):
    fig = plt.figure()

    bins = np.linspace(math.ceil(min(bin_data)), math.floor(max(bin_data)), 20) # Number of bins

    plt.xlim([min(bin_data)-5, max(bin_data)+5])

    patches = []
    for idx in range(len(args.genres)):
        plt.hist(hist_data[idx], bins=bins, alpha=alpha, color=colors[idx], normed=True)
        patches.append(mpatches.Patch(color=colors[idx], alpha=alpha, label=args.genres[idx]))

    plt.title('Genres: {}'.format(', '.join(args.genres)))
    plt.xlabel('Num of: {}'.format(args.type))
    plt.legend(handles=patches)
    plt.ylabel('Normalized count')

    #plt.show()
    plt.draw()
    plt.pause(1)

    ans = input('Press enter to close, "s" to save: ')

    if ans.lower() == 's':
        print('Saving')
        plt.savefig('{}/{}-{}.png'.format(folder_name, args.type, '_'.join(args.genres)))

    plt.close(fig)

if __name__ == '__main__':
    args = parse_args()
    if 'all' in args.genres:
        args.genres = all_genres

    hist_data, bin_data = read_data(args)

    plot_data(args, hist_data, bin_data)







