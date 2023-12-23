"""
Various global configurations.
"""

# Target FPS for animations
# I suspect high values cause time shift due to the time to complete setting each frame
# It is suggested to keep it reasonably low
TARGET_FPS = 24

POLLING_SECONDS = 3

# Idle timeout (in seconds).
# If nothing is playing for this amount of time, the Spotify loop will stop.
IDLE_TIMEOUT = 5 * 60