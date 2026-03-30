import json
import os
import re
import csv
from rapidfuzz import fuzz

from preprocess import preprocess_image
from tesseract_extractor import extract_tesseract
from mistral_extractor import extract_mistral

DATA_DIR = "data/sample_docs"
GROUND_TRUTH_PATH = "data/ground_truth.json"
PREDICTIONS_PATH = "outputs/predictions.json"
METRICS_PATH = "outputs/metrics.csv"


def normalize_value(value):
    if value is None:
        return ""
    return str(value).strip()


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


def parse_mistral_fields(text):
    cleaned = text.strip()

    cleaned = cleaned.replace("```json", "").replace("```", "").strip()

    try:
        parsed = json.loads(cleaned)
        return {
            "invoice_number": normalize_value(parsed.get("invoice_number", "")),
            "date": normalize_value(parsed.get("date", "")),
            "vendor": normalize_value(parsed.get("vendor", "")),
            "total_amount": normalize_value(parsed.get("total_amount", "")),
        }
    except Exception:
        return {
            "invoice_number": "",
            "date": "",
            "vendor": "",
            "total_amount": "",
        }


def compute_field_score(predicted, actual):
    predicted = normalize_value(predicted)
    actual = normalize_value(actual)

    if predicted == actual:
        return 100.0

    return float(fuzz.ratio(predicted, actual))


def evaluate_prediction(document, model, predicted_fields, ground_truth, latency, cost):
    gt_fields = ground_truth.get(document, {})

    field_names = ["invoice_number", "date", "vendor", "total_amount"]
    scores = {}

    for field in field_names:
        predicted = predicted_fields.get(field, "")
        actual = gt_fields.get(field, "")
        scores[field] = compute_field_score(predicted, actual)

    avg_accuracy = sum(scores.values()) / len(field_names)

    return {
        "document": document,
        "model": model,
        "invoice_number_score": round(scores["invoice_number"], 2),
        "date_score": round(scores["date"], 2),
        "vendor_score": round(scores["vendor"], 2),
        "total_amount_score": round(scores["total_amount"], 2),
        "accuracy": round(avg_accuracy, 2),
        "latency": round(latency, 4),
        "cost": cost,
    }


def main():
    os.makedirs("outputs", exist_ok=True)

    with open(GROUND_TRUTH_PATH, "r") as f:
        ground_truth = json.load(f)

    predictions = []
    metrics = []

    for file in os.listdir(DATA_DIR):
        path = os.path.join(DATA_DIR, file)

        if not os.path.isfile(path):
            continue

        image = preprocess_image(path)

        tesseract_result = extract_tesseract(image)
        tesseract_result["document"] = file
        tesseract_result["fields"] = parse_tesseract_fields(tesseract_result["text"])
        predictions.append(tesseract_result)

        metrics.append(
            evaluate_prediction(
                document=file,
                model=tesseract_result["model"],
                predicted_fields=tesseract_result["fields"],
                ground_truth=ground_truth,
                latency=tesseract_result["latency"],
                cost=tesseract_result["cost"],
            )
        )

        mistral_result = extract_mistral(path)
        mistral_result["document"] = file
        mistral_result["fields"] = parse_mistral_fields(mistral_result["text"])
        predictions.append(mistral_result)

        metrics.append(
            evaluate_prediction(
                document=file,
                model=mistral_result["model"],
                predicted_fields=mistral_result["fields"],
                ground_truth=ground_truth,
                latency=mistral_result["latency"],
                cost=mistral_result["cost"],
            )
        )

    with open(PREDICTIONS_PATH, "w") as f:
        json.dump(predictions, f, indent=2)

    with open(METRICS_PATH, "w", newline="") as f:
        writer = csv.DictWriter(
            f,
            fieldnames=[
                "document",
                "model",
                "invoice_number_score",
                "date_score",
                "vendor_score",
                "total_amount_score",
                "accuracy",
                "latency",
                "cost",
            ],
        )
        writer.writeheader()
        writer.writerows(metrics)

    print(f"Saved predictions to {PREDICTIONS_PATH}")
    print(f"Saved metrics to {METRICS_PATH}")


if __name__ == "__main__":
    main()