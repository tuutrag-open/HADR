import os
import json
import kagglehub

from pathlib import Path

def get_data():
    def os_path(file) -> str:
        return os.path.abspath(os.path.join(os.pardir, file))

    _PDF_DATA = os_path("data/pdf_to_image_data")
    _REQ_DATA = os_path("data/requirement/requirements.json")
    _TES_DATA = os_path("data/test-cases/tests.json")

    # DATA
    PDF, REQ, TEST = None, None, None
    
    # PDF KAGGLE DATA
    if not os.path.isdir(_PDF_DATA):
        try:
            os.environ["KAGGLEHUB_CACHE"] = _PDF_DATA
            _KAGGLE_PATH = "pablobedolla/pdf-to-image-data/versions/1"
            path = kagglehub.dataset_download(_KAGGLE_PATH)
            print(f"Dataset succesfully downloaded to {path}")
            images = [str(p) for p in Path(path).rglob("*.png")]

            PDF = images
        except Exception as e:
            raise e

    # REQUIREMENT DATA
    with open(_REQ_DATA) as f:
        data = json.load(f)
        REQ = [obj['requirement'] for obj in data]

    # TEST DATA
    with open(_TES_DATA) as f:
        TEST = json.load(f)

    return PDF, REQ, TEST


if __name__ == "__main__":
    pdfs, reqs, tests = get_data()
    print(reqs)
