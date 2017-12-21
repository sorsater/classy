
import random
import nltk
from nltk.corpus import names
import os
import argparse
from naive_bayes import Classy
import json

random.seed(12345)

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('file_name', type=str, help='Name of json file')
    parser.add_argument('--folder_name', type=str, default='data', help='Name of folder')

    return parser.parse_args()

def get_lyrics_from_file(args):
    '''
    From specified 'file', open data/ and return lyrics
    '''

    lyrics = []
    with open(args.file_name) as f:
        data = json.load(f)

    failed = []
    for genre, music in data.items():
        for artist, songs in music.items():
            for song in songs:
                song_path = os.path.join(args.folder_name, artist.replace('/','') + '~' + song.replace('/',''))
                if not os.path.exists(song_path):
                    failed.append([artist, song])
                    continue
                with open(song_path) as f:
                    lyric = []
                    for line in f:
                        lyric += line.split()
                    lyrics.append({'name': song, 'lyric': lyric, 'genre': genre})
    
    return data.keys(), lyrics, failed

if __name__ == '__main__':
    args = parse_args()

    print('===== Preprocess =====')
    print('Parsing file: "{}"'.format(args.file_name))
    #songs = get_lyrics_from_genres(args.genres, args.n_songs)
    genres, songs, failed = get_lyrics_from_file(args)
    print("Genres: {} {}".format(len(genres), ', '.join(genres)))
    print("Number of songs in total:", len(songs))
    if failed:
        print("Failed:")
        for artist, song in failed:
            print('\t', artist, song)
    random.shuffle(songs)

    print()
    print('===== NLTK =====')
    # Create the classy object
    classy = Classy(songs, genres)

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

