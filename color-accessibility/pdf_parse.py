import fitz
from pathlib import Path

def get_images(fname:Path):
    with fitz.open(fname) as doc:
        for page in doc:
            yield page.get_pixmap(matrix=fitz.Identity, dpi=None,
                          colorspace=fitz.csRGB, clip=None, alpha=True, annots=True)