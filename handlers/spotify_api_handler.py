"""
Classes for interacting with Spotify API
"""
import asyncio
import inspect
import pprint
import time
from functools import lru_cache

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from confs.global_confs import IDLE_IMAGE_URL, POLLING_SECONDS


class TrackObject:
    def __init__(self, track_dict):
        if track_dict is not None:
            self.track_id = track_dict["item"]["id"]
            self.track_name = track_dict["item"]["name"]
            self.progress = track_dict["progress_ms"]
            self.track_length = track_dict["item"]["duration_ms"]
            self.cover_url = track_dict["item"]["album"]["images"][0]["url"]
            self.is_playing = track_dict["is_playing"]
        else:
            self.track_id = None
            self.track_name = "Not Playing"
            self.progress = None
            self.track_length = None
            self.cover_url = None
            self.is_playing = False

class AudioFeatures:
    def __init__(self, danceability: float, energy: float, key: int, loudness: float, mode: int,
                 speechiness: float, acousticness: float, instrumentalness: float,
                 liveness: float, valence: float, tempo: float):
        self.danceability = danceability
        self.energy = energy
        self.key = key
        self.loudness = loudness
        self.mode = mode
        self.speechiness = speechiness
        self.acousticness = acousticness
        self.instrumentalness = instrumentalness
        self.liveness = liveness
        self.valence = valence
        self.tempo = tempo

    @classmethod
    def empty(cls):
        return AudioFeatures(0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0)

    def is_none(self):
        attributes = [
            self.danceability, self.energy, self.key, self.loudness, self.mode,
            self.speechiness, self.acousticness, self.instrumentalness,
            self.liveness, self.valence, self.tempo
        ]

        return all(value == 0.0 if isinstance(value, float) else value == 0 for value in attributes)

    @classmethod
    def from_dict(cls, audio_features_dict: dict):
        return cls(
            audio_features_dict.get('danceability', 0.0),
            audio_features_dict.get('energy', 0.0),
            audio_features_dict.get('key', 0),
            audio_features_dict.get('loudness', 0.0),
            audio_features_dict.get('mode', 0),
            audio_features_dict.get('speechiness', 0.0),
            audio_features_dict.get('acousticness', 0.0),
            audio_features_dict.get('instrumentalness', 0.0),
            audio_features_dict.get('liveness', 0.0),
            audio_features_dict.get('valence', 0.0),
            audio_features_dict.get('tempo', 0.0))

class SpotifyAPIHandler:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
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
        # Log API call interval in background
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
        json = self.spotify.audio_features(track_id)
        self.audio_features = AudioFeatures.from_dict(json[0])
        return self.audio_features

    def get_current_track_cover(self):
        if self.current_track.track_id is None:
            return IDLE_IMAGE_URL
        else:
            return self.current_track.cover_url
