import json
import re
from dataclasses import asdict
from html.parser import HTMLParser
from pathlib import Path

from pypdf import PdfReader

from app.models import Record

RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/records.json")
STANDUP_OUTPUT = Path("data/standup_faq.txt")
OCR_FILE = RAW_DIR / "pmmy_ocr.txt"
MANIFEST_FILE = Path("data/source_manifest.json")

PMMY_SOURCE = (
    "https://static.pib.gov.in/WriteReadData/"
    "specificdocs/documents/2025/sep/"
    "doc2025927648901.pdf"
)

STANDUP_SOURCE = (
    "https://static.pib.gov.in/WriteReadData/"
    "specificdocs/documents/2022/apr/"
    "doc20224535701.pdf"
)


class PageTextParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        cleaned = data.strip()
        if cleaned:
            self.parts.append(cleaned)


def extract_pdf(filename):

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found. Run python -m app.fetch first."
        )

    reader = PdfReader(str(path))

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    if not text.strip():
        raise ValueError(f"No readable text found in {filename}")

    return text


def extract_html(filename):

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found. Run python -m app.fetch first."
        )

    parser = PageTextParser()
    parser.feed(path.read_text(encoding="utf-8"))

    return "\n".join(parser.parts)


def normalize(text):
    return re.sub(r"\s+", " ", text).strip()


def extract_mudra_records(pmmy_text):

    text = normalize(pmmy_text)

    category_patterns = [
        (
            "Shishu",
            r"Shishu\s+Loans?\s+"
            r"(upto\s+Rs\.?\s*50,000/?-?)"
        ),
        (
            "Kishor",
            r"Kishor\s+Loans?\s+"
            r"(above\s+Rs\.?\s*50,000\s*/?-?\s*and\s+upto\s+"
            r"Rs\.?\s*5\.?00\s+Lakh)"
        ),
        (
            "Tarun Plus",
            r"Tarun\s+Plus\*?\s+Loans?\s+"
            r"(above\s+Rs\.?\s*10\.?00\s+lakh\s+and\s+"
            r"upto\s+Rs\.?\s*20\.?00\s+lakh)"
        ),
        (
            "Tarun",
            r"Tarun\s+Loans?\s+"
            r"(above\s+Rs\.?\s*5\.?00\s+lakh\s+and\s+"
            r"upto\s+Rs\.?\s*10\.?00\s+lakh)"
        )
    ]

    eligibility_match = re.search(
        r"Any Indian Citizen who has a business plan "
        r"for a non-farm income generating activity.*?"
        r"MUDRA loans",
        text,
        re.IGNORECASE
    )

    if not eligibility_match:
        raise ValueError(
            "Could not extract eligibility from PMMY FAQ OCR."
        )

    eligibility = eligibility_match.group(0)

    repayment_match = re.search(
        r"Cash Credit\s*[-:]\s*Yearly review.*?"
        r"Term Loan\s*[-:]\s*Maximum tenure should not exceed 7 years",
        text,
        re.IGNORECASE
    )

    if not repayment_match:
        raise ValueError(
            "Could not extract repayment details from PMMY FAQ OCR."
        )

    repayment = repayment_match.group(0)

    records = []

    for category, pattern in category_patterns:

        match = re.search(pattern, text, re.IGNORECASE)

        if not match:
            raise ValueError(
                f"Could not extract loan amount for {category}."
            )

        amount = normalize(match.group(1))

        if category == "Tarun Plus":
            category_eligibility = (
                eligibility
                + ". Additionally, the applicant must have "
                "successfully repaid a previous Tarun-category loan."
            )
        else:
            category_eligibility = eligibility

        record = Record(
            loan_category=category,
            amount_range=amount,
            who_can_apply=category_eligibility,
            margin_or_contribution=(
                "Not specified in the extracted PMMY FAQ. "
                "Confirm with the lending institution."
            ),
            repayment=repayment,
            source_doc=(
                f"{PMMY_SOURCE} "
                "(PMMY FAQ, pages 4, 18-19 and 21)"
            )
        )

        records.append(asdict(record))

    return records


def save_manifest():

    manifest = {
        "project": "MudraMitra",
        "documents": [
            {
                "filename": "pmmy_faq.pdf",
                "url": PMMY_SOURCE,
                "local_path": "data/raw/pmmy_faq.pdf",
                "ocr_output": "data/raw/pmmy_ocr.txt"
            },
            {
                "filename": "standup_faq.pdf",
                "url": STANDUP_SOURCE,
                "local_path": "data/raw/standup_faq.pdf"
            }
        ],
        "download_command": "python -m app.fetch",
        "ocr_command": "python -m app.ocr_all_pages",
        "ingestion_command": "python -m app.ingest"
    }

    MANIFEST_FILE.parent.mkdir(parents=True, exist_ok=True)

    MANIFEST_FILE.write_text(
        json.dumps(manifest, indent=4),
        encoding="utf-8"
    )


def ingest_data():

    try:

        print("\n========== MUDRAMITRA DATA INGESTION ==========")

        if not OCR_FILE.exists():
            raise FileNotFoundError(
                "PMMY OCR text not found. Run "
                "python -m app.ocr_all_pages first."
            )

        print("\nReading OCR text from PMMY FAQ...")

        pmmy_text = OCR_FILE.read_text(encoding="utf-8")

        if len(pmmy_text) < 1000:
            raise ValueError(
                "PMMY OCR text is too short. Check OCR output."
            )

        records = extract_mudra_records(pmmy_text)

        print("Extracted MUDRA records from source text.")

        print("\nReading Stand-Up India FAQ...")

        standup_text = extract_pdf("standup_faq.pdf")

        print("Reading Stand-Up India announcement...")

        standup_update = extract_html("standup_update.html")

        if not standup_update.strip():
            raise ValueError(
                "Stand-Up India update contains no readable text."
            )

        combined_standup_text = (
            "SOURCE: " + STANDUP_SOURCE
            + "\n\n"
            + standup_text
            + "\n\nLATEST STAND-UP INDIA UPDATE\n"
            + standup_update
        )

        STANDUP_OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        STANDUP_OUTPUT.write_text(
            combined_standup_text,
            encoding="utf-8"
        )

        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with OUTPUT_FILE.open("w", encoding="utf-8") as file:
            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False
            )

        save_manifest()

        print("\n========== INGESTION REPORT ==========")
        print("Total MUDRA records:", len(records))

        for record in records:
            print(
                record["loan_category"],
                "->",
                record["amount_range"]
            )

        print("\nRepayment extracted from PMMY FAQ.")
        print("Eligibility extracted from PMMY FAQ.")
        print("Manifest saved:", MANIFEST_FILE)
        print("MUDRA JSON:", OUTPUT_FILE)
        print("Stand-Up FAQ:", STANDUP_OUTPUT)
        print("\nData ingestion completed successfully!")

    except (
        FileNotFoundError,
        ValueError,
        OSError
    ) as error:

        print("\nIngestion error:", error)


if __name__ == "__main__":
    ingest_data()
