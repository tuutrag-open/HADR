import fitz  # PyMuPDF
import os
import math


DATA_DIR = os.path.abspath(os.path.join(
    os.getcwd(), "..", "data/supplemental"))

PATCH_DIR = os.path.join(DATA_DIR, "patches")
multiplier = 1.62  # < gpt-4.1-mini


def get_pdf(filename: str):
    path = os.path.join(DATA_DIR, filename)
    if not os.path.exists(path):
        print(f"[Error] Missing PDF: {path}")
        return None
    return fitz.open(path)


def apply_token_logic_resizing(image: fitz.Pixmap) -> tuple[int, int]:
    """
    Implements OpenAI image token logic:
    - 32x32 patches
    - Hard cap at 1536 patches
    - Number of patches is number of token
    """
    width, height = image.width, image.height
    raw_patches = math.ceil(width / 32) * math.ceil(height / 32)

    if raw_patches <= 1536:
        return (raw_patches, int(raw_patches * multiplier))

    # Scale factor
    r = math.sqrt((32**2 * 1536) / (width * height))

    # Adjustment to keep integer patch grid
    sw = (width * r) / 32
    sh = (height * r) / 32
    r *= min(math.floor(sw) / sw, math.floor(sh) / sh)

    new_w = int(width * r)
    new_h = int(height * r)
    new_patches = math.ceil(new_w/32) * math.ceil(new_h/32)
    tokens = int(new_patches * multiplier)

    print(f"  Rescale: {width}x{height} -> {new_w}x{new_h}")
    return (new_patches, tokens)


def ensure_patch_dir():
    os.makedirs(PATCH_DIR, exist_ok=True)


def extraction(filename: str, pages: list[int]):
    document = get_pdf(filename)
    ensure_patch_dir()

    if not document:
        return

    print(f"\nProcessing: {filename}")

    for i, p in enumerate(pages):
        if p >= len(document):
            print(f"  Skip page {p} (out of range)")
            continue

        page = document[p]
        pix = page.get_pixmap(dpi=300)
        patches, tokens = apply_token_logic_resizing(pix)
        print(f"  Page {p}: {patches} patches, Tokens {tokens}")

        name = filename.replace("/", "_").replace(".", "_")
        pix.save(os.path.join(PATCH_DIR, f"{name}.png"))


pdfs = [
    {"path": "doc_stand_ref.pdf", "pages": [40]},
    {"path": "PDS-SMP.pdf", "pages": [30]},
    {"path": "pds4_preparation_design.pdf", "pages": [14, 15]},
    {"path": "blue/CCSDS_123_0-B-2.pdf", "pages": [24, 37]},
    {"path": "blue/CCSDS_131_2-B-2.pdf", "pages": [33, 69]},
    {"path": "blue/CCSDS_734_1-B-1.pdf", "pages": [19]},
    {"path": "blue/CCSDS_876_0-B-1.pdf", "pages": [71]},
    {"path": "blue/CCSDS_922_3-B-1.pdf", "pages": [197]},
]

if __name__ == "__main__":
    print(f"Patch output: {PATCH_DIR}")
    for pdf in pdfs:
        extraction(pdf["path"], pdf["pages"])


