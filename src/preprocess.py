from PIL import Image
import cv2
from pdf2image import convert_from_path
import numpy as np
import os

def preprocess_image(path):
    if path.lower().endswith(".pdf"):
        pages = convert_from_path(path, first_page=1, last_page=1)
        image = pages[0]
        image = np.array(image)
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread(path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray