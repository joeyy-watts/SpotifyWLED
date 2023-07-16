"""
The HTTP sever for the application
"""

from http.server import BaseHTTPRequestHandler
from time import sleep

from spotify_api_handler import SpotifyAPIHandler

from spotify_utils import calculate_remaining_time
from wled_handler import WLEDHandler


class SpotifyWLEDHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, client_id:str, client_secret: str, wled_handler: WLEDHandler, *args, **kwargs):
        self.api_handler = SpotifyAPIHandler(client_id, client_secret)
        self.wled_handler = wled_handler
        super().__init__(*args, **kwargs)

    def _start_loop(self):
        """
        initiates listening loop to start updating WLED target with album cover
        """

        while(True):
            track = self.api_handler.get_current_track()

            # TODO: check if WLED is running any effects (is not displaying album cover)
            # if should_stop:
            #     break

            self.wled_handler.update_cover(track.cover_url)

            sleep(calculate_remaining_time(track) / 1000)


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
            # TODO: async and stop loop
            pass


