"""
Class to interact with WLED server
"""
import asyncio

import requests

from handlers.artnet.artnet_handler import ArtNetHandler, WLEDArtNetMode
from utils.effects.effects import PlaybackEffects
from utils.image_utils import download_image, downscale_image, scale_brightness

MAX_PER_REQUEST = 1024   # max colors to be specified in each request to WLED, 256 is the max
TARGET_IMAGE_BRIGHTNESS = 150   # the brightness of image to be scaled to (0 - 255)
ENABLE_IMAGE_BRIGHTNESS_SCALING = True  # enable/disable image brightness scaling
WLED_BASE_BRIGHTNESS = 150    # WLED brightness (0 - 255)
WLED_JSON_UPDATE_PATH = "/json/state"

headers = {"Content-Type": "application/json"}

class BaseWLEDHandler():
    """
    Base class for WLED handlers. Contains common methods to control WLED.
    """
    def __init__(self, address: str, width: int, height: int):
        self.address = address
        # size in WxH format
        self.size = (width, height)

    def _get_current_state(self):
        """
        gets the current state of the WLED target
        """
        resp = requests.get(f"{self.address}/json/state")
        return resp.json()

    def _send_json(self, headers, json, path: str, extra_headers=False):
        """
        :param data: JSON object to be sent to WLED
        :return: nothing
        """
        if extra_headers:
            headers["Content-Length"] = str(len(json))

        requests.post(
            f"{self.address}{path}",
            json=json,
            headers=headers
        )

    def should_update(self):
        """
        checks if WLED target should be updated
        If some animation is running, i.e. "Spotify mode" isn't running
        then should be false.
        """
        # TWO CASES WHERE should_update IS FALSE
        # 1. WLED is off
        # 2. WLED is on, but not in "Spotify mode"

        # WLED is off, then just shouldn't update anymore
        if self._get_current_state()["on"] is False:
            return False
        else:
            # TODO: have to implement some way to check if WLED is in "Spotify mode"
            # maybe use "v" flag, and check current WLED state if it matches the album cover
            return True

    def on(self, on_state: bool):
        """
        turns on/off WLED target
        """
        json = {"on": on_state}
        self._send_json(headers, json, WLED_JSON_UPDATE_PATH)

class WLEDJson(BaseWLEDHandler):
    def __init__(self, address: str, width: int, height: int):
        self.address = address
        # size in WxH format
        super().__init__(width, height)

        # TODO: move to image_utils

    def __convert_image_to_json_single(self, image):
        # TODO: implement other color addressing modes (Hybrid, Range)
        # TODO: fix missing pixel in each segment
        # whatever the segment size is, the last pixel is skipped for some reason
        pixel_data = list(image.convert("RGB").getdata())
        segmented_data = []
        color_index = 0

        while color_index < len(pixel_data):
            print(f"color_index is {color_index}")
            segment = {"seg": {"id": 0, "i": []}}
            segment["seg"]["i"].append(color_index)

            for i in range(MAX_PER_REQUEST):
                r, g, b = pixel_data[color_index]
                hex_color = f"{r:02x}{g:02x}{b:02x}"
                segment["seg"]["i"].append(hex_color)

                color_index += 1

            segmented_data.append(segment)

        return segmented_data

    def update_cover(self, image):
        """
        updates WLED target with album cover
        # TODO: add some warnings (flashing light or something when API error)
        """

        if image is not None:
            image = downscale_image(image, self.size)

            if ENABLE_IMAGE_BRIGHTNESS_SCALING:
                image = scale_brightness(image, TARGET_IMAGE_BRIGHTNESS)

            data = self.__convert_image_to_json_single(image)

            for segment in data:
                json = {"on": True,
                        "bri": WLED_BASE_BRIGHTNESS,
                        "seg": segment["seg"]}
                # TODO: faster updates
                self._send_json(headers, json, WLED_JSON_UPDATE_PATH)
        else:
            json = {"on": False}
            self._send_json(headers, json, WLED_JSON_UPDATE_PATH)

class WLEDArtNet(BaseWLEDHandler):
    def __init__(self, address: str, width: int, height: int):
        super().__init__(address, width, height)
        self.handler = ArtNetHandler(address, 6454, width * height, WLEDArtNetMode.MULTI_RGB)

    async def play_cover(self, image):
        """
        applies the playing animation to the given cover
        :param image: current track
        :return: an asyncio task
        """
        factors = PlaybackEffects(self.size[0], self.size[1]).generic_play()
        return asyncio.create_task(self.__animate_cover_task(image, factors))

    async def pause_cover(self, image):
        """
        applies the paused animation to the given cover
        :param image: current track
        :return: an asyncio task
        """
        factors = PlaybackEffects(self.size[0], self.size[1]).pause()
        return asyncio.create_task(self.__animate_cover_task(image, factors))

    async def __animate_cover_task(self, image, factors):
        """
        an asyncio task to animate cover in the background
        :param track: currently track
        :param factors: the animation factors to be applied to the cover
        :return: asyncio coroutine
        """
        while True:
            for i in factors:
                await self.handler.set_pixels([[int(r*i), int(g*i), int(b*i)] for r, g, b in image])
