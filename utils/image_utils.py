import io
from functools import lru_cache

import requests
from PIL import Image


@lru_cache(maxsize=32)
def get_cover(url: str, size: (int, int)):
    """
    Downloads and processes image from given URL to be displayed on matrix.
    :param url: image URL
    :param size: tuple of (width, height) of image
    :return: [R, G, B] array of pixels
    """
    image = download_image(url)
    image = downscale_image(image, (size[0], size[1]))
    return image_to_rgb_array(image)

def download_image(url: str):
    response = requests.get(url)
    response.raise_for_status()
    return response.content


def downscale_image(image, size):
    img = Image.open(io.BytesIO(image))
    img.thumbnail(size)
    return img

def calculate_average_brightness(image):
    grayscale_image = image.convert("L")
    grayscale_pixels = list(grayscale_image.getdata())
    total_brightness = sum(grayscale_pixels)
    num_pixels = len(grayscale_pixels)
    average_brightness = total_brightness / num_pixels
    return average_brightness

def scale_brightness(image, desired_brightness):
    # TODO: better scaling
    # have to account for: dark spots, dark colored background
    # local scaling if black background
    # scaling for light colors
    image_hsv = image.convert("HSV")
    image_hsv_pixels = list(image_hsv.getdata())

    scale_factor = desired_brightness / calculate_average_brightness(image)

    scaled_hsv_pixels = []
    for pixel in image_hsv_pixels:
        h, s, v = pixel
        scaled_v = int(v * scale_factor)
        scaled_hsv_pixels.append((h, s, scaled_v))

    scaled_image = Image.new("HSV", image.size)
    scaled_image.putdata(scaled_hsv_pixels)

    return scaled_image.convert("RGB")

def image_to_rgb_array(image):
    """
    Takes an image, and converts it to a list of RGB values, to be used with ArtNet

    :param image: input image
    :return: list of lists of RGB values, representing the image
    """
    pixel_data = list(image.convert("RGB").getdata())

    output = [list(pixel) for pixel in pixel_data]
    return output
