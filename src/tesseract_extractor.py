import pytesseract
import time
import re

def parse_tesseract_fields(text):
    fields = {}

    invoice_match = re.search(r"Invoice Number:\s*(.+)", text, re.IGNORECASE)
    date_match = re.search(r"Date:\s*(.+)", text, re.IGNORECASE)
    vendor_match = re.search(r"Vendor:\s*(.+)", text, re.IGNORECASE)
    total_match = re.search(r"Total Amount:\s*(.+)", text, re.IGNORECASE)

    fields["invoice_number"] = invoice_match.group(1).strip() if invoice_match else ""
    fields["date"] = date_match.group(1).strip() if date_match else ""
    fields["vendor"] = vendor_match.group(1).strip() if vendor_match else ""
    fields["total_amount"] = total_match.group(1).strip() if total_match else ""

    return fields

def extract_tesseract(image):
    start = time.time()
    text = pytesseract.image_to_string(image)
    latency = time.time() - start

    return {
        "model": "tesseract",
        "text": text,
        "fields": parse_tesseract_fields(text),
        "latency": latency,
        "cost": 0
    }