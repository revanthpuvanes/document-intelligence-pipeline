import os
import json
import tempfile
import pandas as pd
import streamlit as st

from preprocess import preprocess_image
from tesseract_extractor import extract_tesseract
from mistral_extractor import extract_mistral


st.set_page_config(page_title="OCR Benchmark Dashboard", layout="wide")
st.title("Document Intelligence Benchmark")

st.markdown("Upload an invoice image and compare **Tesseract** vs **Mistral**.")

uploaded_file = st.file_uploader(
    "Upload a document (image or PDF)",
    type=["png", "jpg", "jpeg", "pdf"]
)

if uploaded_file is not None:
    suffix = os.path.splitext(uploaded_file.name)[1].lower()
    if suffix not in [".png", ".jpg", ".jpeg"]:
        suffix = ".png"

    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
        tmp_file.write(uploaded_file.read())
        temp_path = tmp_file.name

    st.subheader("Uploaded Document")
    st.image(temp_path, caption=uploaded_file.name, use_container_width=True)

    if st.button("Run Extraction"):
        with st.spinner("Running OCR models..."):
            image = preprocess_image(temp_path)

            tesseract_result = extract_tesseract(image)
            tesseract_result["document"] = uploaded_file.name

            mistral_result = extract_mistral(temp_path)
            mistral_result["document"] = uploaded_file.name

            results = [tesseract_result, mistral_result]
            df = pd.DataFrame(results)

        st.success("Extraction complete.")

        st.subheader("Comparison Table")
        display_cols = [col for col in ["document", "model", "latency", "cost", "error"] if col in df.columns]
        st.dataframe(df[display_cols], use_container_width=True)

        st.subheader("Latency Comparison")
        latency_df = df.set_index("model")["latency"]
        st.bar_chart(latency_df)

        for result in results:
            with st.expander(f"{result['model']} output", expanded=False):
                st.write("**Raw Output:**")
                st.text(result.get("text", ""))

                if result.get("fields"):
                    st.write("**Parsed Fields:**")
                    st.json(result["fields"])

# Optional: show existing benchmark results if available
st.divider()
st.subheader("Saved Benchmark Results")

metrics_path = "outputs/metrics.csv"
predictions_path = "outputs/predictions.json"

if os.path.exists(metrics_path):
    metrics_df = pd.read_csv(metrics_path)

    st.write("**Metrics Table**")
    st.dataframe(metrics_df, use_container_width=True)

    if not metrics_df.empty:
        st.write("**Average Accuracy by Model**")
        accuracy_df = metrics_df.groupby("model", as_index=True)["accuracy"].mean()
        st.bar_chart(accuracy_df)

        st.write("**Average Latency by Model**")
        latency_df = metrics_df.groupby("model", as_index=True)["latency"].mean()
        st.bar_chart(latency_df)

        st.write("**Average Cost by Model**")
        cost_df = metrics_df.groupby("model", as_index=True)["cost"].mean()
        st.bar_chart(cost_df)

if os.path.exists(predictions_path):
    with open(predictions_path, "r") as f:
        predictions = json.load(f)

    st.write("**Saved Predictions**")
    for item in predictions:
        with st.expander(f"{item.get('document', 'unknown')} — {item.get('model', 'unknown')}"):
            if item.get("fields"):
                st.write("**Fields**")
                st.json(item["fields"])

            st.write("**Text**")
            st.text(item.get("text", ""))