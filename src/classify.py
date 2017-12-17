
import random
import nltk
from nltk.corpus import names
import os
import argparse
from naive_bayes import Classy

def parse_args():
    parser = argparse.ArgumentParser()
    parser.add_argument('-n', '--n_songs', default='all', help='Number of songs in each genre')
    parser.add_argument('-g', '--genres', default='all', nargs='*', help='Genres to parse')

    return parser.parse_args()

def get_lyrics_from_genres(genres, _n='all'):
    '''
    From specified 'genre', open data/'genre' and return n lyrics
    If 'all' or not provided, return all in folde
    '''
    
    lyrics = []
    for genre in genres:
        genre_path = os.path.join('data', genre)
        songs = os.listdir(genre_path)

        n = len(songs) if _n == 'all' else int(_n)
        print('{}: {} ({})'.format(genre, n, len(songs)))

        for song in songs[:n]:
            with open(os.path.join(genre_path, song)) as f:
                lyric = []
                for line in f:
                    lyric += line.split()
                lyrics.append({'name': song, 'lyric': lyric, 'genre': genre})
    
    return lyrics

if __name__ == '__main__':


    args = parse_args()

    if args.genres == 'all':
        args.genres = os.listdir('data')
    elif isinstance(args.genres, str):
        args.genres = [genre]

    print('===== Preprocess =====')
    print('Parsing genres: {}'.format(', '.join(args.genres)))
    songs = get_lyrics_from_genres(args.genres, args.n_songs)
    print("Number of songs in total:", len(songs))
    random.shuffle(songs)

    print()
    print('===== NLTK =====')
    # Create the classy object
    classy = Classy(songs, args.genres)

    # For each song, extract features
    classy.extract_features()

    # Provide percent that is train, rest is test
    classy.split_train_test(0.7)
    
    # Train the model
    classy.train()

    # Test the model
    classy.test_all()

    #text = ['love', 'me', 'tender', 'kiss', 'me', 'bye', 'babe']
    #document = [classy.get_features(text), 'rock']s
    #classy.test_documents([document], True)

