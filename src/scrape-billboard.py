'''
Scrapes local billboard files and saves them to json file
'''

import os
import sys
import json
from bs4 import BeautifulSoup

output_name = 'billboard-ddddpop-rap.json'
genres = {}
cntr = 0
for genre in ['pop', 'rap']:
    genre_path = os.path.join('html-files', 'billboard', genre)
    files = os.listdir(genre_path)
    genres[genre] = {}
    for file_name in files:
        file_path = os.path.join(genre_path, file_name)
        soup = BeautifulSoup(open(file_path), 'html.parser')    
        for row in soup.find_all('div', {'class': 'ye-chart-item__text'}):
            song = row.find('div', {'class': 'ye-chart-item__title'}).text.strip()
            artist = row.find('div', {'class': 'ye-chart-item__artist'}).text.strip()

            artist = artist.replace(u'\u200b', '')
            song = song.replace(u'\u200b', '')
            genres[genre][artist] = genres[genre].get(artist, []) + [song]
            cntr += 1
            print('Number of songs: {}'.format(cntr), end='\r')


with open(output_name, 'w') as f:
    json.dump(genres, f, indent=4)
print('Saved to: {}'.format(output_name))
