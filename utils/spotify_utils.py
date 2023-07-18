"""
Utility functions related to the Spotify API
"""
from handlers.spotify_api_handler import TrackObject
import requests


def calculate_remaining_time(track: TrackObject):
    """
    Calculates remaining time in milliseconds
    """
    return track.track_length - track.progress


def download_cover(track: TrackObject):
    """
    Downloads cover from track object
    """
    return requests.get(track.cover_url)