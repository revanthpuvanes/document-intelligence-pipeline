import os
import time
import json
import base64

from dotenv import load_dotenv

try:
    from mistralai.client import Mistral
except ImportError:
    Mistral = None

load_dotenv()

PROMPT = """
Extract these fields from the invoice:
- invoice_number
- date
- vendor
- total_amount

Return ONLY valid JSON.
"""


def get_api_key():
    key = os.getenv("MISTRAL_API_KEY", "")
    if key:
        return key

    try:
        import streamlit as st
        return st.secrets.get("MISTRAL_API_KEY", "")
    except Exception:
        return ""


def encode_image(image_path):
    with open(image_path, "rb") as f:
        return base64.b64encode(f.read()).decode("utf-8")


def guess_mime_type(image_path):
    ext = os.path.splitext(image_path)[1].lower()
    if ext == ".pdf":
        return "application/pdf"
    if ext in [".jpg", ".jpeg"]:
        return "image/jpeg"
    return "image/png"


def parse_json_from_text(text):
    cleaned = text.strip()
    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "invoice_number": str(parsed.get("invoice_number", "")).strip(),
            "date": str(parsed.get("date", "")).strip(),
            "vendor": str(parsed.get("vendor", "")).strip(),
            "total_amount": str(parsed.get("total_amount", "")).strip(),
        }
    except Exception:
        return {}


def extract_mistral(image_path):
    start = time.time()

    if Mistral is None:
        return {
            "model": "mistral",
            "text": "",
            "fields": {},
            "latency": 0,
            "cost": 0.002,
            "error": "mistralai import failed"
        }

    api_key = get_api_key()
    if not api_key:
        return {
            "model": "mistral",
            "text": "",
            "fields": {},
            "latency": 0,
            "cost": 0.002,
            "error": "MISTRAL_API_KEY not set"
        }

    try:
        client = Mistral(api_key=api_key)

        file_b64 = encode_image(image_path)
        mime_type = guess_mime_type(image_path)
        file_url = f"data:{mime_type};base64,{file_b64}"

        response = client.chat.complete(
            model="pixtral-12b-2409",
            messages=[
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": PROMPT},
                        {"type": "image_url", "image_url": file_url},
                    ],
                }
            ],
        )

        latency = time.time() - start
        content = response.choices[0].message.content

        return {
            "model": "mistral",
            "text": content,
            "fields": parse_json_from_text(content),
            "latency": latency,
            "cost": 0.002
        }

    except Exception as e:
        latency = time.time() - start
        return {
            "model": "mistral",
            "text": "",
            "fields": {},
            "latency": latency,
            "cost": 0.002,
            "error": str(e)
        }