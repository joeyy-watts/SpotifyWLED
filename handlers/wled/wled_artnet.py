import asyncio
from enum import Enum

from handlers.artnet.artnet_handler import ArtNetHandler, WLEDArtNetMode
from handlers.spotify_api_handler import SpotifyAPIHandler
from handlers.wled.wled_handler import BaseWLEDHandler
from utils.effects.effects import PlaybackEffects


class WLEDArtNet(BaseWLEDHandler):

    class WLEDState(Enum):
        PLAYING = 0
        PAUSED = 1

    def __init__(self, address: str, width: int, height: int, spotify_handler: SpotifyAPIHandler):
        super().__init__(address, width, height)
        self.api_handler = spotify_handler
        self.current_tid = self.api_handler.get_current_track().track_id
        self.handler = ArtNetHandler(address, 6454, width * height, WLEDArtNetMode.MULTI_RGB)

    async def play_cover(self, image):
        """
        applies the playing animation to the given cover
        :param image: current track
        :return: an asyncio task
        """
        factors = PlaybackEffects(self.size[0], self.size[1]).generic_play()
        return await asyncio.create_task(self.__animate_cover_task(image, factors, WLEDArtNet.WLEDState.PLAYING))

    async def pause_cover(self, image):
        """
        applies the paused animation to the given cover
        :param image: current track
        :return: an asyncio task
        """
        factors = PlaybackEffects(self.size[0], self.size[1]).pause()
        return await asyncio.create_task(self.__animate_cover_task(image, factors, WLEDArtNet.WLEDState.PAUSED))

    async def __stop_loop(self, stop_event, state: WLEDState):
        self.current_tid = self.api_handler.current_track.track_id
        while not await self.__should_stop(state):
            # update current track every stop lop
            self.api_handler.update_current_track()

            # TODO: change this to use global POLLING_SECONDS
            await asyncio.sleep(5)

        stop_event.set()

    async def __should_stop(self, state: WLEDState):
        current_track = self.api_handler.get_current_track()
        if state == WLEDArtNet.WLEDState.PLAYING:
            # if current state is playing, the loop should break if:
            #   - track is now paused
            #   - track has changed
            if not current_track.is_playing \
                    or current_track.track_id != self.current_tid:
                return True

        if state == WLEDArtNet.WLEDState.PAUSED:
            # if current state is paused, the loop should break if:
            #   - track is now playing
            #   - track has changed, even if paused
            #   - TODO: if WLED is powered off
            if current_track.is_playing \
                    or current_track.track_id != self.current_tid:
                return True

        return False

    async def __animate_cover_task(self, image, factors, state):
        """
        an asyncio task to animate cover in the background
        :param image: image to animate
        :param factors: the animation factors to be applied to the cover
        :return: asyncio coroutine
        """
        # setup stop event
        stop_event = asyncio.Event()
        asyncio.create_task(self.__stop_loop(stop_event, state))

        while True:
            # check for stop event
            if stop_event.is_set():
                # TODO:
                # if stop event is set for PLAYING state, it means:
                #   - song has changed -> break into outer loop to update cover
                #   - song is now paused -> change state ONLY
                # if stop event is set for PAUSED state:
                #   - song has changed -> break into outer loop to update cover
                #   - song is now playing -> change state ONLY
                # so, if still same song, no need to break into outer loop
                # just need to change play state

                stop_event.clear()
                break

            for i in factors:
                await self.handler.set_pixels([[int(r*i), int(g*i), int(b*i)] for r, g, b in image])
