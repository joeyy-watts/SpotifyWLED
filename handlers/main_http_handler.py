"""
The HTTP server for the application
"""
import asyncio
from time import sleep

from aiohttp import web

from handlers.spotify_api_handler import SpotifyAPIHandler
from handlers.wled import WLEDArtNet, WLEDJson
from utils.common import WLEDMode
from utils.image_utils import downscale_image, image_to_rgb_array, download_image
from utils.spotify_utils import calculate_remaining_time


# Spotify API has a rate limit per 30-second rolling window
# so we have to be conservative in the polling frequency
# also I don't want to get my Spotify account of many years
# accidentally banned by abusing the API or something
#
# https://developer.spotify.com/documentation/web-api/concepts/rate-limits

POLLING_SECONDS = 5  # period in seconds to poll Spotify API for changes

class AioMainHTTPHandler():
    def __init__(self,
                 client_id: str,
                 client_secret: str,
                 wled_address: str,
                 wled_mode: WLEDMode,
                 width: int,
                 height: int):
        self.app = web.Application()
        self.address = wled_address
        self.api_handler = SpotifyAPIHandler(client_id, client_secret)
        self.width = width
        self.height = height
        self.wled_mode = wled_mode

    async def __get_wled_handler(self, address: str, mode: WLEDMode):
        task = asyncio.create_task(self.__actual_get(address, mode))
        await task
        return task.result()

    async def __actual_get(self, address, mode):
        if mode == WLEDMode.ARTNET:
            return WLEDArtNet(address, self.width, self.height, self.api_handler)
        elif mode == WLEDMode.JSON:
            return WLEDJson(address, self.width, self.height)

    async def __run_loop(self, request):
        """
        runs the correct loop functions according to given WLED handler
        """
        print("running loop!")
        task = asyncio.create_task(self.__get_wled_handler(self.address, self.wled_mode))
        await task
        if self.wled_mode is WLEDMode.ARTNET:
            await self.__artnet_loop(task.result())
        elif self.wled_mode is WLEDMode.JSON:
            await self.__json_loop(task.result())

        return web.Response(text="Started loop")

    async def __artnet_loop(self, handler: WLEDArtNet):
        """
        initiates listening loop to start updating WLED target with album cover

        for ArtNet, polling is handled by the internal WLEDArtNet async stop loops.
        """
        while(True):
            self.api_handler.update_current_track()
            current_track = self.api_handler.get_current_track()

            # nothing is playing, wait and continue loop
            if current_track is None:
                sleep(POLLING_SECONDS)
                continue

            # get current track cover
            image = download_image(current_track.cover_url)
            image = downscale_image(image, (self.width, self.height))
            image = image_to_rgb_array(image)

            # animate according to playback state
            if current_track.is_playing:
                # polling goes inside the break function
                await handler.play_cover(image)
            else:
                await handler.pause_cover(image)


    async def __json_loop(self, wled_handler: WLEDJson):
        """
        initiates listening loop to start updating WLED target with album cover

        for JSON, polling is handled in this class
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

    def run(self, host='0.0.0.0', port=8080):
        self.app.add_routes([
            web.get('/start', self.__run_loop)
        ])
        web.run_app(self.app, host=host, port=port)
