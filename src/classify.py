''''
Takes an .json file as input.
In that file, each artist and title are associated with an genre.
From that data train a classifier and evaluate the performance
'''

import random
import nltk
import os
import argparse
from bayes import Classy
import json
from collections import Counter, OrderedDict
from time import time
import sys

# Available features.
# The first element should be all, the second is the default
all_features = OrderedDict([
    ('all', 'Add all features to the baseline'),
    ('baseline', 'The baseline system'),
    ('bigram', 'Bigrams in the songs'),
    ('trigram', 'Trigrams in the songs'),
    ('fourgram', 'Four-grams in the songs'),
    ('fivegram', 'Five-grams in the songs'),
    ('meta', 'Song structure, use data about "Verse", "Chorus" etc'),
    ('stopwords', 'Remove stopwords'),
    ('tokenize', 'Tokenize lyrics'),
    ('stem', 'Stem all words'),
])

suppress_output = False

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

    # N-grams
    parser.add_argument('-u', '--uni_thresh', type=int, default=2500, help='Number of unigram features to be in model')
    parser.add_argument('-b', '--bi_thresh', type=int, default=2000, help='Number of bigram features to be in model')
    parser.add_argument('-t', '--tri_thresh', type=int, default=3000, help='Number of trigram features to be in model')
    parser.add_argument('--four_thresh', type=int, default=1000, help='Number of four-gram features to be in model')
    parser.add_argument('--five_thresh', type=int, default=1000, help='Number of five-gram features to be in model')

    parser.add_argument('-s', '--split', type=int, default=70, help='In percent, how much is training data')
    parser.add_argument('-f', '--features', type=str, nargs='*', default=[], help='Features to be used, default none.',
        choices=list(all_features.keys()))

    parser.add_argument('--count', type=int, default=-1, help='Limit the number of songs in each genre to this number. To test system on smaller dataset.')

    parser.add_argument('--output', action='store_false', help='If provided, do not use multiline print')
    parser.add_argument('--stats', action='store_true', help='Show stats about precision, recall, f_measure')
    parser.add_argument('--folder_name', type=str, default='lyrics', help='Name of folder to look for songs')
    parser.add_argument('--show', type=int, default=-1, help='If provided, number of informative features to show')

    # Tune number of chars/words/unique words
    parser.add_argument('--num_chars', type=int, default=-1, help='Number of chars in lyrics')
    parser.add_argument('--num_words', type=int, default=-1, help='Number of words in lyrics')
    parser.add_argument('--num_unique', type=int, default=-1, help='Number of uique words in lyrics')

    args = parser.parse_args(arguments) if arguments else parser.parse_args()

    # Output is needed for the stats to work
    if args.stats:
        args.output = False

    return args

def get_lyrics_from_file(args):
    '''
    From specified 'args.file', return lyrics from 'args.folder_name'
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

        if args.count != -1:
            if genre_distribution.count(genre) >= args.count:
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
    t_run = time()

    print('===== RUNNING MODEL, iteration {}/{} ====='.format(i+1, args.iterations))
    random.shuffle(corpus)

    classy = Classy(corpus, args)

    classy.split_train_test()

    classy.train()
    classy.test()

    num_prints = classy.num_prints

    # Distribution of genres in the train/test set
    # print(Counter([genre for features, genre in classy.train_set]))
    # print(Counter([genre for features, genre in classy.test_set]))

    # Clear previous print
    if args.output:
        print('\033[F\033[K' * (num_prints + 1), end='')
        print(' {}: Accuracy: {:.2f}%, Time: {:.1f} seconds'.format(str(i+1).rjust(2), 100*classy.accuracy, time() - t_run))

    # Show features or not
    if args.show >= 1:
        classy.show_features(args.show)

    return classy.accuracy, classy.stats

def _print(msg=''):
    '''
    Used when evaluating the system.
    Suppress some prints to limit the output.
    '''
    print(msg) if not suppress_output else None

def main(args, output=False):
    global suppress_output
    suppress_output = output

    try:
        # Reset the seed after each test
        random.seed(12345)

        t_start = time()
        _print()
        _print('##### READING DATA #####')
        _print('Using file: "{}"'.format(args.file))
        # Read lyrics for all songs in file
        genre_distribution, corpus, failed = get_lyrics_from_file(args)
        # Creates a dict of the genres and their song count
        args.genres = Counter(genre_distribution)

        if failed:
            _print('Failed: {}'.format(len(failed)))
            # Toggle to see songs that failed
            if True:
                for artist, song in failed:
                    _print(' "{}": "{}"'.format(artist, song))
        _print()
        _print('Number of songs in total: {}'.format(len(corpus)))
        for genre, cntr in args.genres.items():
            _print('  {}: "{}" '.format(cntr, genre))
        num_train = int(args.split/100*len(corpus))

        _print()
        _print('##### MODEL PARAMETERS #####')
        _print('Train and test: {:.0f}:{:.0f} ({}:{})'.format(args.split,100-args.split, num_train, len(corpus)-num_train))

        if 'all' in args.features:
            args.features = list(all_features.keys())[1:]
        else:
            # Add baseline
            args.features = [list(all_features.keys())[1]] + args.features

        _print()
        _print('Features:')
        for feature, description in all_features.items():
            if feature in args.features:
                _print('  {}: \t {}'.format(feature, all_features[feature]))

        _print()
        _print('Classifier with unigram value: {}'.format(args.uni_thresh))
        if 'bigram' in args.features:
            _print('Classifier with bigram value: {}'.format(args.bi_thresh))
        if 'trigram' in args.features:
            _print('Classifier with trigram value: {}'.format(args.tri_thresh))
        if 'fourgram' in args.features:
            _print('Classifier with four-gram value: {}'.format(args.four_thresh))
        if 'fivegram' in args.features:
            _print('Classifier with five-gram value: {}'.format(args.five_thresh))
        _print('Number of iterations: {}'.format(args.iterations))

        # Run model 'args.iterations' times
        print()
        accs = []
        stats = []
        for i in range(args.iterations):
            acc, stat = run_model(i, corpus, args)
            accs.append(acc)
            stats.append(stat)

        total_accuracy = sum(accs) / len(accs)
        total_time = time() - t_start

        print()
        print('##### RESULT #####')
        print('Average accuracy: {:.2f}%'.format(100*total_accuracy))

        _print()
        print('Test time: {:.1f} seconds'.format(total_time))

        return total_accuracy, stats, total_time

    except KeyboardInterrupt:
        print()
        print()
        print('CANCELED')
        # Raise to caller (if exists)
        if __name__ != '__main__':
            raise KeyboardInterrupt
    '''
    except Exception as e:
        exc_type, exc_obj, exc_tb = sys.exc_info()
        exc_name = sys.exc_info()[0].__name__
        file_name = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
        print()
        print()
        print(exc_name, file_name, exc_tb.tb_lineno)
        print('Error: {}'.format(e))
    '''
if __name__ == '__main__':
    main(parse_args())