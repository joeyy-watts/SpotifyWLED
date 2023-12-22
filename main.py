from handlers.main_http_handler import AioMainHTTPHandler
from utils.common import get_client_id, get_client_secret, WLEDMode
import socket

"""
USER SETTINGS

Adjust these settings according to your WLED setup.
"""
# mDNS or IP address of target WLED device
TARGET = 'wled-frame.local'

# Dimensions of target WLED device
TARGET_WIDTH = 32
TARGET_HEIGHT = 32

"""
There are two modes of operation for WLED:
    - ARTNET: WLED is controlled via ArtNet, supports animations.
    - JSON: WLED is controlled via JSON API, only static images supported.
        This is pretty much deprecated as there is not much potential in it.
"""
WLED_MODE = WLEDMode.ARTNET


"""
Main entrypoint
"""
if __name__ == '__main__':
    handler = AioMainHTTPHandler(
        get_client_id(),
        get_client_secret(),
        socket.gethostbyname(TARGET),
        WLED_MODE,
        TARGET_WIDTH,
        TARGET_HEIGHT
    )

    handler.run()
