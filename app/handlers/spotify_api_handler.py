"""
Classes for interacting with Spotify API
"""
import inspect
import time
from functools import lru_cache

import spotipy
from spotipy.oauth2 import SpotifyOAuth, SpotifyClientCredentials

from confs.global_confs import IDLE_IMAGE_URL, POLLING_SECONDS


class TrackObject:
    def __init__(self, track_dict):
        if track_dict is not None:
            self.json = track_dict
            self.track_id = track_dict["item"]["id"]
            self.track_name = track_dict["item"]["name"]
            self.progress = track_dict["progress_ms"]
            self.track_length = track_dict["item"]["duration_ms"]
            self.cover_url = track_dict["item"]["album"]["images"][0]["url"]
            self.is_playing = track_dict["is_playing"]
        else:
            self.json = {}
            self.track_id = None
            self.track_name = "Not Playing"
            self.progress = None
            self.track_length = None
            self.cover_url = None
            self.is_playing = False

    def to_dict(self):
        return {
            "track_id": self.track_id,
            "track_name": self.track_name,
            "progress": self.progress,
            "track_length": self.track_length,
            "cover_url": self.cover_url,
            "is_playing": self.is_playing
        }

class AudioFeatures:
    def __init__(self, dict):
        self.json = dict
        self.danceability = dict.get('danceability', 0.0)
        self.energy = dict.get('energy', 0.0)
        self.key = dict.get('key', 0)
        self.loudness = dict.get('loudness', 0.0)
        self.mode = dict.get('mode', 0)
        self.speechiness = dict.get('speechiness', 0.0)
        self.acousticness = dict.get('acousticness', 0.0)
        self.instrumentalness = dict.get('instrumentalness', 0.0)
        self.liveness = dict.get('liveness', 0.0)
        self.valence = dict.get('valence', 0.0)
        self.tempo = dict.get('tempo', 0.0)

    @classmethod
    def empty(cls):
        return AudioFeatures({})

    def is_none(self):
        attributes = [
            self.danceability, self.energy, self.key, self.loudness, self.mode,
            self.speechiness, self.acousticness, self.instrumentalness,
            self.liveness, self.valence, self.tempo
        ]

        return all(value == 0.0 if isinstance(value, float) else value == 0 for value in attributes)

    def to_dict(self):
        return self.json

class SpotifyAPIHandler:
    def __init__(self):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            redirect_uri="http://localhost:8080",
            scope="user-read-currently-playing,user-read-playback-state"))

        self.current_track: TrackObject = TrackObject(None)
        self.audio_features: AudioFeatures = AudioFeatures.empty()
        self.last_api_call_time = time.time()

    def __handle_api_interval(self):
        current_time = time.time()
        diff = current_time - self.last_api_call_time
        self.last_api_call_time = current_time
        if diff < POLLING_SECONDS:
            print(f"WARN - API call interval < {POLLING_SECONDS}s: {diff:.2f}; caller: {inspect.stack()[1].function}")
        else:
            print(f"API call interval: {diff:.2f}")

    def update_current_track(self):
        self.__handle_api_interval()
        self.current_track = TrackObject(self.spotify.currently_playing())
        return self.current_track

    def get_current_track(self):
        return self.current_track

    def get_audio_features(self):
        if self.current_track is None:
            self.update_current_track()

        return self._get_audio_features_cached(self.current_track.track_id)

    @lru_cache(maxsize=32)
    def _get_audio_features_cached(self, track_id):
        self.__handle_api_interval()
        json = self.spotify.audio_features(track_id)
        self.audio_features = AudioFeatures(json[0])
        return self.audio_features

    def get_current_track_cover(self):
        if self.current_track.track_id is None:
            return IDLE_IMAGE_URL
        else:
            return self.current_track.cover_url
