'''
Takes an input file with genre, artist and songs.
From that file find all songs and store the lyrics
'''

from genius import *

import sys

from w8m8 import progressbar
import argparse
import json
import os
from collections import Counter

def parse_args():
    parser = argparse.ArgumentParser()

    parser.add_argument('--file', type=str, help='Name of json to parse')
    parser.add_argument('--folder_name', type=str, default='billboard_lyrics', help='Name of folder')
    parser.add_argument('--fix_failed', action='store_true', help='Try to fix failed directly')
    parser.add_argument('--ignore_feat', action='store_true', help='Remove featuring from artist name when searching (fix for billboard data)')

    return parser.parse_args()

args = parse_args()

if not os.path.exists(args.folder_name):
    os.makedirs(args.folder_name)

print('Storing songs to folder: {}'.format(args.folder_name))

def main():
    fix_failed = 'fix' if args.fix_failed else ''
    
    with open(args.file) as f:
        data = json.load(f)
    num_songs = sum([len(songs) for genre, artists in data.items() for artist, songs in artists.items()] )
    print('File: {} with: {} songs'.format(args.file, num_songs))
    print()
    print()
    cntr = 0
    failed = []
    paths = []
    for genre, artists in data.items():
        for artist, songs in artists.items():
            for song in songs:
                cntr += 1
                new_path = os.path.join(args.folder_name, artist.replace('/','') + '~' + song.replace('/',''))
                paths.append(new_path)
                print('\033[F {} found, {} failed, '.format(cntr - len(failed), len(failed)))

                progressbar(cntr/num_songs, '"{}"'.format(genre), '"{}"'.format(artist), '"{}"'.format(song))
                if not os.path.exists(new_path):
                    
                    if args.ignore_feat:
                        if 'Featuring' in artist:
                            featuring = artist.index(' Featuring')
                            artist_no_feature = artist[:featuring]
                        else:
                            artist_no_feature = artist
                        url, q_artist, q_song = get_url_from_name(artist_no_feature, song, fix_failed)
                    else:
                        url, q_artist, q_song = get_url_from_name(artist, song, fix_failed)
                    if url == '':
                        failed.append([artist, song])
                        # Remove just added song
                        paths = paths[:-1]
                    else:
                        lyrics = get_lyrics_url(url)
                        with open(new_path, 'w') as f:
                            f.write(lyrics)
            
    print()
    print(cntr)
   
    print('Number of songs in folder: {}'.format(len(os.listdir(args.folder_name))))
    print('Number of songs added: {}'.format(len(paths)))
    print('Number of unique songs: {}'.format(len(set(paths))))

    # Songs that are duplicates in file
    duplicates = [[cnt, song] for song, cnt in Counter(paths).items() if cnt > 1]
    if duplicates:
        print('{} duplicates in "{}":'.format(len(duplicates), args.file))
        duplicates.sort(reverse=True)
        for cnt, song in duplicates:
            print('\t', cnt, ':', song)
    else:
        print('No duplicates in: "{}"'.format(args.file))

try:
    main()
except KeyboardInterrupt:
    pass
