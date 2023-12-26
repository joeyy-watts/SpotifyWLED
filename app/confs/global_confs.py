"""
Various global configurations.
"""

# Target FPS for animations
# I suspect high values cause time shift due to the time to complete setting each frame
# It is suggested to keep it reasonably low
TARGET_FPS = 44

POLLING_SECONDS = 2

IDLE_IMAGE_URL = 'https://play-lh.googleusercontent.com/cShys-AmJ93dB0SV8kE6Fl5eSaf4-qMMZdwEDKI5VEmKAXfzOqbiaeAsqqrEBCTdIEs'

# Idle timeout (in seconds).
# If nothing is playing for this amount of time, the Spotify loop will stop.
IDLE_TIMEOUT = 5 * 60