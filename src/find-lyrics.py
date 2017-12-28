'''
Takes an input file with genre, artist and songs.
From that file find all songs and store the lyrics
'''

from genius import *
from scraper import *

import sys
from w8m8 import progressbar
import argparse
import json
import os
from bs4 import BeautifulSoup

json_db_file = 'billboard-links2.json'

def parse_args():
    '''
    Parse arguments.
    Only required argument is .json file with artist, song, genres
    '''

    parser = argparse.ArgumentParser()

    parser.add_argument('file', type=str, help='Name of json to parse')
    parser.add_argument('--folder_name', type=str, default='lyrics', help='Name of folder')
    parser.add_argument('--fix_failed', action='store_true', help='Try to fix failed directly')
    parser.add_argument('--ignore_feat', action='store_true', help='Remove featuring from artist name when searching (fix for billboard data)')

    parser.add_argument('--bb_file', type=str, default='billboard-links.json', help='File with billboard links to scrape')
    parser.add_argument('--db_file', type=str, default='url-db.json', help='List of all songs with their url')
    parser.add_argument('--scrape_bb', action='store_true', help='Scrape from billboard files')
    parser.add_argument('--get_urls', action='store_true', help='Get url from the inputfile and store in it')
    parser.add_argument('--get_lyrics', action='store_true', help='Get lyrics from all urls')

    return parser.parse_args()

def get_lyrics_from_url():
    '''
    From the file "db_file", download and store all lyrics in the folder "folder_name"
    '''
    with open(args.db_file) as f:
        data = json.load(f)
    num_songs = len(data)
    print('File: {} with: {} songs'.format(args.db_file, num_songs))
    print()
    print()
    cntr = 0
    failed = []
    for key, url in data.items():
        artist, song = eval(key)
        cntr += 1
        progressbar(cntr/num_songs, '"{}"'.format(artist), '"{}"'.format(song))
        print('\033[F {} found, {} failed, '.format(cntr - len(failed), len(failed)))

        song_path = os.path.join(args.folder_name, artist.replace('/','') + '~' + song.replace('/',''))
        # File already processed
        if os.path.exists(song_path):
            continue

        # No valid url
        if url in ['', 'fail', 'manual', 'none']:
            failed.append([url, key])
            continue

        lyrics = get_lyrics_url(url)
        with open(song_path, 'w') as f:
            f.write(lyrics)

    print()
    for code, name in failed:
        print('Failed: {}: {}'.format(code, name))
    print('Number of failed: {}'.format(len(failed)))

def find_url_for_songs():
    '''
    Use the genius API to find urls for the songs in "db_file"
    '''
    fix_failed = 'fix' if args.fix_failed else ''
    
    with open(args.db_file) as f:
        data = json.load(f)
    num_songs = len(data)
    print('File: {} with: {} songs'.format(args.db_file, num_songs))
    print()
    print()
    cntr = 0
    failed = []

    try:
        for key, url in data.items():
            artist, song = eval(key)
            cntr += 1
            print('\033[F {} found, {} failed, '.format(cntr - len(failed), len(failed)))
            progressbar(cntr/num_songs, '"{}"'.format(artist), '"{}"'.format(song))
            if (url in ['manual', 'none']) or (url == 'fail' and not args.fix_failed):
                failed.append([artist, song])
                continue

            if 'genius.com' in url:
                continue
            
            if args.ignore_feat:
                if 'Featuring' in artist:
                    featuring = artist.index(' Featuring')
                    artist_no_feature = artist[:featuring]
                else:
                    artist_no_feature = artist
                url, q_artist, q_song = get_url_from_name(artist_no_feature, song, fix_failed)
            else:
                url, q_artist, q_song = get_url_from_name(artist, song, fix_failed)
            if url in ['fail', 'manual']:
                failed.append([artist, song])
                
            data[key] = url
    except KeyboardInterrupt:
        pass
    except:
        pass
        
    # Dump data
    with open(args.db_file, 'w') as f:
        json.dump(data, f, indent=4)

    print()
    for fail in failed:
        print('Url not found:', fail)

if __name__ == '__main__':
    args = parse_args()

    if not os.path.exists(args.folder_name):
        os.makedirs(args.folder_name)

    try:
        if args.scrape_bb:
            scrape_billboard(args.bb_file, args.db_file, args.genre_file)
            clean_json_file(args.genre_file)

        if args.get_urls:
            print('Finding urls for songs')
            find_url_for_songs()
        
        if args.get_lyrics:
            print('Getting lyrics from urls')
            print('Storing songs to folder: {}'.format(args.folder_name))
            get_lyrics_from_url()

            print('Number of lyrics in folder "{}": {}'.format(args.folder_name, len(os.listdir(args.folder_name))))
    except KeyboardInterrupt:
        print()
        print('Canceled')

    print('Done')
