from handlers.wled.wled_handler import BaseWLEDHandler
from utils.image_utils import downscale_image, scale_brightness

MAX_PER_REQUEST = 1024   # max colors to be specified in each request to WLED, 256 is the max

TARGET_IMAGE_BRIGHTNESS = 150   # the brightness of image to be scaled to (0 - 255)
ENABLE_IMAGE_BRIGHTNESS_SCALING = True  # enable/disable image brightness scaling
WLED_BASE_BRIGHTNESS = 150    # WLED brightness (0 - 255)


class WLEDJson(BaseWLEDHandler):
    def __init__(self, address: str, width: int, height: int):
        self.address = address
        # size in WxH format
        super().__init__(address, width, height)

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