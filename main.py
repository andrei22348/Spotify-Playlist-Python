from bs4 import BeautifulSoup
import requests
import spotipy
from spotipy.oauth2 import SpotifyOAuth
import os
from dotenv import load_dotenv

load_dotenv()
CLIENT_ID = os.getenv("CLIENT_ID")
CLIENT_SECRET = os.getenv("CLIENT_SECRET")
REDIRECT_URI = os.getenv("REDIRECT_URI")

sp = spotipy.Spotify(auth_manager=SpotifyOAuth(client_id=CLIENT_ID,
                                               client_secret=CLIENT_SECRET,
                                               redirect_uri=REDIRECT_URI,
                                               scope="playlist-modify-private"))

user_id = sp.current_user()["id"]
date = input("Which year do you want to travel to? Type the date in this format YYYY-MM-DD: ")

header = {"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:131.0) Gecko/20100101 Firefox/131.0"}
url = "https://www.billboard.com/charts/hot-100/" + date
response = requests.get(url=url, headers=header)

soup = BeautifulSoup(response.text, 'html.parser')

song_titles = []
original_artists = []
titles = soup.select('ul > li > #title-of-a-story')
artists = soup.select('ul > li > .c-label.a-no-trucate')

for title, artist in zip(titles, artists):
    song_titles.append(title.getText().strip())
    original_artists.append(artist.getText().strip())

print(f"Collected {len(song_titles)} songs and artists.")

year = date.split('-')[0]
song_uris = []

for title, artist in zip(song_titles, original_artists):
    track_uri = None

    query = f"track:{title}"
    result = sp.search(q=query, type='track', limit=50)

    for item in result['tracks']['items']:
        spotify_title = item['name'].lower()
        spotify_artists = [a['name'].lower() for a in item['artists']]


        if (title.lower() in spotify_title or spotify_title in title.lower()) and any(artist.lower() in spotify_artist or spotify_artist in artist.lower() for spotify_artist in spotify_artists):
            track_uri = item['uri']
            break

    if track_uri:
        song_uris.append(track_uri)
    else:
        print(f"Could not find an exact match for '{title}' by '{artist}' on Spotify.")

playlist_name = f"Billboard Top 100 - {date}"
playlist = sp.user_playlist_create(user=user_id, name=playlist_name, public=False)

if song_uris:
    sp.playlist_add_items(playlist_id=playlist['id'], items=song_uris)
    print(f"Playlist '{playlist_name}' created successfully with {len(song_uris)} songs.")
else:
    print("No songs were added to the playlist.")
