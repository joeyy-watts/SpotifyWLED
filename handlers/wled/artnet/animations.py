import asyncio

from confs.global_confs import TARGET_FPS
from handlers.artnet.artnet_handler import ArtNetHandler
from handlers.wled.WLEDState import WLEDState
from utils.async_utils import ManagedCoroutineFunction
from utils.effects.base_effects import EffectData
from utils.effects.effects_utils import is_black


class AnimateCover(ManagedCoroutineFunction):
    def __init__(self, handler: ArtNetHandler, image, effect_data: EffectData, player_state: WLEDState):
        """
        Class for animating a given image with the given EffectData
        :param handler: ArtNetHandler
        :param image: image to animate
        :param effect_data: the EffectData object with calculated effects
        :param player_state: the player state associated with the animation
        """
        super().__init__()
        self.handler: ArtNetHandler = handler
        self.image = image
        self.effect_data = effect_data
        self.player_state = player_state

    async def _main_function(self):
        """
        plays the play animation
        :param image: image to animate
        :param effect_data: the EffectData object for a given calculated effect
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

    async def _stop_function(self, stop_event):
        pass
