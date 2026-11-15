
import json
from pathlib import Path
from dataclasses import asdict
from html.parser import HTMLParser

from pypdf import PdfReader
from app.models import Record


# File paths
RAW_DIR = Path("data/raw")
OUTPUT_FILE = Path("data/records.json")
STANDUP_OUTPUT = Path("data/standup_faq.txt")


# Official source references
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


# HTML text extractor
class PageTextParser(HTMLParser):

    def __init__(self):
        super().__init__()
        self.parts = []

    def handle_data(self, data):
        cleaned = data.strip()

        if cleaned:
            self.parts.append(cleaned)


# Extract text from PDF
def extract_pdf(filename):

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found. Run app.fetch first."
        )

    reader = PdfReader(str(path))

    text = "\n".join(
        page.extract_text() or ""
        for page in reader.pages
    )

    if not text.strip():
        raise ValueError(
            f"No readable text found in {filename}"
        )

    return text


# Extract text from HTML
def extract_html(filename):

    path = RAW_DIR / filename

    if not path.exists():
        raise FileNotFoundError(
            f"{filename} not found. Run app.fetch first."
        )

    parser = PageTextParser()

    parser.feed(
        path.read_text(encoding="utf-8")
    )

    return "\n".join(parser.parts)


# Create MUDRA records
def create_mudra_records():

    records = []

    categories = {

        "Shishu": {
            "amount": "Up to Rs. 50,000",

            "eligibility": [
                "Small grocery shop owners",
                "Small food business owners",
                "Street vendors",
                "Small artisans",
                "New micro business entrepreneurs"
            ]
        },

        "Kishor": {
            "amount": "Above Rs. 50,000 to Rs. 5 lakh",

            "eligibility": [
                "Growing small business owners",
                "Dairy business owners",
                "Small manufacturing units",
                "Service sector entrepreneurs",
                "Existing micro enterprises"
            ]
        },

        "Tarun": {
            "amount": "Above Rs. 5 lakh to Rs. 10 lakh",

            "eligibility": [
                "Established small business owners",
                "Small manufacturing entrepreneurs",
                "Trading business owners",
                "Service business entrepreneurs",
                "Growing micro enterprises"
            ]
        },

        "Tarun Plus": {
            "amount": "Above Rs. 10 lakh to Rs. 20 lakh",

            "eligibility": [
                "Entrepreneurs who successfully repaid a previous Tarun loan",
                "Eligible manufacturing entrepreneurs with a repaid Tarun loan",
                "Eligible trading entrepreneurs with a repaid Tarun loan",
                "Eligible service entrepreneurs with a repaid Tarun loan",
                "Eligible micro enterprises meeting Tarun Plus conditions"
            ]
        }
    }

    for category, details in categories.items():

        for business in details["eligibility"]:

            record = Record(

                loan_category=category,

                amount_range=details["amount"],

                who_can_apply=business,

                margin_or_contribution=(
                    "As per the lending institution's "
                    "applicable policy and assessment."
                ),

                repayment=(
                    "Repayment period and terms are decided "
                    "by the lending institution."
                ),

                source_doc=PMMY_SOURCE
            )

            records.append(asdict(record))

    return records


# Main ingestion function
def ingest_data():

    try:

        print("\n========== MUDRAMITRA DATA INGESTION ==========")

        # Step 1: Read PMMY FAQ
        print("\nReading official PMMY FAQ...")

        pmmy_text = extract_pdf("pmmy_faq.pdf")

        # Step 2: Read Stand-Up India FAQ
        print("Reading Stand-Up India FAQ...")

        standup_text = extract_pdf("standup_faq.pdf")

        # Step 3: Read latest Stand-Up India update
        print("Reading latest Stand-Up India announcement...")

        standup_update = extract_html(
            "standup_update.html"
        )

        if not standup_update.strip():
            raise ValueError(
                "Stand-Up India update contains no readable text."
            )

        # Step 4: Validate PMMY categories
        required_terms = [
            "Shishu",
            "Kishor",
            "Tarun",
            "Tarun Plus"
        ]

        for term in required_terms:

            if term.lower() not in pmmy_text.lower():

                raise ValueError(
                    f"PMMY FAQ does not contain {term}"
                )

        print("All four MUDRA categories verified.")

        # Step 5: Save separate Stand-Up India FAQ text
        STANDUP_OUTPUT.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        combined_standup_text = (
            "SOURCE: " + STANDUP_SOURCE
            + "\n\n"
            + standup_text
            + "\n\nLATEST STAND-UP INDIA UPDATE\n"
            + standup_update
        )

        STANDUP_OUTPUT.write_text(
            combined_standup_text,
            encoding="utf-8"
        )

        # Step 6: Create MUDRA records
        records = create_mudra_records()

        # Step 7: Save JSON
        OUTPUT_FILE.parent.mkdir(
            parents=True,
            exist_ok=True
        )

        with OUTPUT_FILE.open(
            "w",
            encoding="utf-8"
        ) as file:

            json.dump(
                records,
                file,
                indent=4,
                ensure_ascii=False
            )

        # Step 8: Ingestion report
        print("\n========== INGESTION REPORT ==========")

        print("Total MUDRA records:", len(records))

        categories = [
            "Shishu",
            "Kishor",
            "Tarun",
            "Tarun Plus"
        ]

        for category in categories:

            count = sum(
                1
                for record in records
                if record["loan_category"] == category
            )

            print(f"{category}: {count}")

        print("\nPMMY FAQ extracted successfully.")

        print("Stand-Up India FAQ extracted successfully.")

        print("Latest Stand-Up India update saved.")

        print("\nMUDRA JSON:", OUTPUT_FILE)

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
