from PIL import Image, ImageDraw, ImageFont
import os
import base64
import numpy as np
import urllib.request

def image_to_64(imag):
    with open(f"{imag}", "rb") as f:
        image_data = f.read()
    print(image_data)
    image_base64 = base64.b64encode(image_data)
    image_base64 = image_base64.decode('utf-8')
    return image_base64

def url_to_64(url):
    try:
        with urllib.request.urlopen(url) as response:
            image_data = response.read()
            image_base64 = base64.b64encode(image_data)
            image_base64 = image_base64.decode('utf-8')
            return image_base64
    except urllib.error.URLError as e:
        print(f"Error opening URL: {e}")
