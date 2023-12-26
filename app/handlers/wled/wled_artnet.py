from handlers.artnet.artnet_handler import ArtNetHandler, WLEDArtNetMode
from handlers.spotify_api_handler import SpotifyAPIHandler
from handlers.wled.artnet.animations import PlayCover, PauseCover, IdleCover, AnimateCover
from handlers.wled.wled_handler import BaseWLEDHandler


class WLEDArtNet(BaseWLEDHandler):
    """
    ArtNet handler for WLED devices
    """
    def __init__(self, address: str, width: int, height: int, spotify_handler: SpotifyAPIHandler):
        super().__init__(address, width, height)
        self.api_handler = spotify_handler
        self.current_track = self.api_handler.update_current_track()
        self.artnet_handler = ArtNetHandler(address, 6454, width * height, WLEDArtNetMode.MULTI_RGB)

        self.animation: AnimateCover = None

    """
    Get functions for frontend
    """
    async def get_current_track(self):
        return self.current_track

    # can't really be cached, so not making this available for now
    # async def get_queue(self):
    #     return self.api_handler.spotify.queue()

    async def get_audio_features(self):
        return self.api_handler.get_audio_features()

    """
    Entrypoint for animations
    """
    async def animate(self):
        # idle animation, if no track is playing
        if self.current_track.track_id is None:
            self.animation = IdleCover(self)

        # run appropriate animation (play/pause)
        if self.current_track.is_playing:
            self.animation = PlayCover(self)
        else:
            self.animation = PauseCover(self)

        await self.animation.run()