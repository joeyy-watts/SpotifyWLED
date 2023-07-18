import io

import requests
from PIL import Image


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