'''
Takes several project files and merges them to one big
'''

import json
import os
import argparse
from w8m8 import progressbar
from scraper import clean_duplicates

def parse_args():
    '''
    Parse arguments.
    Only required argument is .json file with artist, song, genres and an output file
    '''
    parser = argparse.ArgumentParser()

    parser.add_argument('files', nargs='*', type=str, help='Name of json file')
    parser.add_argument('output_file', type=str, help='Name of output file')
    parser.add_argument('--db_file', type=str, default='url-db.json', help='List of all songs with their url')

    return parser.parse_args()

def merge_files(args):
    '''
    Takes several project files and merges them to one big
    '''
    for file_name in args.files:
        print(file_name)
    print()
    print(args.output_file)

    url_data_db = json.load(open(args.db_file))
    init_len_url_data_db = len(url_data_db)
    print()
    print('Analyzing files: "{}"'.format(args.files))
    print()

    new_data = {}
    cntr = 0
    for project in args.files:
        data = json.load(open(project))
        print('Number of songs for "{}": {}'.format(project, len(data)))
        for idx, (artist, song, genre) in data.items():
            key = str((artist, song))
            if not key in url_data_db:
                url_data_db[key] = ''
            new_data[cntr] = [artist, song, genre]
            cntr += 1
    print()
    print('Number of songs: {}'.format(len(new_data)))
    json.dump(new_data, open(args.output_file, 'w'), indent=4, sort_keys=True)
    print('Dumped in file: "{}"'.format(args.output_file))
    print()

    print('Number of db_entrys before: {}'.format(init_len_url_data_db))
    print('Number of db_entrys: {}'.format(len(url_data_db)))

    json.dump(url_data_db, open(args.db_file, 'w'), indent=4)#, sort_keys=True)

    clean_duplicates(args.output_file)

if __name__ == '__main__':
    args = parse_args()
    merge_files(args)