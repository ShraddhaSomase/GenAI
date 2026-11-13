
import requests
import zipfile
from pathlib import Path

RAW_DIR = Path("data/raw")
RAW_DIR.mkdir(parents=True, exist_ok=True)

URL = "https://huggingface.co/datasets/AnguloM/loan_data/resolve/main/loan.zip"
ZIP_PATH = RAW_DIR / "loan.zip"

def download_dataset():
    try:
        print("Downloading historical loan dataset...")

        response = requests.get(URL, timeout=60)
        response.raise_for_status()

        ZIP_PATH.write_bytes(response.content)

        print("Download successful!")

        with zipfile.ZipFile(ZIP_PATH, "r") as zip_file:
            csv_files = [
                name for name in zip_file.namelist()
                if name.lower().endswith(".csv")
            ]

            if not csv_files:
                raise ValueError("No CSV file found inside ZIP.")

            selected_file = csv_files[0]

            with zip_file.open(selected_file) as source:
                output_path = RAW_DIR / "loan_data.csv"
                output_path.write_bytes(source.read())

        print("CSV extracted:", output_path)
        print("Source:", URL)

    except requests.exceptions.Timeout:
        print("Error: Download timed out.")

    except requests.exceptions.RequestException as error:
        print("Download error:", error)

    except (zipfile.BadZipFile, ValueError, OSError) as error:
        print("File error:", error)


if __name__ == "__main__":
    download_dataset()
