from PIL import Image, ImageDraw, ImageFont
import os

os.makedirs("data/sample_docs", exist_ok=True)

samples = [
    {
        "filename": "invoice_1.png",
        "lines": [
            "INVOICE",
            "Vendor: ABC Corp",
            "Invoice Number: INV-001",
            "Date: 2024-01-10",
            "Total Amount: 129.99"
        ]
    },
    {
        "filename": "invoice_2.png",
        "lines": [
            "INVOICE",
            "Vendor: Tech Supplies Ltd",
            "Invoice Number: INV-002",
            "Date: 2024-02-15",
            "Total Amount: 349.50"
        ]
    },
    {
        "filename": "invoice_3.png",
        "lines": [
            "INVOICE",
            "Vendor: Office Mart",
            "Invoice Number: INV-003",
            "Date: 2024-03-01",
            "Total Amount: 89.00"
        ]
    }
]

for sample in samples:
    img = Image.new("RGB", (900, 500), "white")
    draw = ImageDraw.Draw(img)

    try:
        font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 28)
    except:
        font = ImageFont.load_default()

    y = 40
    for line in sample["lines"]:
        draw.text((40, y), line, fill="black", font=font)
        y += 60

    img.save(os.path.join("data/sample_docs", sample["filename"]))

print("Sample invoices created in data/sample_docs/")