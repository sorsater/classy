from genius import *

import sys

from w8m8 import progressbar
import argparse
import json
import os

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('genre', type=str, help='Genre')
    #parser.add_argument('corpus', type=str, default='data', help='Name of corpus')

    return parser.parse_args()

args = parse_args()
genre = args.genre
file_name = genre + '.json'

if not os.path.exists(os.path.join('data', genre)):
    print('Creating genre folder in data/')
    os.makedirs(os.path.join('data', genre))

with open(file_name) as f:
    data = json.load(f)

num_songs = sum([len(songs) for artist, songs in data.items()])
cntr = 0

print('Genre: {} with {} songs'.format(genre, num_songs))
no_match = []
for artist, songs in data.items():
    for song in songs:
        cntr += 1

        url, q_artist, q_song = get_url_from_name(artist, song)

        if url == '':
            print('Failed: {} - {}'.format(artist, song))
            no_match.append([artist, song])
        else:
            lyrics = get_lyrics_url(url)
            # Fix name error
            artist = artist.replace('/', ' ')
            song = song.replace('/', ' ')
            with open('data/{}/{}~{}'.format(genre, artist, song), 'w') as f:
                f.write(lyrics)
    
        progressbar(cntr/num_songs, q_artist, q_song)

print()

if no_match:
    print('{} failed'.format(len(no_match)))
    for match in no_match:
        print(match)
else:
    print('Everything went well')