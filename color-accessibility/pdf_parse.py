import fitz
from pathlib import Path
from PIL import Image

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

def get_text(fname:Path):
    with fitz.open(fname) as doc:
        for i in range(len(doc)):
            deets = getText2(doc[i])
            print(deets.keys())
            handle_page_highlights(doc[i])

def getText2(page: fitz.Page, zoom_f=3) -> dict:
    """
    Function similar to fitz.Page.getText("dict"). But the returned dict
    also contains a key "bg_color" with color tuple as value for each block in "blocks".
    """
    # Retrieves the content of the page
    all_words = page.get_text("dict")

    # Transform page into PIL.Image
    #mat = fitz.Matrix(zoom_f, zoom_f)
    pixmap = page.get_pixmap()
    img = Image.open(io.BytesIO(pixmap.tobytes()))
    img_border = fitz.Rect(0, 0, img.width, img.height)
    for block in all_words['blocks']:
        # Retrieve only text block (type 0)
        if block['type'] == 0:
            rect = fitz.Rect(*tuple(xy * zoom_f for xy in block['bbox']))
            if img_border.contains(rect):
                color = img.getpixel((rect.x0, rect.y0))
                block['bg_color'] = tuple(c/255 for c in color)
    return all_words

def handle_page_highlights(page):
    wordlist = page.get_text("words")  # list of words on page
    wordlist.sort(key=lambda w: (w[3], w[0]))  # ascending y, then x

    highlights = []
    annot = page.first_annot
    while annot:
        if annot.type[0] == 8:
            #highlights.append(_parse_highlight(annot, wordlist))
            print(annot.colors)
        annot = annot.next
    return highlights


def norm_color(c):
    return (c[0]/255, c[1]/255, c[2]/255)

def create_pdf(images:list, stats:list):
    RED = (1, 0.3, 0.1)
    YELLOW = (1, 0.8, 0)
    GREEN = (0.05, 0.6, 0.73)
    doc = fitz.Document(filetype="pdf")
    for image, (cratio, c1, c2) in zip(images, stats):
        page = doc.new_page()
        #insert status light
        status_color, status_label = RED, "Failed!"
        if cratio > 4.5:
            status_color, status_label = GREEN, "Passed!"
        elif cratio > 3.0:
            status_color, status_label = YELLOW, "Ensure font size is 18pt or larger"
        elif cratio == 0:
            status_color, status_label = YELLOW, "No text found"
        page.draw_circle(fitz.Point(50, 50), 15, color=status_color, fill=status_color)
        page.insert_text(fitz.Point(70, 55), status_label)
        # insert image
        buf = io.BytesIO()
        image.save(buf, "JPEG")
        i = fitz.Pixmap(buf)
        page.insert_image(fitz.Rect(50,80,400,300), pixmap=i, keep_proportion=True)
        #insert details
        if cratio > 0:
            page.insert_text(fitz.Point(100, 480), f"Contrast ratio: {cratio:2.1f}")
            page.insert_text(fitz.Point(100, 500), "Hues found:")
            c1_norm = norm_color(c1)
            c2_norm = norm_color(c2)
            page.draw_circle(fitz.Point(115, 520), 15, fill=c1_norm)
            page.insert_text(fitz.Point(135, 520), f"RGB: {c1}, hex: {c1[0]:X}{c1[1]:X}{c1[2]:X}")
            page.draw_circle(fitz.Point(115, 570), 15, fill=c2_norm)
            page.insert_text(fitz.Point(135, 570), f"RGB: {c2}, hex: {c2[0]:X}{c2[1]:X}{c2[2]:X}")
    doc.save("report.pdf")

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