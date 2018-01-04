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
from collections import Counter

def scrape_billboard(billboard_file='billboard-links.json', db_file_name='url-db.json', genre_file_name='billboard.json'):
    '''
    From the 'billboard_file' (which contains urls)
    Scrape all songs (artist, song) and store in 'db_file_name'
    Scrape all songs (artist, song, genre) and store in 'genre_file_name'
    Will not overwrite old entries in 'db_file_name'
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
    failed_links = []
    working_archive = set()
    chart_items = {
        False: [['ye-chart-item__text', 'div'], ['ye-chart-item__title', 'div'], ['ye-chart-item__artist', 'div']],
        True: [['ye-chart__item-text', 'div'], ['ye-chart__item-title', 'h1'], ['ye-chart__item-subtitle', 'h2']],
    }
    genre_distribution = []
    for genre, urls in billboard_links.items():
        for url in urls:
            url_cntr += 1

            page = requests.get(url)
            soup = BeautifulSoup(page.text, 'html.parser')

            with open('billboard-pages/' + url.replace('/', '|') + '.html', 'w') as f:
                f.write(page.text)
            print('\033[F\033[K"{}": {}'.format(genre, url))

            class_base = chart_items[True]
            items = soup.find_all('', {'class': class_base[0][0]})
            if not items:
                class_base = chart_items[False]
                items = soup.find_all('', {'class': class_base[0][0]})
            if not items:
                failed_links.append([genre, url])
            for row in items:
                if 'archive' in url:
                    working_archive.add(url)
                song = row.find('', {'class': class_base[1][0]}).text.strip()
                artist = row.find('', {'class': class_base[2][0]}).text.strip()

                artist = artist.replace(u'\u200b', '')
                song = song.replace(u'\u200b', '')
                key = str((artist, song))
                if not key in url_data_db:
                    url_data_db[key] = ''

                genre_data[str(cntr)] = [artist, song, genre]
                genre_distribution.append(genre)
                cntr += 1
            progressbar(url_cntr/num_urls, 'Number of songs: {} Failed: {}'.format(cntr, len(failed_links)))
    print()
    print()
    for genre, link in failed_links:
        print('Failed: Genre: "{}", url: {}'.format(genre, link))
    print()
    for archive in working_archive:
        print('Archive: {}'.format(archive))
    print('Manually added "adult pop songs 2012"')

    print()
    print()
    with open(db_file_name, 'w') as f:
        json.dump(url_data_db, f, indent=4)
    print('Db file saved to: "{}"'.format(db_file_name))

    with open(genre_file_name, 'w') as f:
        json.dump(genre_data, f, indent=4)
    print('Genre file saved to: "{}"'.format(genre_file_name))
    print()
    print()
    for genre, cnt in Counter(genre_distribution).items():
        print('  Genre: {} {}'.format(genre, cnt))
    print()

def clean_duplicates(file_name):
    '''
    Removes duplicates in 'file_name'
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
        entry_low = tuple([e.lower() for e in entry])
        if not entry_low in seen:
            new_data[str(cntr)] = tuple(entry)
            cntr += 1
        seen.add(entry_low)

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

    for genre, cnt in Counter([genre for idx, (artist, song, genre) in data.items()]).items():
        print('  Genre: {} {}'.format(genre, cnt))
    print()

    print('Number of songs: {}'.format(len(data)))
    print()

    with open(file_name, 'w') as f:
        json.dump(data, f, indent=4)
    print('Saved to: "{}"'.format(file_name))

if __name__ == '__main__':
    scrape_billboard()
    clean_duplicates(genre_file_name)
