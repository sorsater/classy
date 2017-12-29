'''
Analyzes a genre file by calculating number of songs in each genre.
'''

import sys
import json
from collections import Counter

file_name = sys.argv[1] if len(sys.argv) >= 2 else 'billboard.json'

print()
print('Analyzing file: "{}"'.format(file_name))
print()

for genre, cnt in Counter([genre for idx, (artist, song, genre) in json.load(open(file_name)).items()]).items():
    print('Genre: "{}" with: {} songs'.format(genre, cnt))