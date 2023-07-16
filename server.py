"""
The HTTP sever for the application
"""

from http.server import BaseHTTPRequestHandler
from time import sleep

from spotify_api_handler import SpotifyAPIHandler

from wled_handler import WLEDHandler

POLLING_SECONDS = 10  # period in seconds to poll Spotify API for changes

class SpotifyWLEDHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, client_id: str, client_secret: str, wled_handler: WLEDHandler, *args, **kwargs):
        self.api_handler = SpotifyAPIHandler(client_id, client_secret)
        self.wled_handler = wled_handler
        super().__init__(*args, **kwargs)

    def _start_loop(self):
        """
        initiates listening loop to start updating WLED target with album cover
        """
        current_id = None

        while (True):
            track = self.api_handler.get_current_track()

            # TODO: check if WLED is running any effects (is not displaying album cover)
            # if should_stop:
            #     break

            # first iteration, or new track
            if current_id is None or track.track_id != current_id:
                self.wled_handler.update_cover(track.cover_url)

            current_id = track.track_id

            sleep(POLLING_SECONDS)

    def do_POST(self):
        if '/' in self.path:
            self.send_response(501)

    def do_GET(self):
        if self.path == '/start':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self._start_loop()
        elif self.path == '/stop':
            # TODO: async and stop loop (manual stop via API)
            pass
