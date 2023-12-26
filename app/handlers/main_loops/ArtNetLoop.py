from handlers.wled import WLEDArtNet
from utils.async_utils import ManagedCoroutineFunction


class ArtNetLoop(ManagedCoroutineFunction):
    """
    Loop for animating WLED devices via ArtNet

    .exit() should be used instead of .stop() to ensure that the ArtNet refresh is stopped
    """
    def __init__(self, wled_handler: WLEDArtNet):
        self.wled_handler: WLEDArtNet = wled_handler
        super().__init__()

    def exit(self):
        self.wled_handler.artnet_handler.node.stop_refresh()
        self.stop()

    async def _main_function(self):
        await self.wled_handler.animate()

    async def _stop_function(self):
        pass
