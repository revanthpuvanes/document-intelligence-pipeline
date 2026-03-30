from paddleocr import PaddleOCR
import time

ocr = PaddleOCR(use_angle_cls=True, lang='en')

def extract_paddle(image_path):
    start = time.time()
    result = ocr.ocr(image_path)

    text = " ".join([line[1][0] for line in result[0]])
    latency = time.time() - start

    return {
        "model": "paddleocr",
        "text": text,
        "fields": {},
        "latency": latency,
        "cost": 0
    }