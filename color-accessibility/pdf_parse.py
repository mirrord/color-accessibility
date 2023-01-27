import fitz
from pathlib import Path
from PIL import Image

def get_images(fname:Path):
    with fitz.open(fname) as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Identity, dpi=None,
                          colorspace=fitz.csRGB, clip=None, alpha=True, annots=True)
            yield Image.frombytes("RGB", [pix.width, pix.height], pix.samples)