''''
Takes an .json file as input.
In that file, each artist and title are associated with an genre.
From that data train a classifier and evaluate the performance
'''

import random
import nltk
from nltk.corpus import names
import os
import argparse
from naive_bayes import Classy
import json
from collections import Counter

random.seed(12345)

def parse_args():
    '''
    Parse arguments.
    Only required argument is .json file with artist, song, genres
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, help='Name of json file')
    parser.add_argument('--folder_name', type=str, default='lyrics', help='Name of folder')
    parser.add_argument('--genres', nargs='*', default=['all'], help='Genres to be parsed')
    parser.add_argument('--failed', action='store_true', help='Show the failed songs')
    parser.add_argument('--thresh', type=int, default=10, help='Number of occurences for a word to be in model')
    parser.add_argument('--features', type=int, default=-1, help='If provided, number of informative features to show')
    parser.add_argument('--split', type=int, default=70, help='In percent, how much is training data')
    parser.add_argument('--iterations', type=int, default=1, help='Number of iterations to run model')

    return parser.parse_args()

def get_lyrics_from_file(args):
    '''
    From specified "args.file", return lyrics from "args.folder_name"
    '''

    lyrics = []
    with open(args.file) as f:
        data = json.load(f)

    failed = []
    genre_distribution = []
    for idx, entry in data.items():
        artist, song, genre = entry
        song_path = os.path.join(args.folder_name, artist.replace('/','') + '~' + song.replace('/',''))

        if not os.path.exists(song_path):
            failed.append([artist, song])
            continue

        if args.genres != ['all'] and genre not in args.genres:
            continue

        genre_distribution.append(genre)
        with open(song_path) as f:
            lyric = []
            for i, line in enumerate(f):
                lyric += line.split()
            lyrics.append({'name': song, 'n': i, 'lyric': lyric, 'genre': genre})

    return genre_distribution, lyrics, failed

if __name__ == '__main__':
    try:
        args = parse_args()
        print(args.genres)
        print('===== READ DATA =====')
        print('Parsing file: "{}"'.format(args.file))
        genre_distribution, songs, failed = get_lyrics_from_file(args)
        print()
        print("Number of songs in total:", len(songs))
        for genre, cntr in Counter(genre_distribution).items():
            print('\tGenre "{}" with {} songs'.format(genre, cntr))

        genres = set(genre_distribution)

        if failed:
            print("Failed: {}".format(len(failed)))
            if args.failed:
                for artist, song in failed:
                    print('\t', artist, song)

        accs = []
        for i in range(args.iterations):
            random.shuffle(songs)

            print()
            print('===== RUNNING MODEL =====')
            print('Iteration: {}/{}'.format(i+1, args.iterations))
            # Create the classy object
            classy = Classy(songs, genres, args.thresh)

            # For each song, extract features
            classy.extract_features()

            # Provide percent that is train, rest is test
            classy.split_train_test(percent=args.split)

            # Train the model
            classy.train()

            # Test the model
            #classy.test_all()
            classy.test_documents(classy.test_set)

            # Show features or not
            if args.features >= 1:
                classy.show_features(args.features)

            accs.append(classy.accuracy)

        print('\n\n===== RESULT =====')
        print('File: "{}"'.format(args.file))
        print("Number of songs in total:", len(songs))
        print('Train and test: {:.0f}:{:.0f} ({}:{})'.format(args.split, 100-args.split, len(classy.train_set), len(classy.test_set)))
        print()
        for genre, cntr in Counter(genre_distribution).items():
            print('  Genre "{}" with {} songs'.format(genre, cntr))
        print()
        for acc in accs:
            print('  Accuracy of {} songs: {:.2f}%'.format(len(classy.test_set), 100*acc))

        print()

        print('Average accuracy of {} songs: {:.2f}%'.format(len(classy.test_set), 100*sum(accs)/len(accs)))
    except KeyboardInterrupt:
        print()
        print()
        print('CANCELED')
    except Exception as e:
        print('Error: {}'.format(e))
