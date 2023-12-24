from handlers.wled import WLEDArtNet
from utils.async_utils import ManagedCoroutineFunction


class ArtNetLoop(ManagedCoroutineFunction):
    def __init__(self, handler: WLEDArtNet):
        self.handler: WLEDArtNet = handler
        super().__init__()

    async def _main_function(self):
        await self.handler.animate()

    async def _stop_function(self):
        pass
