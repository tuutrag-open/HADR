# // Using a PDF -> Image conversion for full, accurate
# // context etraction from PDFs
import os
import glob
import math
import json
import tiktoken
import kagglehub

from PIL import Image
from openai import OpenAI
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor


PDF_TO_IMAGE_DATA = os.path.abspath(
    os.path.join(os.pardir, "data/pdf_to_image_data")
    )
REQUIREMENT_DATA = os.path.abspath(
    os.path.join(os.pardir, "data/requirement/requirements.json") 
)
TEST_DATA = os.path.abspath(
    os.path.join(os.pardir, "data/test-cases/tests.json")
)   
KAGGLE_PATH = "pablobedolla/pdf-to-image-data/versions/1"
MODEL = 'gpt-4.1-min'
SCHEME = 'o200k_base'
MULTIPLIER = 1.62


def get_pdf_image_dataset_paths():
    if not os.path.isdir(PDF_TO_IMAGE_DATA):
        try:
            os.environ["KAGGLEHUB_CACHE"] = PDF_TO_IMAGE_DATA
            path = kagglehub.dataset_download(KAGGLE_PATH)

            print(f"Dataset succesfully downloaded to {path}")

            images = [str(p) for p in Path(path).rglob("*.png")]

            return images
        except Exception as e:
            raise e

    return [str(p) for p in Path(PDF_TO_IMAGE_DATA).rglob("*.png")]

def get_requirements():
    reqs = []
    with open(REQUIREMENT_DATA) as f:
        data = json.load(f)
        
        for obj in data:
            reqs.append(obj['requirement'])

    return reqs

def image_tok_cnt(path): 
    with Image.open(path) as im:
        w, h = im.size
        raw_patches = math.ceil(w/32) * math.ceil(h/32)

        if raw_patches <= 1536:
            return raw_patches * MULTIPLIER

        # Scale factor
        r = math.sqrt((32**2 * 1536) / (w*h))

        # Adjust to keep integer patch grid
        sw = (w*r)/32
        sh = (h*r)/32
        r *= min(math.floor(sw) / sw, math.floor(sh) / sh)

        new_w = int(w*r)
        new_h = int(h*r)
        new_patches = math.ceil(new_w/32) * math.ceil(new_h/32)

        return new_patches*MULTIPLIER


if __name__ == "__main__":
    # get paths here
    images = get_pdf_image_dataset_paths()
    requirements = get_requirements()
    
    # Encode
    enc = tiktoken.get_encoding(SCHEME)

    # Image token count
    img_tok = 0
    cnt = 0
    with ProcessPoolExecutor(max_workers=4) as executor:
        for res in executor.map(image_tok_cnt, images):
            img_tok += res
            cnt += 1
    
    # Requirement token count
    req_tok = [len(enc.encode(r)) for r in requirements]
    
    # Test case toke count
    with open(TEST_DATA) as f:
        test_tok = json.load(f)
        test_tok = [len(enc.encode(t)) for t in test_tok]
        test_tok = sum(test_tok)

    print(f"IMG TCNT: {int(img_tok)}")
    print(f"REQ TCNT: {sum(req_tok)}")
    print(f"TES TCNT: {test_tok}")

    print(f"{'='*10}")


    print(f"TOTAL: {format(int(img_tok + sum(req_tok) + test_tok), ",")}")

