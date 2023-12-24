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
    try:
        target_ip = socket.gethostbyname(TARGET)
    except socket.gaierror:
        print(f'Could not resolve IP address for {TARGET}.')
        exit(1)
    except Exception as e:
        print(f'Unknown error occurred while resolving IP address for {TARGET}.\nCaught exception: {e}')
        exit(1)

    handler = AioMainHTTPHandler(
        get_client_id(),
        get_client_secret(),
        target_ip,
        WLED_MODE,
        TARGET_WIDTH,
        TARGET_HEIGHT
    )

    print(f"Starting SpotifyWLED for device: {TARGET} ({target_ip})")

    handler.run()
