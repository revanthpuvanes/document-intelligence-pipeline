import os
import json
import tempfile
from pathlib import Path

import pandas as pd
import streamlit as st

from preprocess import preprocess_image
from tesseract_extractor import extract_tesseract
from mistral_extractor import extract_mistral


# ----------------------------
# Page config
# ----------------------------
st.set_page_config(
    page_title="Document Intelligence Benchmark",
    page_icon="📄",
    layout="wide"
)

# ----------------------------
# Config
# ----------------------------
BASE_DIR = Path(__file__).resolve().parent.parent
OUTPUTS_DIR = BASE_DIR / "outputs"
DEFAULT_DOC_PATH = BASE_DIR / "data" / "sample_docs" / "invoice_1.png"

# Disable Tesseract by default on Streamlit Cloud
RUN_TESSERACT = os.getenv("RUN_TESSERACT", "false").lower() == "true"


# ----------------------------
# Helpers
# ----------------------------
def save_uploaded_file(uploaded_file):
    suffix = Path(uploaded_file.name).suffix.lower()
    if suffix not in [".png", ".jpg", ".jpeg", ".pdf"]:
        suffix = ".png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        return tmp_file.name


def build_summary_cards(results):
    cols = st.columns(len(results))
    for col, result in zip(cols, results):
        with col:
            st.markdown(f"### {result['model'].capitalize()}")
            st.metric("Latency", f"{result.get('latency', 0):.2f}s")
            st.metric("Cost / doc", f"${result.get('cost', 0):.4f}")

            if result.get("error"):
                st.error(result["error"])
            else:
                st.success("Completed")


def render_fields(fields, title):
    st.markdown(f"#### {title}")
    if fields and any(str(v).strip() for v in fields.values()):
        st.json(fields)
    else:
        st.info("No structured fields extracted.")


def run_pipeline(file_path, document_name):
    results = []

    # Tesseract
    if RUN_TESSERACT:
        try:
            image = preprocess_image(file_path)
            tesseract_result = extract_tesseract(image)
            tesseract_result["document"] = document_name
            results.append(tesseract_result)
        except Exception as e:
            results.append({
                "model": "tesseract",
                "document": document_name,
                "text": "",
                "fields": {},
                "latency": 0,
                "cost": 0,
                "error": str(e)
            })

    # Mistral
    try:
        mistral_result = extract_mistral(file_path)
        mistral_result["document"] = document_name
        results.append(mistral_result)
    except Exception as e:
        results.append({
            "model": "mistral",
            "document": document_name,
            "text": "",
            "fields": {},
            "latency": 0,
            "cost": 0.002,
            "error": str(e)
        })

    return results


def load_saved_metrics():
    metrics_path = OUTPUTS_DIR / "metrics.csv"
    if metrics_path.exists():
        return pd.read_csv(metrics_path)
    return None


def load_saved_predictions():
    predictions_path = OUTPUTS_DIR / "predictions.json"
    if predictions_path.exists():
        with open(predictions_path, "r") as f:
            return json.load(f)
    return None


# ----------------------------
# Header
# ----------------------------
st.title("📄 Document Intelligence Benchmark")
st.caption("Compare OCR and vision-language extraction on invoices and documents.")

with st.container():
    st.markdown(
        """
        This app benchmarks document extraction pipelines on:
        - **structured field extraction**
        - **latency**
        - **cost per document**

        Upload your own file or test the app with the default sample invoice.
        """
    )

# ----------------------------
# Sidebar
# ----------------------------
with st.sidebar:
    st.header("⚙️ Settings")
    use_default_sample = st.checkbox("Use default sample document", value=True)
    st.markdown("---")
    st.markdown("### Active models")
    if RUN_TESSERACT:
        st.write("✅ Tesseract")
    else:
        st.write("☁️ Tesseract disabled for cloud deploy")
    st.write("✅ Mistral")

    st.markdown("---")
    st.markdown("### Supported files")
    st.write("PNG, JPG, JPEG")


# ----------------------------
# Input section
# ----------------------------
st.markdown("## Upload Document")

uploaded_file = st.file_uploader(
    "Upload an image or PDF",
    type=["png", "jpg", "jpeg"]
)

selected_path = None
selected_name = None

if use_default_sample and DEFAULT_DOC_PATH.exists():
    selected_path = str(DEFAULT_DOC_PATH)
    selected_name = DEFAULT_DOC_PATH.name
    st.info(f"Using default sample: `{selected_name}`")

elif uploaded_file is not None:
    selected_path = save_uploaded_file(uploaded_file)
    selected_name = uploaded_file.name
    st.success(f"Uploaded file: `{selected_name}`")

elif use_default_sample and not DEFAULT_DOC_PATH.exists():
    st.warning("Default sample file not found. Upload a document manually.")

# ----------------------------
# Preview
# ----------------------------
if selected_path:
    st.markdown("## Document Preview")

    if selected_path.lower().endswith((".png", ".jpg", ".jpeg")):
        st.image(selected_path, caption=selected_name, use_container_width=True)
    else:
        st.info("PDF uploaded. Preview is not rendered here, but extraction will use the first page.")

# ----------------------------
# Run section
# ----------------------------
if selected_path:
    if st.button("🚀 Run Extraction", use_container_width=True):
        with st.spinner("Running extraction pipelines..."):
            results = run_pipeline(selected_path, selected_name)

        st.markdown("## Results Overview")
        build_summary_cards(results)

        st.markdown("## Model Comparison")
        comparison_df = pd.DataFrame(results)
        display_cols = [c for c in ["document", "model", "latency", "cost", "error"] if c in comparison_df.columns]
        st.dataframe(comparison_df[display_cols], use_container_width=True)

        if "latency" in comparison_df.columns and not comparison_df.empty:
            st.markdown("## Latency Comparison")
            latency_df = comparison_df.set_index("model")["latency"]
            st.bar_chart(latency_df)

        st.markdown("## Extraction Details")
        for result in results:
            st.markdown(f"### {result['model'].capitalize()} Output")
            render_fields(result.get("fields", {}), "Structured Fields")
            st.markdown("#### Raw Output")
            st.text(result.get("text", ""))
            
# ----------------------------
# Saved benchmark section
# ----------------------------
st.markdown("---")
st.markdown("## Saved Benchmark Results")

metrics_df = load_saved_metrics()
predictions = load_saved_predictions()

if metrics_df is not None and not metrics_df.empty:
    col1, col2, col3 = st.columns(3)

    with col1:
        avg_accuracy = metrics_df.groupby("model")["accuracy"].mean()
        st.markdown("### Average Accuracy")
        st.bar_chart(avg_accuracy)

    with col2:
        avg_latency = metrics_df.groupby("model")["latency"].mean()
        st.markdown("### Average Latency")
        st.bar_chart(avg_latency)

    with col3:
        avg_cost = metrics_df.groupby("model")["cost"].mean()
        st.markdown("### Average Cost")
        st.bar_chart(avg_cost)

    st.markdown("### Metrics Table")
    st.dataframe(metrics_df, use_container_width=True)

    if {"document", "model", "accuracy"}.issubset(metrics_df.columns):
        st.markdown("### Per-Document Accuracy")
        pivot_df = metrics_df.pivot(index="document", columns="model", values="accuracy")
        st.dataframe(pivot_df, use_container_width=True)
else:
    st.info("No saved metrics found yet. Run `python src/evaluate.py` locally to generate benchmark outputs.")

if predictions:
    st.markdown("### Saved Predictions")
    for item in predictions:
        with st.expander(f"{item.get('document', 'unknown')} — {item.get('model', 'unknown')}"):
            render_fields(item.get("fields", {}), "Structured Fields")
            st.markdown("#### Raw Text / Output")
            st.text(item.get("text", ""))