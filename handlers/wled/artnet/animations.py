import asyncio
import time
from asyncio import Event
from typing import final

from confs.global_confs import TARGET_FPS, IDLE_TIMEOUT
from handlers.artnet.artnet_handler import ArtNetHandler
from handlers.spotify_api_handler import SpotifyAPIHandler, TrackObject
from utils.async_utils import ManagedCoroutineFunction
from utils.effects.base_effects import EffectData
from utils.effects.effects import PlaybackEffects
from utils.effects.effects_utils import is_black
from utils.image_utils import get_cover


class AnimateCover(ManagedCoroutineFunction):
    def __init__(self,
                 width: int,
                 height: int,
                 handler: ArtNetHandler,
                 api_handler: SpotifyAPIHandler,
                 track: TrackObject
                 ):
        """
        Base class for all animations

        :param handler: ArtNetHandler
        :param image: image to animate
        :param effect_data: the EffectData object with calculated effects
        :param player_state: the player state associated with the animation
        """
        self.handler: ArtNetHandler = handler
        self.api_handler: SpotifyAPIHandler = api_handler
        self.image = get_cover(self.api_handler.get_current_track_cover(), (width, height))
        self.effect_data = self._get_effect_data()
        self.displaying_tid = track.track_id

        super().__init__()

    @final
    async def _main_function(self):
        """
        Main function that plays animation
        """
        for i in self.effect_data.factors:
            # TODO: for brighter pixels, apply factor at 1.0 multiplier
            # for darker pixels, apply factor scaled to absolute brightness

            # TODO: refactor into separate function
            await self.handler.set_pixels([[int(r * i), int(g * i), int(b * i)]
                                           if not is_black((r, g, b)) else
                                           [int(r), int(g), int(b)]
                                           for r, g, b in self.image])

            # have to await according to target FPS
            await asyncio.sleep(self.effect_data.period / TARGET_FPS)

    async def _stop_function(self):
        raise NotImplementedError

    def _get_effect_data(self) -> EffectData:
        raise NotImplementedError


class PlayCover(AnimateCover):
    def __init__(self,
                 width: int,
                 height: int,
                 handler: ArtNetHandler,
                 api_handler: SpotifyAPIHandler,
                 track: TrackObject
                 ):
        self.width = width
        self.height = height
        self.track = track

        super().__init__(width, height, handler, api_handler, track)

    def _get_effect_data(self) -> EffectData:
        return PlaybackEffects(self.width, self.height).bpm_play(self.api_handler.get_audio_features())

    async def _stop_function(self):
        current_track = self.api_handler.update_current_track()

        if not current_track.is_playing \
                or current_track.track_id != self.track.track_id:
            self.stop_event.set()


class PauseCover(AnimateCover):
    def __init__(self,
                 width: int,
                 height: int,
                 handler: ArtNetHandler,
                 api_handler: SpotifyAPIHandler,
                 track: TrackObject
                 ):
        self.width = width
        self.height = height
        self.track = track

        super().__init__(width, height, handler, api_handler, track)

    def _get_effect_data(self) -> EffectData:
        return PlaybackEffects(self.width, self.height).pause()

    async def _stop_function(self):
        current_track = self.api_handler.update_current_track()

        if current_track.is_playing \
                or current_track.track_id != self.track.track_id:
            self.stop_event.set()


class IdleCover(AnimateCover):
    def __init__(self,
                 width: int,
                 height: int,
                 handler: ArtNetHandler,
                 api_handler: SpotifyAPIHandler,
                 track: TrackObject
                 ):
        self.width = width
        self.height = height
        self.track = track
        self.idle_start_time = time.time()

        super().__init__(width, height, handler, api_handler, track)

    def _get_effect_data(self) -> EffectData:
        return PlaybackEffects(self.width, self.height).pause()

    async def _stop_function(self):
        current_track = self.api_handler.update_current_track()

        if time.time() - self.idle_start_time > IDLE_TIMEOUT \
                or current_track.track_id is not None:
            self.stop_event.set()
