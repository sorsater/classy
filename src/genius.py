'''
Get data from genius by using genius API as well as normal scraping (genius have no api to get lyrics???)
'''
import requests
from bs4 import BeautifulSoup
from api_token import token
base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer {}'.format(token)}

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

def get_url_from_name(artist, song, verbose=''):
    '''
    From artist and song, use genius api to search for song.
    If verbose is set to 'fix', method is called again and queries the user about alternatives.
    '''
    
    search_string = artist + ' ' + song

    search_url = base_url + "/search"
    data = {'q': search_string}

    response = requests.get(search_url, params=data, headers=headers)

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
        
        alternatives.append([url, q_artist, q_song])

    # Gives examples to the user, answer with number to 
    if verbose == 'fix_now':
        print()
        print()
        for i, (url, q_artist, q_song) in enumerate(alternatives):
            print('"{}": "{}" \n\t"{}"'.format(i, q_artist, q_song))
        
        res = input('Enter number for correct, "n" for failed: ')
        print()
        if res.isdigit():
            print('Valid entry')
            print()
            with open(matching_file_name, 'a+') as f:
                f.write('Json:["{}" "{}"] ::matched:: genius: "{}" \n'.format(artist, song, str(alternatives[int(res)][1:])))
            return(alternatives[int(res)])
            
        print('Failed song')
        print()
        print()
        return 'manual', '', ''

    # No match
    elif verbose == 'fix':
        return get_url_from_name(artist, song, 'fix_now')
    else:
        return 'fail', '', ''
