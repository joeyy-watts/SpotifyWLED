"""
Classes for interacting with Spotify API
"""

import spotipy
from spotipy.oauth2 import SpotifyOAuth

class TrackObject:
    def __init__(self, track_dict):
        self.track_name = track_dict["item"]["name"]
        self.progress = track_dict["progress_ms"]
        self.track_length = track_dict["item"]["duration_ms"]
        self.cover_url = track_dict["item"]["album"]["images"][0]["url"]
class SpotifyAPIHandler:
    def __init__(self, client_id: str, client_secret: str):
        self.spotify = spotipy.Spotify(auth_manager=SpotifyOAuth(
            client_id=client_id,
            client_secret=client_secret,
            redirect_uri="http://localhost:8080",
            scope="user-read-currently-playing,user-read-playback-state"))

    def get_current_track(self):
        track = self.spotify.currently_playing()
        print(f"track is {track}")
        return TrackObject(track)