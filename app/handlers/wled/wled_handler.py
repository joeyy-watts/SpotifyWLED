"""
Class to interact with WLED server
"""
import asyncio
from enum import Enum

import requests

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
