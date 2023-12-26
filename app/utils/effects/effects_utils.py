"""
Various utilities related to effects
"""

BLACK_THRESHOLD = 30

def is_black(rgb: tuple[int, int, int]) -> bool:
    """
    Checks if a pixel is black

    :param rgb: pixel RGB value
    :return: True if black, False otherwise
    """
    r, g, b = rgb
    return all([r < BLACK_THRESHOLD, g < BLACK_THRESHOLD, b < BLACK_THRESHOLD])