from functools import partial
from http.server import HTTPServer

from utils.common import get_client_secret, get_client_id, get_target_address
from handlers.server import SpotifyWLEDHTTPHandler
from handlers.wled_handler import WLEDHandler

"""
Main entry point for the application
"""

if __name__ == '__main__':
    wled_handler = WLEDHandler(get_target_address(), 32, 32)

    handler = partial(SpotifyWLEDHTTPHandler, get_client_id(), get_client_secret(), wled_handler)

    server = HTTPServer(('', 8081), handler)
    server.serve_forever()
