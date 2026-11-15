import pymupdf
import pytesseract
from PIL import Image

pytesseract.pytesseract.tesseract_cmd = (
    r"C:\Program Files\Tesseract-OCR\tesseract.exe"
)

pdf_path = "data/raw/pmmy_faq.pdf"

doc = pymupdf.open(pdf_path)

print("Total PDF pages:", len(doc))

page = doc[0]

pix = page.get_pixmap(matrix=pymupdf.Matrix(2, 2))

image = Image.frombytes(
    "RGB",
    [pix.width, pix.height],
    pix.samples
)

text = pytesseract.image_to_string(image, lang="eng")

print("\nOCR TEXT FROM PAGE 1:\n")
print(text)

print("\nExtracted characters:", len(text))
