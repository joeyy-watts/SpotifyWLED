"""
Class to interact with WLED server
"""
import io
from time import sleep

import requests
from PIL import Image

MAX_PER_REQUEST = 256
BRIGHTNESS = 80    # brightness from 0-255
WLED_JSON_UPDATE_PATH = "/json/state"
WLED_POST_DELAY = 0.1

headers = {"Content-Type": "application/json"}

class WLEDHandler():
    def __init__(self, address: str, width: int, height: int):
        self.address = address
        # size in WxH format
        self.size = (width, height)

    def __download_image(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return response.content

    def __downscale_image(self, image):
        img = Image.open(io.BytesIO(image))
        img.thumbnail(self.size)
        return img

    def __convert_image_to_json(self, image):
        # TODO: implement some brightness scaling for bright colors
        # TODO: implement other color addressing modes (Hybrid, Range)
        pixel_data = list(image.convert("RGB").getdata())
        segmented_data = []
        color_index = 0

        while color_index < len(pixel_data):
            print(f"color_index is {color_index}")
            segment = {"seg": {"id": 0, "i": []}}
            segment["seg"]["i"].append(color_index)

            for i in range(MAX_PER_REQUEST + 1):
                if color_index >= len(pixel_data):
                    break

                r, g, b = pixel_data[color_index]
                hex_color = f"{r:02x}{g:02x}{b:02x}"
                segment["seg"]["i"].append(hex_color)

                color_index += 1

            segmented_data.append(segment)

        return segmented_data

    def __format_image(self, cover_url: str):
        image = self.__download_image(cover_url)
        image = self.__downscale_image(image)
        image = self.__convert_image_to_json(image)
        return image

    def __send_json(self, headers, json, path: str):
        """
        :param data: JSON object to be sent to WLED
        :return: nothing
        """
        headers["Content-Length"] = str(len(json))

        requests.post(
            f"{self.address}{path}",
            json=json,
            headers=headers
        )

    def __get_current_state(self):
        """
        gets the current state of the WLED target
        """
        resp = requests.get(f"{self.address}/json/state")
        print(f"sending request :: {self.address}/json/state")
        print(f"resp is :: {resp.text}")
        return resp.json()

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
        if self.__get_current_state()["on"] is False:
            return False
        else:
            # TODO: have to implement some way to check if WLED is in "Spotify mode"
            # maybe use "v" flag, and check current WLED state if it matches the album cover
            return True

    def update_cover(self, cover_url: str):
        """
        updates WLED target with album cover
        # TODO: add some warnings (flashing light or something when API error)
        """

        if cover_url is not None:
            data = self.__format_image(cover_url)

            for segment in data:
                json = {"on": True,
                        "bri": BRIGHTNESS,
                        "seg": segment["seg"]}

                self.__send_json(headers, json, WLED_JSON_UPDATE_PATH)
                sleep(WLED_POST_DELAY)
        else:
            json = {"on": False}
            self.__send_json(headers, json, WLED_JSON_UPDATE_PATH)

    def on(self, on_state: bool):
        """
        turns on/off WLED target
        """
        json = {"on": on_state}
        self.__send_json(headers, json, WLED_JSON_UPDATE_PATH)
