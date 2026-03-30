import cv2
import numpy as np
from pdf2image import convert_from_path


def preprocess_image(path):
    if path.lower().endswith(".pdf"):
        pages = convert_from_path(path, first_page=1, last_page=1)
        image = np.array(pages[0])
        image = cv2.cvtColor(image, cv2.COLOR_RGB2BGR)
    else:
        image = cv2.imread(path)

    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray