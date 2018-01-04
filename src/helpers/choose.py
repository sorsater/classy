
from itertools import combinations

import sys

try:
    number = int(sys.argv[1])
except IndexError:
    print('Provide a number: "python3 choose.py n", using default')
    number = 2

print('Using number: {}'.format(number))
print()
genres = ['pop', 'rap', 'electronic', 'rob', 'rock', 'country']

for i, comb in enumerate(combinations(genres, number)):
    print(list(comb))

print()
print('Number of combos: {}'.format(i+1))