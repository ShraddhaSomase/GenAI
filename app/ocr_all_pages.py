import pymupdf
import pytesseract
from PIL import Image
from pathlib import Path

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pdf_path = Path("data/raw/pmmy_faq.pdf")
output_path = Path("data/raw/pmmy_ocr.txt")

doc = pymupdf.open(pdf_path)

all_text = []

print("Total pages:", len(doc))

for page_number, page in enumerate(doc, start=1):

    print(f"Processing page {page_number}/{len(doc)}...")

    pix = page.get_pixmap(
        matrix=pymupdf.Matrix(2, 2),
        alpha=False
    )

    image = Image.frombytes(
        "RGB",
        [pix.width, pix.height],
        pix.samples
    )

    text = pytesseract.image_to_string(
        image,
        lang="eng"
    )

    all_text.append(
        f"\n\n--- PAGE {page_number} ---\n{text}"
    )

full_text = "".join(all_text)

output_path.write_text(full_text, encoding="utf-8")

print("\nOCR COMPLETED")
print("Total extracted characters:", len(full_text))
print("Saved to:", output_path)
