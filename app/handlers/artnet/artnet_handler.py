import asyncio
from enum import Enum
from functools import lru_cache
from math import ceil, floor

from pyartnet import ArtNetNode, Channel, BaseUniverse, output_correction

# ArtNet and WLED related constants
CHANNELS_PER_UNIVERSE = 512

"""
Channel widths for each WLED ArtNet mode:

refer: https://kno.wled.ge/interfaces/e1.31-dmx/
"""
class WLEDArtNetMode(Enum):
    MULTI_RGB = 0
    DIM_MULTI_RGB = 1


# Mapping for WLED ArtNet channel widths
CHANNEL_WIDTH_MAPPING = {
    WLEDArtNetMode.MULTI_RGB: 3,
    WLEDArtNetMode.DIM_MULTI_RGB: 3
}


class ArtNetHandler:
    def __init__(self, target_address: str, port: int, leds: int, mode: WLEDArtNetMode):
        """
        Initializes a handler for an ArtNet node.

        :param target_address: address of the ArtNet node
        :param port: port of the ArtNet node (standard port is 6454; not recommended to change)
        :param leds: number of leds in the ArtNet node
        :param mode: ArtNet mode of the WLED target
        """
        self.node = ArtNetNode(target_address, port)
        self.leds = leds
        self.mode = mode
        self.universes = self.__initialize_universes(mode)
        self.__initialize_channels()

    def __initialize_universes(self, mode: WLEDArtNetMode) -> tuple:
        universes = []

        for i in range(self.__get_num_universe(self.leds, mode)):
            universes.append(self.node.add_universe(i))

        # for u in universes:
        #     u.set_output_correction(output_correction.quadratic)

        return tuple(universes)

    def __initialize_channels(self):
        for idx, u in enumerate(self.universes):
            channel_start = 1

            # for DIM_MULTI_RGB, add first channel for brightness
            if self.mode is WLEDArtNetMode.DIM_MULTI_RGB and idx == 0:
                u.add_channel(start=1, width=1, channel_name='brightness')
                channel_start += 1

            for i in range(self.__get_led_per_universe()):
                u.add_channel(start=channel_start, width=CHANNEL_WIDTH_MAPPING[self.mode])
                channel_start += CHANNEL_WIDTH_MAPPING[self.mode]

    def __get_num_universe(self, leds: int, mode: WLEDArtNetMode):
        leds_per_universe = floor(CHANNELS_PER_UNIVERSE / CHANNEL_WIDTH_MAPPING[mode])
        total_universes = ceil(leds / leds_per_universe)

        return total_universes

    def __get_led_per_universe(self):
        return floor(CHANNELS_PER_UNIVERSE / CHANNEL_WIDTH_MAPPING[self.mode])

    def set_brightness(self, brightness: int):
        self.universes[0]['brightness'].set_values([brightness])

    async def fade_brightness(self, brightness: int, fade_time: int):
        """
        Fades brightness of the WLED to given brightness value.

        This is a BLOCKING operation, as we want to wait for the fade to complete.
        :param brightness: target brightness value [0-255]
        :param fade_time: time to fade, in ms
        :return: None
        """
        if self.mode is not WLEDArtNetMode.DIM_MULTI_RGB:
            raise Exception("Cannot fade brightness for non-dimming mode!")

        self.universes[0]['brightness'].set_fade([brightness], fade_time)

        await self.universes[0]['brightness']

    async def set_pixels(self, pixels: tuple):
        assigned_pixels = self.__assign_pixels(pixels, self.universes)

        await asyncio.gather(*[self.__async_set_pixels(up) for up in assigned_pixels])

    @lru_cache(maxsize=256)
    def __assign_pixels(self, pixels: tuple, universes: tuple):
        """
        Breaks up the given pixels, and assigns the maximum number into each universe.

        To be used for parallely setting pixels in universes.
        :param pixels: list of all input pixels
        :param universes: list of universes in node
        :return: tuple of (universe, pixels, channel_offset)
        """
        # ppu: pixels-per-universe
        ppu = self.__get_led_per_universe()

        universe_to_pixels = []

        for i in range(len(universes)):
            if i == 0 and self.mode is WLEDArtNetMode.DIM_MULTI_RGB:
                offset = 1
            else:
                offset = 0

            pixel_slice = pixels[i * ppu:min((i + 1) * ppu, len(pixels))]

            universe_to_pixels.append(
                (universes[i], tuple(pixel_slice), offset)
            )

        return tuple(universe_to_pixels)

    async def __async_set_pixels(self, upo: tuple[BaseUniverse, tuple, int]):
        """
        Asynchronously sets pixels in a given universe

        :param upo: a tuple of (universe, pixels to set, channel offset)
            - channel_offset: offset of first pixel channel in universe
        :return: None
        """
        universe, pixels, channel_offset = upo
        latest_channel = 1 + channel_offset

        for p in pixels:
            universe[f"{latest_channel}/{CHANNEL_WIDTH_MAPPING[self.mode]}"].set_values(p)
            latest_channel += CHANNEL_WIDTH_MAPPING[self.mode]
