"""
Classes for interacting with Spotify API
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth

from utils.image_utils import download_image


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

class SpotifyAPIHandler:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8080",
            scope="user-read-currently-playing,user-read-playback-state"))

    def get_current_track(self):
        track = self.spotify.currently_playing()
        return TrackObject(track)

    def get_current_track_cover(self):
        track = self.spotify.currently_playing()
        cover_url = track["item"]["album"]["images"][0]["url"]

        if cover_url is not None:
            return download_image(cover_url)
        else:
            return None
