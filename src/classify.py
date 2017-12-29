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
from bayes import Classy
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
    parser.add_argument('--output', action='store_false', help='Do not use multiline print')

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

def run_model(args, i, songs, genres):
    '''
    Run one iteration of the model.
    If the argument 'output' is provided, prints more pretty.
    The inte
    '''
    # Might need to be modified so print appers as expected
    printed_lines = 7

    print('===== RUNNING MODEL, iteration {}/{} ====='.format(i+1, args.iterations))
    random.shuffle(songs)

    classy = Classy(songs, genres, args)

    classy.split_train_test()

    classy.train()
    classy.test()

    # Distribution in the train/test set
    # print(Counter([genre for features, genre in classy.train_set]))
    # print(Counter([genre for features, genre in classy.test_set]))

    # Show features or not
    if args.features >= 1:
        classy.show_features(args.features)

    # Clear previous print
    if args.output:
        print('\033[F\033[K' * printed_lines, end='')
        print('Iteration: {} Accuracy: {:.2f}%'.format(i+1, 100*classy.accuracy))

    return classy

if __name__ == '__main__':
    try:
        args = parse_args()
        print('===== READ DATA =====')
        print('Using file: "{}"'.format(args.file))
        # Read lyrics for all songs in file
        genre_distribution, songs, failed = get_lyrics_from_file(args)

        if failed:
            print("Failed: {}".format(len(failed)))
            if args.failed:
                for artist, song in failed:
                    print('\t', artist, song)

        print()
        print("Number of songs in total:", len(songs))
        num_train = int(args.split/100*len(songs))
        print('Train and test: {:.0f}:{:.0f} ({}:{})'.format(args.split, 100-args.split, num_train, len(songs)-num_train))
        print('Genres:')
        for genre, cntr in Counter(genre_distribution).items():
            print('  "{}" with {} songs'.format(genre, cntr))

        print('Classifier with freq value: {}'.format(args.thresh))

        genres = set(genre_distribution)

        print()
        accs = []
        for i in range(args.iterations):
            classy = run_model(args, i, songs, genres)
            accs.append(classy.accuracy)
            prev_acc = classy.accuracy

        print()
        print('===== RESULT =====')
        print('Average accuracy: {:.2f}%'.format(100*sum(accs)/len(accs)))

    except KeyboardInterrupt:
        print()
        print()
        print('CANCELED')
    except Exception as e:
        print('Error: {}'.format(e))
