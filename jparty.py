from flask import Flask
from flask import jsonify
from yeelight import Bulb, discover_bulbs
from yeelight import flow
from yeelight import *
import requests
from timeit import Timer
import time
import socket

#from .utils import _clamp

#import base64
#import urllib
import spotipy
from spotipy import oauth2
#import spotipy.util as util
#import json

app = Flask(__name__)

ip = None
bulbs = discover_bulbs()
print(bulbs)
ip = bulbs[0]['ip']
Bulb.set_music = True

PORT = 8080
SPOTIPY_CLIENT_ID = "40673f62ed1d44b387160bf9e82a2de1"
SPOTIPY_CLIENT_SECRET = '7a3ee97f8220400e9edf8a3b01fcc84f'
SPOTIPY_REDIRECT_URI = 'http://localhost:8080'
SCOPE = 'user-library-read user-read-playback-state user-modify-playback-state'
CACHE = '.spotipyoauthcache'
SPOTIPY_PLAYLIST_API = "https://api.spotify.com/v1/playlists/{1IAY7B3G3MKO9Pre7cxA9A}/tracks"

sp_oauth = oauth2.SpotifyOAuth(SPOTIPY_CLIENT_ID, SPOTIPY_CLIENT_SECRET, SPOTIPY_REDIRECT_URI, scope=SCOPE,
                               cache_path=CACHE)

access_token = 'BQAMT3Gzj-Is0XLxfWJCd4ymP90hVSfpqW35LYeNsGv2Pci8MBXkV_0oXSWE7MhdsxiJmBmca0U-Od8psKTHn22aeqKHWly3TzObOOAXv0zfAo_6cwQ2c4TGuT9stJrsLCWOjGp7MfoGsg4aNHamS4i9Y5FChExPe7B00xfVaVnngp9udJQiSerbJiPXuJz4wvXJopg'

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

    energy = 0
    audiofeat = sp.audio_features(song)
    energy = (audiofeat[0]['energy'])

    merge = []
    merge.append(playing)
    merge.append(tempo)
    merge.append(duration)
    merge.append(song)
    merge.append(energy)

    return jsonify(merge)

#get uri of song
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

def double():

    bpm = tempo() * 2
    duration = int(60000 / bpm)
    transitions = [
        HSVTransition(0, 100, duration=duration, brightness=100),
        HSVTransition(0, 100, duration=duration, brightness=1),
        HSVTransition(90, 100, duration=duration, brightness=100),
        HSVTransition(90, 100, duration=duration, brightness=1),
        HSVTransition(180, 100, duration=duration, brightness=100),
        HSVTransition(180, 100, duration=duration, brightness=1),
        HSVTransition(270, 100, duration=duration, brightness=100),
        HSVTransition(270, 100, duration=duration, brightness=1),
    ]
    bulb = Bulb(ip)
    flow = Flow(
        count=0,  # Cycle forever.
        transitions=transitions
    )

    bulb.start_flow(flow)

def advanced():
    playback = sp.current_playback()
    isplaying = playback['is_playing']
    songid = playback['item']['uri']
    song = str(songid)
    analysis = sp.audio_analysis(song)

    beats = analysis['beats']
    start = analysis['beats'][0]['start']
    beats = list(map(lambda item: item["duration"], beats))
    beats.insert(0, start)

    return beats


def half():
    bulb = Bulb
    duration = advanced()
    length = len(duration)
    while length >=1:

        if not duration:
            break

        bulb = Bulb(ip,effect='smooth', duration = duration[0])
        bulb.set_rgb(255,0,0)
        bulb.turn_on()
        duration.pop(0)

        bulb = Bulb(ip, effect='smooth', duration=duration[0])
        bulb.turn_off()
        duration.pop(0)

        bulb = Bulb(ip, effect='smooth', duration=duration[0])
        bulb.set_rgb(0,255,0)
        bulb.turn_on()
        duration.pop(0)
        bulb.turn_off()
        duration.pop(0)


def duration():
    playback = sp.current_playback()
    songid = playback['item']['uri']
    song = str(songid)
    audiofeat = sp.audio_features(song)
    duration = (audiofeat[0]['duration_ms'])
    return duration

def keepgoing():
    getsong()

    timer()



def timer():
    d = duration()
    d = (d / 1000)
    print(d)
    time.sleep(d)
    keepgoing()
    return getsong()

@app.route('/analyse')
def analyse():
    playback = sp.current_playback()
    isplaying = playback['is_playing']
    songid = playback['item']['uri']
    song = str(songid)
    analysis = sp.audio_analysis(song)

    beats = analysis['beats']
    start = analysis['beats'][0]['start']
    beats = list(map(lambda item: item["duration"], beats))
    beats.insert(0, start)

    return jsonify(beats)


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


@app.route("/disco")
def disco():
    """
    Color changes to the beat.
    :param int bpm: The beats per minute to pulse to.
    :returns: A list of transitions.
    :rtype: list
    """
    bpm = tempo()
    duration = int(60000 / bpm)
    transitions = [
        HSVTransition(0, 100, duration=duration, brightness=100),
        HSVTransition(0, 100, duration=duration, brightness=1),
        HSVTransition(90, 100, duration=duration, brightness=100),
        HSVTransition(90, 100, duration=duration, brightness=1),
        HSVTransition(180, 100, duration=duration, brightness=100),
        HSVTransition(180, 100, duration=duration, brightness=1),
        HSVTransition(270, 100, duration=duration, brightness=100),
        HSVTransition(270, 100, duration=duration, brightness=1),
    ]
    bulb = Bulb(ip)
    flow = Flow(
        count=0,  # Cycle forever.
        transitions=transitions
    )

    bulb.start_flow(flow)

    return jsonify({'status': 'OK'})

@app.route("/reset")
def reset():

   if ip is None:
       return jsonify({'status': 'error', 'message': 'no bulb found'})

   bulb = Bulb(ip)

   try:

       bulb.set_rgb(255, 255, 255)


   except:
       return jsonify({'status': 'error', 'message': 'could not adjust brightness'})

   return jsonify({'status': 'OK'})


@app.route("/party")
def party():

   if ip is None:
       return jsonify({'status': 'error', 'message': 'no bulb found'})

   bulb = Bulb(ip)

   try:

       bulb.set_rgb(255, 0, 0)


   except:
       return jsonify({'status': 'error', 'message': 'could not adjust brightness'})

   return jsonify({'status': 'OK'})

@app.route("/on")
def on():

   if ip is None:
      return jsonify({'status': 'error', 'message': 'no bulb found'})

   bulb = Bulb(ip)

   try:
      bulb.turn_on()
   except:
      return jsonify({'status': 'error', 'message': 'could not turn on bulb'})

   return jsonify({'status': 'OK'})

@app.route("/off")
def off():

  if ip is None:
      return jsonify({'status': 'error', 'message': 'no bulb found'})

  bulb = Bulb(ip)

  try:
      bulb.turn_off()
  except:
      return jsonify({'status': 'error', 'message': 'could not turn off bulb'})

  return jsonify({'status': 'OK'})

@app.route("/brightness")
def brightness():

   if ip is None:
       return jsonify({'status': 'error', 'message': 'no bulb found'})

   bulb = Bulb(ip)

   try:
       bulb.set_brightness(10)

   except:
       return jsonify({'status': 'error', 'message': 'could not adjust brightness'})


   return jsonify({'status': 'OK'})

@app.route('/lsd')
def lsd(duration=3000, brightness=100):
    """
    Gradual changes to a pleasing, trippy palette.

    :param int brightness: The brightness of the transition.

    :returns: A list of transitions.
    :rtype: list
    """
    hs_values = [(3, 85), (20, 90), (55, 95), (93, 50), (198, 97)]
    transitions = [HSVTransition(hue, saturation, duration=duration, brightness=brightness) for hue, saturation in hs_values]

    bulb = Bulb(ip)
    flow = Flow(
        count=0,  # Cycle forever.
        transitions=transitions
    )

    bulb.start_flow(flow)
    return ("All good boi")


@app.route('/start')
def start():

    nextsong()
    getsong()
    disco()
    return getsong()

@app.route('/next')
def next():
    nextsong()

@app.route('/doubletime')
def doubletime():
    nextsong()
    getsong()
    double()
    return getsong()

@app.route('/test')
def test():

    nextsong()
    getsong()
    half()
    return getsong()

if __name__ == "__main__":
    app.run(debug=True, port=PORT)

