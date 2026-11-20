
import time
from pathlib import Path

import requests

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

SOURCES = {
    "pmmy_faq.pdf": (
        "https://static.pib.gov.in/WriteReadData/"
        "specificdocs/documents/2025/sep/"
        "doc2025927648901.pdf"
    ),
    "standup_faq.pdf": (
        "https://static.pib.gov.in/WriteReadData/"
        "specificdocs/documents/2022/apr/"
        "doc20224535701.pdf"
    ),
    "standup_update.html": (
        "https://www.pib.gov.in/PressReleasePage.aspx?PRID=2334978"
    )
}


def download_file(filename, url):

    output_path = RAW_DIR / filename

    for attempt in range(1, 4):

        try:
            print(f"\nDownloading {filename}...")
            print(f"Attempt {attempt}/3")

            response = requests.get(
                url,
                timeout=(15, 60),
                headers={
                    "User-Agent": "Mozilla/5.0"
                }
            )

            response.raise_for_status()

            content = response.content

            if filename.endswith(".pdf"):
                if not content.startswith(b"%PDF"):
                    raise ValueError(
                        "Downloaded content is not a valid PDF."
                    )

            elif filename.endswith(".html"):
                if not content.strip():
                    raise ValueError("Downloaded HTML is empty.")

            output_path.write_bytes(content)

            print("Download successful!")
            print("Saved:", output_path)

            return True

        except (
            requests.exceptions.RequestException,
            OSError,
            ValueError
        ) as error:

            print("Download failed:", error)

            if attempt < 3:
                print("Retrying in 3 seconds...")
                time.sleep(3)

    print(f"Could not download {filename}.")
    return False


def download_dataset():

    print("\n========== OFFICIAL DATA DOWNLOAD ==========")

    successful = 0

    for filename, url in SOURCES.items():

        if download_file(filename, url):
            successful += 1

    print("\n========== DOWNLOAD REPORT ==========")
    print("Successful:", successful)
    print("Failed:", len(SOURCES) - successful)

    if successful == len(SOURCES):
        print("All official documents downloaded!")
    else:
        print("Some downloads failed. Check the errors above.")


if __name__ == "__main__":
    download_dataset()
