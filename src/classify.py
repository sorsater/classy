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
from collections import Counter, OrderedDict
from time import time

# Available features.
# The first element should be all, the second is the default
all_features = OrderedDict([
    ('all', 'Add all features to the baseline'),
    ('baseline', 'The baseline system'),
    ('bigram', 'Bigrams in the songs'),
    ('meta', 'Song structure, use data about "Verse", "Chorus" etc'),
    ('stopwords', 'Remove stopwords'),
    ('stem', 'Stem all words'),
])

def parse_args(arguments=[]):
    '''
    Parse arguments.
    Only required argument is .json file with artist, song, genres
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, help='Name of json file')
    parser.add_argument('-g', '--genres', nargs='*', default=['all'], help='Genres to be parsed',
        choices=['all', 'baseline', 'pop', 'rap', 'rock', 'country', 'electronic', 'rob'])
    parser.add_argument('-i', '--iterations', type=int, default=1, help='Number of iterations to run model')
    parser.add_argument('-u', '--uni_thresh', type=int, default=10, help='Number of occurences for a unigram to be in model')
    parser.add_argument('-b', '--bi_thresh', type=int, default=10, help='Number of occurences for a bigram to be in model')
    parser.add_argument('-s', '--split', type=int, default=70, help='In percent, how much is training data')
    parser.add_argument('-f', '--features', type=str, nargs='*', default=[], help='Features to be used, default none.',
        choices=list(all_features.keys()))

    parser.add_argument('--output', action='store_false', help='Do not use multiline print')
    parser.add_argument('--folder_name', type=str, default='lyrics', help='Name of folder to look for songs')
    parser.add_argument('--failed', action='store_true', help='Show the failed songs')
    parser.add_argument('--show', type=int, default=-1, help='If provided, number of informative features to show')

    return parser.parse_args(arguments) if arguments else parser.parse_args()

def get_lyrics_from_file(args):
    '''
    From specified "args.file", return lyrics from "args.folder_name"
    '''

    corpus = []
    genre_distribution = []
    failed = []
    for idx, entry in json.load(open(args.file)).items():
        artist, song, genre = entry
        song_path = os.path.join(args.folder_name, artist.replace('/','') + '~' + song.replace('/',''))

        if ('all' not in args.genres) and (genre not in args.genres):
            continue

        if not os.path.exists(song_path):
            failed.append([artist, song])
            continue

        genre_distribution.append(genre)

        corpus.append({
            'name': artist + '~' + song,
            'lyrics': open(song_path).read(),
            'genre': genre,
        })

    return genre_distribution, corpus, failed

def run_model(i, corpus, args):
    '''
    Run one iteration of the model.
    If the argument 'output' is provided, prints more pretty.
    The inte
    '''
    # Might need to be modified so print behaves as expected
    printed_lines = 7

    t_run = time()

    print('===== RUNNING MODEL, iteration {}/{} ====='.format(i+1, args.iterations))
    random.shuffle(corpus)

    classy = Classy(corpus, args)

    classy.split_train_test()

    classy.train()
    classy.test()

    # Distribution in the train/test set
    # print(Counter([genre for features, genre in classy.train_set]))
    # print(Counter([genre for features, genre in classy.test_set]))

    # Show features or not
    if args.show >= 1:
        classy.show_features(args.show)

    # Clear previous print
    if args.output:
        print('\033[F\033[K' * printed_lines, end='')
        print('{}: Accuracy: {:.2f}%, Time: {:.1f} seconds'.format(i+1, 100*classy.accuracy, time() - t_run))

    return classy.accuracy

def main(args):
    try:
        # Reset the seed after each test
        random.seed(12345)

        t_start = time()
        print()
        print('===== READING DATA =====')
        print('Using file: "{}"'.format(args.file))
        # Read lyrics for all songs in file
        genre_distribution, corpus, failed = get_lyrics_from_file(args)
        # Creates a dict of the genres and their song count
        args.genres = Counter(genre_distribution)

        if failed:
            print('Failed: {}'.format(len(failed)))
            # Toggle to see songs that failed
            if False:
                for artist, song in failed:
                    print(' "{}": "{}"'.format(artist, song))
        print()
        print('Number of songs in total: {}'.format(len(corpus)))
        for genre, cntr in args.genres.items():
            print('  {}: "{}" '.format(cntr, genre))
        num_train = int(args.split/100*len(corpus))

        print()
        print('===== MODEL PARAMETERS =====')
        print('Train and test: {:.0f}:{:.0f} ({}:{})'.format(args.split,100-args.split, num_train, len(corpus)-num_train))

        if 'all' in args.features:
            args.features = list(all_features.keys())[1:]
        else:
            # Add baseline
            args.features = [list(all_features.keys())[1]] + args.features

        print()
        print('Features:')
        for feature, description in all_features.items():
            if feature in args.features:
                print('  {}: \t {}'.format(feature, all_features[feature]))

        print()
        print('Classifier with unigram value: {}'.format(args.uni_thresh))
        if 'bigram' in args.features:
            print('Classifier with bigram value: {}'.format(args.bi_thresh))
        print('Number of iterations: {}'.format(args.iterations))

        # Run model "args.iterations" times
        print()
        accs = [run_model(i, corpus, args) for i in range(args.iterations)]

        total_accuracy = sum(accs) / len(accs)
        total_time = time() - t_start

        print()
        print('===== RESULT =====')
        print('Average accuracy: {:.2f}%'.format(100*total_accuracy))

        print()
        print('Total time: {:.1f} seconds'.format(total_time))

        return total_accuracy, total_time

    except KeyboardInterrupt:
        print()
        print()
        print('CANCELED')
    except Exception as e:
        print('Error: {}'.format(e))

if __name__ == '__main__':
    main(parse_args())