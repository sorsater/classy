'''
Get data from genius by using genius API as well as normal scraping, genius have no API method to get lyrics :(
'''

import requests
from bs4 import BeautifulSoup
from api_token import token
from pylev3 import Levenshtein

base_url = "http://api.genius.com"
search_url = base_url + "/search"
headers = {'Authorization': 'Bearer {}'.format(token)}

# Log file for the manual matches
matching_file_name = 'manual-matches.txt'

def get_lyrics_url(url):
    '''
    From the url, extract the lyrics
    Based on code from: https://bigishdata.com/2016/09/27/getting-song-lyrics-from-geniuss-api-scraping/
    '''
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    #at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("div", class_="lyrics").get_text() #updated css where the lyrics are based in HTML
    return lyrics

def levenshtein_distance(first, second):
    '''
    Find the Levenshtein distance between two strings.
    Taken from:
    https://www.stavros.io/posts/finding-the-levenshtein-distance-in-python/
    '''
    if len(first) > len(second):
        first, second = second, first
    if len(second) == 0:
        return len(first)
    first_length = len(first) + 1
    second_length = len(second) + 1
    distance_matrix = [[0] * second_length for x in range(first_length)]
    for i in range(first_length):
        distance_matrix[i][0] = i
        for j in range(second_length):
            distance_matrix[0][j]=j
    for i in range(1, first_length):
        for j in range(1, second_length):
            deletion = distance_matrix[i-1][j] + 1
            insertion = distance_matrix[i][j-1] + 1
            substitution = distance_matrix[i-1][j-1]
            if first[i-1] != second[j-1]:
                substitution += 1
            distance_matrix[i][j] = min(insertion, deletion, substitution)
    return distance_matrix[first_length-1][second_length-1]

def get_url_from_name(artist, song, verbose='', lev=0):
    '''
    From artist and song, use genius api to search for song.
    If verbose is set to 'fix_failed', method is called again and queries the user about alternatives.
    '''

    query = {'q': artist + ' ' + song}

    try:
        response = requests.get(search_url, params=query, headers=headers)
    except KeyboardInterrupt:
        pass
    except:
        print('Failed with response')
        print(search_url)
        input('Enter to continue')

    alternatives = []
    # Returns a number of hits, try to find correct one
    for hit in response.json()['response']['hits']:
        result = hit['result']

        url = result['url']
        q_artist = result['primary_artist']['name'].replace(u'\u200b', '')
        q_song = result['title'].replace(u'\u200b', '')
        q_api_path = result["api_path"]

        if q_artist.lower() == artist.lower():
            if q_song.lower() == song.lower():
                return url, q_artist, q_song

        # Levenschtein calculations. If distance <= 'lev' it is accepted
        lev_artist = levenshtein_distance(q_artist.lower(), artist.lower())
        lev_song = levenshtein_distance(q_song.lower(), song.lower())

        if (lev_artist + lev_song) <= lev:
            print(artist, '|', song)
            print(q_artist, '|', q_song)
            print('Total levenstein distance: {} / {}. Considered valid'.format(lev_artist + lev_song, lev))
            print()
            return url, q_artist, q_song

        alternatives.append([url, q_artist, q_song])

    # Gives examples to the user, answer with number of correct or blank if no match
    if verbose == 'ask_user':
        print()
        print()
        for i, (url, q_artist, q_song) in enumerate(alternatives):
            print('"{}": "{}" \n\t"{}"'.format(i, q_artist, q_song))

        res = input('Enter number for correct, "n" for failed: ')
        print()
        if res.isdigit():
            try:
                with open(matching_file_name, 'a+') as f:
                    f.write('Json:["{}" "{}"] ::matched:: genius: "{}"\n'.format(artist, song, str(alternatives[int(res)][1:])))
                print('Valid entry: {}'.format(str(alternatives[int(res)][1:])))
                print()
                print()
                return(alternatives[int(res)])
            except:
                print('Not valid number: {}'.format(int(res)))
                print()
                print()
                return 'manual', '', ''

        print('Failed song')
        print()
        print()
        return 'manual', '', ''

    # No match, if verbose is "fix_failed", call method again and query user with alternatives
    elif verbose == 'fix_failed':
        return get_url_from_name(artist, song, 'ask_user', lev)
    else:
        return 'fail', '', ''
