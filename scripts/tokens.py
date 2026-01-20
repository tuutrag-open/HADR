# // Using a PDF -> Image conversion for full, accurate
# // context etraction from PDFs
import os
import glob
import tiktoken
import kagglehub

from openai import OpenAI
from pathlib import Path

PDF_TO_IMAGE_DATA = os.path.abspath(
    os.path.join(os.pardir, "pdf_to_image_data")
)
MODEL = 'gpt-4.1-min'
SCHEME = 'o200k_base'
MULTIPLIER = 1.62


def get_pdf_image_dataset_paths() -> list[str]:
    if not os.path.isdir(PDF_TO_IMAGE_DATA):
        path = kagglehub.dataset_download("pablobedolla/pdf-to-image-data")
        print("KAGGLE DATASET DOWNLOADED:", path)

    images = [str(p) for p in Path(PDF_TO_IMAGE_DATA).rglob("*.png")]    
    


if __name__ == "__main__":
    # get paths here

