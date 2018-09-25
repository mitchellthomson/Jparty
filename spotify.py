from flask import Flask
from flask import jsonify
from yeelight import Bulb, discover_bulbs
from yeelight import flow
from yeelight import *
import requests
from timeit import Timer
import time

#from .utils import _clamp

#import base64
#import urllib
import spotipy
from spotipy import oauth2
#import spotipy.util as util
#import json

app = Flask(__name__)

PORT = 8080
SPOTIPY_CLIENT_ID = "40673f62ed1d44b387160bf9e82a2de1"
SPOTIPY_CLIENT_SECRET = '7a3ee97f8220400e9edf8a3b01fcc84f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read user-read-playback-state user-modify-playback-state'
CACHE = '.spotipyoauthcache'
SPOTIPY_PLAYLIST_API = "https://api.spotify.com/v1/playlists/{1IAY7B3G3MKO9Pre7cxA9A}/tracks"

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE,
                               cache_path=CACHE)

access_token = 'BQDVTDFtgdzbveQniOSi6GMGJU7O6HDH43aNyHLnWc36lHxv89yMbEep6kfyEo-kciKREeHhkDq5axMglZvfkFwWUkddzWsOyvqb4BCgexlR-rYP6J-FuSrU5krdjHjGPjX6LwTwVhw6wvoFZaZSwe5OXsKiZ8FB1AMtteRGAyVdYVI7eDJSLk3jn6ZmJGmMOmHd4bo'


sp = spotipy.Spotify(access_token)

# this will read current player and get the the tempo, duration, song id, and if the song is currently playing
def getsong():
    playback = sp.current_playback()
    isplaying = playback['is_playing']
    songid = playback['item']['uri']
    result = []
    result.append(isplaying)
    result.append(songid)

    song = []
    song = str(songid)
    playing = []
    playing = isplaying

    tempo = 0
    audiofeat = sp.audio_features(song)
    tempo = (audiofeat[0]['tempo'])

    duration = 0
    audiofeat = sp.audio_features(song)
    duration = (audiofeat[0]['duration_ms'])

    merge = []
    merge.append(playing)
    merge.append(tempo)
    merge.append(duration)
    merge.append(song)
    merge.append('Placeholder')

    return jsonify(merge)

#get uri or song id of song
def songuri():
    playback = sp.current_playback()
    songid = playback['item']['uri']
    song = str(songid)
    return song

#get tempo of song
def tempo():
    playback = sp.current_playback()
    songid = playback['item']['uri']
    song = str(songid)
    audiofeat = sp.audio_features(song)
    tempo = (audiofeat[0]['tempo'])
    return tempo

#pause the current song in the spotify player
def pauseback():

    sp.pause_playback(device_id='283ff0b54ce659c556ce668980058488f56ed873')


#get the next song in the playlist and start playing it
def nextsong():

    sp.next_track(device_id='283ff0b54ce659c556ce668980058488f56ed873')

#start the song to sync with lights
def startsong():

    sp.seek_track(0, device_id='283ff0b54ce659c556ce668980058488f56ed873')
    sp.start_playback(device_id='283ff0b54ce659c556ce668980058488f56ed873')

@app.route('/refresh')
def refresh():
    playback = sp.current_playback()
    songid = playback['item']['uri']
    song = str(songid)
    audiofeat = sp.audio_features(song)
    duration = (audiofeat[0]['duration_ms'])
    duration = duration - 10
    time.sleep(2)
    nextsong()
    getsong()
    return getsong()


@app.route('/')
def index():
    print
    "It is running"
    return getsong()



if __name__ == "__main__":
    app.run(debug=True, port=PORT)