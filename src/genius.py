import requests
from bs4 import BeautifulSoup
from api_token import token
base_url = "http://api.genius.com"
headers = {'Authorization': 'Bearer {}'.format(token)}

def get_lyrics_url(url):
    page = requests.get(url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    #at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("div", class_="lyrics").get_text() #updated css where the lyrics are based in HTML
    return lyrics

def get_url_from_name(artist, song):
    search_string = artist + ' ' + song

    search_url = base_url + "/search"
    data = {'q': search_string}

    response = requests.get(search_url, params=data, headers=headers)
    
    # Returns a number of hits, try to find correct one
    for hit in response.json()['response']['hits']:
        result = hit['result']
        
        url = result['url']
        q_artist = result['primary_artist']['name']
        q_song = result['title']
        q_api_path = result["api_path"]

        if q_artist.lower() == artist.lower():
            if q_song.lower() == song.lower():
                return url, q_artist, q_song
        
    # No match
    return '', '', ''

def get_lyrics_api_path(api_path):
    song_url = base_url + api_path
    response = requests.get(song_url, headers=headers)
    json = response.json()
    path = json["response"]["song"]["path"]
    #gotta go regular html scraping... come on Genius
    page_url = "http://genius.com" + path
    page = requests.get(page_url)
    html = BeautifulSoup(page.text, "html.parser")
    #remove script tags that they put in the middle of the lyrics
    [h.extract() for h in html('script')]
    #at least Genius is nice and has a tag called 'lyrics'!
    lyrics = html.find("div", class_="lyrics").get_text() #updated css where the lyrics are based in HTML
    return lyrics
