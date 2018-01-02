'''
Takes several project files and merges them to one big.
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

    return parser.parse_args()

def merge_files(args):
    '''
    Takes several project files and merges them to one big.
    '''
    for potatis in args.files:
        print(potatis)
    print()
    print(args.output_file)

    input()
    #data = json.load(open(args.file))
    print()
    print('Analyzing files: "{}"'.format(args.files))
    print()

    new_data = {}
    valid_cntr = 0
    for project in args.files:
        print('File name: "{}"'.format(project))
        data = json.load(open(project))
        print('Number of songs: {}'.format(len(data)))
        for idx, (artist, song, genre) in data.items():
            new_data[valid_cntr] = [artist, song, genre]
            valid_cntr += 1

    print('Number of songs: {}'.format(len(new_data)))
    input()
    json.dump(new_data, open(args.output_file, 'w'), indent=4, sort_keys=True)
    print('Dumped in file: "{}"'.format(args.output_file))

    clean_duplicates(args.output_file)

if __name__ == '__main__':
    args = parse_args()
    merge_files(args)