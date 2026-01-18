import os
import glob
import math
import asyncio 



from PIL import Image
from pathlib import Path
from typing import List
from pdf2image import convert_from_path
from concurrent.futures import ProcessPoolExecutor

# Directories
DATA_SUPPLEMENTAL = os.path.abspath(os.path.join(os.pardir, "data/supplemental/"))
DATA_STORAGE = os.path.abspath(os.path.join(os.pardir, "batches/"))

# Constants
multiplier = 1.62 # < gpt-4.1-mini

# pdf2image options
options = {
    "output_folder": DATA_STORAGE,
    "dpi": 300,
    "fmt": "png",
    "thread_count": 1,
    "paths_only": True,
} 


def get_pdf_paths() -> list[str]:
    return [str(p) for p in Path(DATA_SUPPLEMENTAL).rglob("*.pdf")]


def process_pdf(path: str) -> list[str]:
    print(f"Processing file: {os.path.basename(path)}")
    return convert_from_path(pdf_path=path, **options)


def pdfs_to_images(paths: list[str], workers: int = 4) -> list[str]:
    all_images: list[str] = []

    with ProcessPoolExecutor(max_workers=workers) as executor:
        for image_paths in executor.map(process_pdf, paths):
            all_images.extend(image_paths)
    
    return all_images


def image_processing(path: str) -> None:
    with Image.open(path) as im:
        width, height = im.size
        raw_patches = math.ceil(width/32) * math.ceil(height/32)

        if raw_patches <= 1536:
            return
        
        # Scale factor
        r = math.sqrt((32**2 * 1536) / (width * height))

        # Adjustment to keep integer patch grid
        sw = (width * r) / 32
        sh = (height * r) / 32
        r *= min(math.floor(sw) / sw, math.floor(sh) / sh)
        
        new_w = int(width * r)
        new_h = int(height * r)

        print(f"    Rescaling: {width}x{height} -> {new_w}x{new_h}")
        im.resize((new_w, new_h)).save(path)

if __name__ == "__main__":
    # paths = get_pdf_paths()
    # images = pdfs_to_images(paths) 
    
    image_paths = [str(p) for p in Path(DATA_STORAGE).glob("*")]
    
         
    with ProcessPoolExecutor(max_workers=4) as executor:
        for _ in executor.map(image_processing, image_paths):
            pass
