from handlers.artnet.artnet_handler import ArtNetHandler, WLEDArtNetMode
from handlers.spotify_api_handler import SpotifyAPIHandler
from handlers.wled.artnet.animations import PlayCover, PauseCover, IdleCover
from handlers.wled.wled_handler import BaseWLEDHandler


class WLEDArtNet(BaseWLEDHandler):
    def __init__(self, address: str, width: int, height: int, spotify_handler: SpotifyAPIHandler):
        super().__init__(address, width, height)
        self.api_handler = spotify_handler
        self.current_tid = self.api_handler.get_current_track().track_id
        self.handler = ArtNetHandler(address, 6454, width * height, WLEDArtNetMode.MULTI_RGB)
        self.animating_track = None

    async def animate(self):
        # update current track
        current_track = self.api_handler.update_current_track()

        # idle animation, if no track is playing
        if current_track.track_id is None:
            await IdleCover(
                self.size[0],
                self.size[1],
                self.handler,
                self.api_handler,
                current_track
            ).run()

        # run appropriate animation (play/pause)
        if current_track.is_playing:
            await PlayCover(
                self.size[0],
                self.size[1],
                self.handler,
                self.api_handler,
                current_track
            ).run()
        else:
            await PauseCover(
                self.size[0],
                self.size[1],
                self.handler,
                self.api_handler,
                current_track
            ).run()
