'''
Scrapes billboard links and stores the data in json file
Clean the files by removing duplicates
'''

import os
import sys
import json
from bs4 import BeautifulSoup
import requests
from w8m8 import progressbar

def scrape_billboard(billboard_file='billboard-links.json', db_file_name='url-db.json', genre_file_name='billboard.json'):
    '''
    From the "billboard_file" (which contains urls)
    Scrape all songs (artist, song) and store in "db_file_name"
    Scrape all songs (artist, song, genre) and store in "genre_file_name"
    Will not overwrite old entries in "db_file_name"
    '''
    print('Scraping billboard webpage')
    with open(billboard_file) as f:
        billboard_links = json.load(f)

    try:
        with open(db_file_name) as f:
            url_data_db = json.load(f)
    except:
        input('File broken "{}", continue with new file?'.format(db_file_name))
        url_data_db = {}

    print()
    num_urls = sum([len(urls) for genre, urls in billboard_links.items()])
    genre_data = {}
    cntr, url_cntr = 0, 0
    for genre, urls in billboard_links.items():
        for url in urls:
            url_cntr += 1
            page = requests.get(url)
            soup = BeautifulSoup(page.text, "html.parser")
            print('\033[F\033[K"{}": {}'.format(genre, url))
            for row in soup.find_all('div', {'class': 'ye-chart-item__text'}):
                song = row.find('div', {'class': 'ye-chart-item__title'}).text.strip()
                artist = row.find('div', {'class': 'ye-chart-item__artist'}).text.strip()

                artist = artist.replace(u'\u200b', '')
                song = song.replace(u'\u200b', '')
                key = str((artist, song))
                if not key in url_data_db:
                    url_data_db[key] = ''

                genre_data[str(cntr)] = [artist, song, genre]
                cntr += 1
                progressbar(url_cntr/num_urls, 'Number of songs: {}'.format(cntr))

    print()
    print()
    with open(db_file_name, 'w') as f:
        json.dump(url_data_db, f, indent=4)
    print('Db file saved to: "{}"'.format(db_file_name))

    with open(genre_file_name, 'w') as f:
        json.dump(genre_data, f, indent=4)
    print('Genre file saved to: "{}"'.format(genre_file_name))
    print()

def clean_json_file(file_name):
    '''
    Removes duplicates in "file_name"
    If duplicates within same genre, keep just one of them
    If same song in more than one genre, delete all occurences of it
    '''
    print('Cleaning file "{}"'.format(file_name))
    with open(file_name) as f:
        data = json.load(f)

    print('Number of songs: {}'.format(len(data)))
    print()
    print('Removing duplicates within same genre')
    seen = set()
    new_data = {}
    cntr = 0
    for idx, entry in data.items():
        entry = tuple(entry)
        if not entry in seen:
            new_data[str(cntr)] = entry
            cntr += 1
        seen.add(entry)

    data = new_data
    print('Number of songs: {}'.format(len(data)))
    print()

    print('Removing duplicates with different genres')
    seen = {}
    duplicates = set()
    for idx, entry in data.items():
        title = entry[:2]
        # Exist other song with different genre
        if title in seen:
            duplicates.add(idx)
            duplicates.add(seen[title])
        seen[title] = idx

    new_data = {}
    cntr = 0
    for idx, entry in data.items():
        if idx in duplicates:
            continue
        new_data[cntr] = entry
        cntr += 1

    data = new_data

    print('Number of songs: {}'.format(len(data)))
    print()

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)
    print('Saved to: "{}"'.format(file_name))


if __name__ == '__main__':
    scrape_billboard()
    clean_json_file('billboard.json')