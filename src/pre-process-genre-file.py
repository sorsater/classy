'''
Detects which language text is written in.
Makes use of the stopwords in each language.

Code based on:
http://www.algorithm.co.il/blogs/programming/python/cheap-language-detection-nltk/
'''

import nltk
import json
import os
import argparse
from w8m8 import progressbar

def parse_args():
    '''
    Parse arguments.
    Only required argument is .json file with artist, song, genres and an output file
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, help='Name of json file')
    parser.add_argument('output_file', type=str, help='Name of output file')
    parser.add_argument('--folder_name', type=str, default='lyrics', help='Name of folder to look for songs')

    return parser.parse_args()

english_stopwords = set(nltk.corpus.stopwords.words('english'))
non_english_stopwords = set(nltk.corpus.stopwords.words()) - english_stopwords

stopwords = {lang: set(nltk.corpus.stopwords.words(lang)) for lang in nltk.corpus.stopwords.fileids()}

def get_language(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return max(((lang, len(words & stopwords)) for lang, stopwords in stopwords.items()), key = lambda x: x[1])[0]

def is_english(text):
    words = set(nltk.wordpunct_tokenize(text.lower()))
    return len(words & english_stopwords) > len(words & non_english_stopwords)

def analyze_file(args):
    '''
    Takes an project file.
    Goes through all lyrics in it.
    If the lyrics doesn't exist or if the lyrics is in another language than english,
    the entry is removed from the json file.
    '''
    data = json.load(open(args.file))
    print()
    print('Analyzing file: "{}"'.format(args.file))
    print('Number of songs: {}'.format(len(data)))
    print()

    failed = []
    new_data = {}
    valid_cntr = 0
    for idx, (artist, song, genre) in data.items():
        file_path = os.path.join(args.folder_name, '{}~{}'.format(artist.replace('/', ''), song.replace('/', '')))
        progressbar((int(idx)+1)/len(data))
        if os.path.exists(file_path):
            lyrics = open(file_path).read()

            unique_words = set(lyrics.replace('\n', ' ').split(' '))
            if 'instrumental' in lyrics.lower():
                if len(unique_words) < 5:
                    failed.append(['instrumental', artist + song, lyrics])
                    continue
            if len(lyrics) < 100:
                failed.append(['less < 100 chars', artist + song, lyrics])
                continue

            language = get_language(lyrics)

            language = get_language(lyrics)
            if language != 'english':
                failed.append(['no-english', artist + song, lyrics])
                continue

            new_data[valid_cntr] = [artist, song, genre]
            valid_cntr += 1
        else:
            failed.append(['file not found', artist + song, ''])

    failed.sort()

    if failed:
        print()
        print('Songs failed, removed: {}'.format(len(failed)))
    for reason, name, lyrics in failed:
        print('  "{}": "{}"'.format(reason, name))

    print()
    print('Number of songs before: {}'.format(len(data)))
    print('Number of songs after : {}'.format(len(new_data)))

    json.dump(new_data, open(args.output_file, 'w'), indent=4, sort_keys=True)
    print('Dumped in file: "{}"'.format(args.output_file))

if __name__ == '__main__':
    args = parse_args()
    analyze_file(args)