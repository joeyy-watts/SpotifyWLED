"""
The HTTP server for the application
"""
import asyncio
from enum import Enum
from http.server import BaseHTTPRequestHandler
from socketserver import ThreadingMixIn
from time import sleep

from handlers.spotify_api_handler import SpotifyAPIHandler
from utils.common import WLEDMode
from utils.image_utils import downscale_image
from utils.spotify_utils import calculate_remaining_time

from handlers.wled_handler import WLEDArtNet, BaseWLEDHandler, WLEDJson

# Spotify API has a rate limit per 30-second rolling window
# so we have to be conservative in the polling frequency
# also I don't want to get my Spotify account of many years
# accidentally banned by abusing the API or something
#
# https://developer.spotify.com/documentation/web-api/concepts/rate-limits

POLLING_SECONDS = 5  # period in seconds to poll Spotify API for changes

class MainHTTPHandler(BaseHTTPRequestHandler):
    def __init__(self, client_id: str,
                 client_secret: str,
                 wled_address: str,
                 wled_mode: WLEDMode,
                 width: int,
                 height: int,
                 *args, **kwargs):
        self.api_handler = SpotifyAPIHandler(client_id, client_secret)
        self.width = width
        self.height = height
        self.wled_mode = wled_mode
        self.wled_handler = self.__get_wled_handler(wled_address, wled_mode)

        # needed to initialize base HTTP server class correctly
        super().__init__(*args, **kwargs)

    def __get_wled_handler(self, address: str, mode: WLEDMode):
        if mode == WLEDMode.ARTNET:
            return WLEDArtNet(address, self.width, self.height)
        elif mode == WLEDMode.JSON:
            return WLEDJson(address, self.width, self.height)

    def __run_loop(self):
        """
        runs the correct loop functions according to given WLED handler
        """
        if self.wled_mode is WLEDMode.ARTNET:
            self.__artnet_loop(self.wled_handler)
        elif self.wled_mode is WLEDMode.JSON:
            self.__json_loop(self.wled_handler)

    def __artnet_loop(self, handler: WLEDArtNet):
        """
        initiates listening loop to start updating WLED target with album cover
        """
        while(True):
            pass

    def __json_loop(self, wled_handler: WLEDJson):
        """
        initiates listening loop to start updating WLED target with album cover
        """
        # when starting Spotify mode, turn on WLED regardless
        wled_handler.on(True)
        current_id = None

        while (True):
            if not wled_handler.should_update():
                break
            image = self.api_handler.get_current_track_cover()

            track = self.api_handler.get_current_track()

            if current_id is None or track.track_id != current_id:
                wled_handler.update_cover(image)

            current_id = track.track_id

            remaining_time = calculate_remaining_time(track) / 1000

            if remaining_time < POLLING_SECONDS and track.is_playing:
                sleep(remaining_time)
            else:
                sleep(POLLING_SECONDS)

    def do_POST(self):
        if '/' in self.path:
            self.send_response(501)

    def do_GET(self):
        if self.path == '/start':
            self.send_response(200)
            self.send_header("Content-type", "text/html")
            self.end_headers()
            self.__run_loop()
        elif self.path == '/stop':
            # TODO: async and stop loop (manual stop via API)
            pass
