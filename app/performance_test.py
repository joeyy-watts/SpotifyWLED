"""
An ad-hoc script to test ArtNet performance.
"""
import os
import socket

from handlers.main_loops.ArtNetLoop import ArtNetLoop
from handlers.spotify_api_handler import SpotifyAPIHandler
from handlers.wled import WLEDArtNet

TARGET = os.environ['TARGET']
TARGET_WIDTH = int(os.environ['TARGET_WIDTH'])
TARGET_HEIGHT = int(os.environ['TARGET_HEIGHT'])

if __name__ == '__main__':
    try:
        target_ip = socket.gethostbyname(TARGET)
    except socket.gaierror:
        print(f'Could not resolve IP address for {TARGET}.')
        exit(1)
    except Exception as e:
        print(f'Unknown error occurred while resolving IP address for {TARGET}.\nCaught exception: {e}')
        exit(1)

    await ArtNetLoop(
        WLEDArtNet(
            target_ip,
            TARGET_WIDTH,
            TARGET_HEIGHT,
            SpotifyAPIHandler()
        )
    ).run()

