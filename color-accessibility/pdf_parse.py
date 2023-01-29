import io
import fitz
from pathlib import Path
from PIL import Image

def get_images(fname:Path):
    with fitz.open(fname) as doc:
        for i in range(len(doc)):
            for img in doc.get_page_images(i):
                # get the XREF of the image
                xref = img[0]
        
                # extract the image bytes
                pix = fitz.Pixmap(doc, xref)
                p = None
                try:
                    p = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
                except ValueError:
                    pass
                yield p

def norm_color(c):
    return (c[0]/255, c[1]/255, c[2]/255)

def create_pdf_simple(imgs):
    doc = fitz.Document(filetype="pdf")
    for img in imgs:
        buf = io.BytesIO()
        page = doc.new_page()
        img.save(buf, "JPEG")
        i = fitz.Pixmap(buf)
        i.shrink(3)
        page.insert_image(fitz.Rect(0,0,595,842), pixmap=i, keep_proportion=True)
    doc.save("report.pdf")

def get_pages_as_images(fname:Path):
    with fitz.open(fname) as doc:
        for page in doc:
            pix = page.get_pixmap(matrix=fitz.Identity, dpi=600,
                          colorspace=fitz.csRGB, clip=None, alpha=False, annots=True)
            yield Image.frombytes("RGB", [pix.width, pix.height], pix.samples)