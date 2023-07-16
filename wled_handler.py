"""
Class to interact with WLED server
"""


class WLEDHandler():
    def __init__(self, address: str):
        self.address = address

    def update_cover(self, cover_url: str):
        """
        updates WLED target with album cover
        """
        print(f"Updating WLED target with album cover :: {cover_url}")
        # have to implement
        pass

    def get_current_state(self):
        """
        gets the current state of the WLED target
        """
        print("Getting current state of WLED target")
        # have to implement
        pass