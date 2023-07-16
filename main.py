from functools import partial
from http.server import HTTPServer

from common import get_client_secret, get_client_id
from server import SpotifyWLEDHTTPHandler
from wled_handler import WLEDHandler

"""
Main entry point for the application
"""

if __name__ == '__main__':
    wled_handler = WLEDHandler("wled-frame.local")

    handler = partial(SpotifyWLEDHTTPHandler, get_client_id(), get_client_secret(), wled_handler)

    server = HTTPServer(('', 8081), handler)
    server.serve_forever()