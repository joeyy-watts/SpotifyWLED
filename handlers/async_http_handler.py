"""
The HTTP server for the application
"""
import asyncio
from http.server import BaseHTTPRequestHandler
from time import sleep

from handlers.spotify_api_handler import SpotifyAPIHandler
from utils.image_utils import downscale_image
from utils.spotify_utils import calculate_remaining_time

from handlers.wled_handler import WLEDArtNet

# Spotify API has a rate limit per 30-second rolling window
# so we have to be conservative in the polling frequency
# also I don't want to get my Spotify account of many years
# accidentally banned by abusing the API or something
#
# https://developer.spotify.com/documentation/web-api/concepts/rate-limits

POLLING_SECONDS = 5  # period in seconds to poll Spotify API for changes

class AsyncHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, client_id: str, client_secret: str, wled_handler: WLEDArtNet, *args, **kwargs):
        self.api_handler = SpotifyAPIHandler(client_id, client_secret)
        self.wled_handler = wled_handler
        super().__init__(*args, **kwargs)

    async def _start_loop(self):
        """
        initiates listening loop to start updating WLED target with album cover
        """
        # when starting Spotify mode, turn on WLED regardless
        self.wled_handler.on(True)
        current_id = None

        while (True):
            if not self.wled_handler.should_update():
                break
            image = self.api_handler.get_current_track_cover()
            image = downscale_image(image, self.wled_handler.size)

            track = self.api_handler.get_current_track()

            # first iteration, or new track
            if track.is_playing is False:
                await self.wled_handler.pause_cover(image)
            else:
                await self.wled_handler.play_cover(image)

            # if current_id is None or track.track_id != current_id:
            #     # apply play animation
            #
            #     self.wled_handler.play_cover(image)
            #     # self.wled_handler.update_cover(track.cover_url)

            current_id = track.track_id

            remaining_time = calculate_remaining_time(track) / 1000

            if remaining_time < POLLING_SECONDS and track.is_playing:
                sleep(remaining_time)
            else:
                # apply pause animation
                await self.wled_handler.pause_cover(image)
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
