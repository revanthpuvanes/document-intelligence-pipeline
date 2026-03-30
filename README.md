# 📄 Document Intelligence Pipeline

### Benchmarking OCR vs Vision-Language Models for Structured Document Extraction

<img width="1268" height="343" alt="Screenshot from 2026-03-30 19-38-58" src="https://github.com/user-attachments/assets/c759a069-90af-4faf-91cd-264809f0d7d6" />
---

## 🚀 Overview

This project is an **end-to-end document intelligence benchmarking system** that compares traditional OCR engines with modern vision-language models (VLMs) on real-world document extraction tasks.

The system evaluates how well different approaches extract structured data (like invoice fields) from documents, and measures trade-offs across:

* 🎯 **Accuracy**
* ⚡ **Latency**
* 💰 **Cost per document**

---

## 🧠 Why this project?

Most OCR demos stop at raw text extraction.

This project goes further:

* Converts documents → **structured JSON**
* Benchmarks **classical OCR vs multimodal AI**
* Provides **quantitative evaluation + visual dashboard**

👉 This reflects real-world production use cases like:

* invoice processing
* KYC / ID verification
* form automation

---

## 🏗️ Architecture

```
Document → Preprocessing → Extraction → Field Parsing → Evaluation → Dashboard
```

### Pipelines Compared

| Approach          | Description                                     |
| ----------------- | ----------------------------------------------- |
| **Tesseract OCR** | Classical OCR baseline (fast, free)             |
| **Mistral VLM**   | Vision-language model for structured extraction |
<img width="614" height="243" alt="Screenshot from 2026-03-30 19-40-25" src="https://github.com/user-attachments/assets/cc7319e9-ed30-4bc3-aff0-cb68532622ba" />
<img width="614" height="243" alt="Screenshot from 2026-03-30 19-40-06" src="https://github.com/user-attachments/assets/fb25928a-8770-4f59-b423-f3ff0a4907d4" />

---

## ⚙️ Features

* 📄 Supports **images and PDFs**
* 🔍 Extracts structured fields:

  * invoice number
  * date
  * vendor
  * total amount
* 📊 Field-level evaluation with fuzzy matching
* 📈 Benchmark metrics:

  * accuracy
  * latency
  * cost
* 🖥️ Interactive **Streamlit dashboard**
* 📤 Upload your own document and compare models live

---

## 📂 Project Structure

```
document-intelligence-pipeline/
│
├── data/
│   ├── sample_docs/
│   └── ground_truth.json
│
├── src/
│   ├── preprocess.py
│   ├── tesseract_extractor.py
│   ├── mistral_extractor.py
│   ├── evaluate.py
│   └── streamlit_app.py
│
├── outputs/
│   ├── predictions.json
│   └── metrics.csv
│
├── requirements.txt
└── README.md
```

---

## 🛠️ Setup

### 1. Clone the repo

```bash
git clone https://github.com/revanthpuvanes/document-intelligence-pipeline.git
cd document-intelligence-pipeline
```

### 2. Create virtual environment

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -U pip setuptools wheel
pip install -r requirements.txt
```

### 4. Install system dependencies (Ubuntu)

```bash
sudo apt install -y tesseract-ocr poppler-utils
```

### 5. Add environment variables

Create `.env`:

```bash
MISTRAL_API_KEY=your_api_key_here
```

---

## ▶️ Usage

### Run Benchmark

```bash
python src/evaluate.py
```

This generates:

* `outputs/predictions.json`
* `outputs/metrics.csv`

---

### Launch Dashboard

```bash
streamlit run src/streamlit_app.py
```

---

## 📊 Example Results

| Model     | Accuracy | Latency | Cost   |
| --------- | -------- | ------- | ------ |
| Tesseract | 100%     | 0.3s    | $0     |
| Mistral   | 100%     | 5.2s    | $0.002 |

### Key Insight:

* Tesseract is **fast and free**
* Mistral provides **robust structured extraction**, especially on complex layouts

---

## 🧪 Evaluation Methodology

* Field-level comparison against ground truth
* Exact match + fuzzy matching (RapidFuzz)
* Metrics computed per document and aggregated by model

---

## 🖼️ Demo

Upload any invoice (image or PDF) and instantly compare:

* Extracted fields (JSON)
* Raw OCR output
* Latency and cost
<img width="1276" height="401" alt="Screenshot from 2026-03-30 19-39-26" src="https://github.com/user-attachments/assets/6052e2a6-8590-46de-b668-2fabc036791b" />
---

## 🔮 Future Improvements

* Multi-page PDF support
* Additional document types (IDs, forms)
* More OCR engines (PaddleOCR, EasyOCR)
* Advanced layout parsing
* Fine-tuned extraction prompts

---

## 💡 Key Takeaways

* Classical OCR is efficient for clean documents
* Vision-language models excel in **understanding structure**
* Choosing the right approach depends on **accuracy vs cost trade-offs**

---

## 🤝 Acknowledgements

* Tesseract OCR
* Mistral AI
* Streamlit for rapid UI development

---

## 📬 Contact

Feel free to reach out or connect if you're working on document AI, OCR, or multimodal systems.

---

⭐ If you found this useful, consider starring the repo!

