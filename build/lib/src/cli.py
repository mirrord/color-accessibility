import argparse
from pathlib import Path

def cli():
    parser = argparse.ArgumentParser(description="Test an image or pdf for WGAC20 AA compliance")
    parser.add_argument("--image", type=Path, help="test an image")
    parser.add_argument("--pdf", type=Path, help="parse a pdf and analyze each page")

    args = parser.parse_args()
    if args.image:
        from PIL import Image
        from distinguish import AA_test
        with Image.open(args.image) as img:
            if AA_test(img):
                print(f"image {str(args.image.absolute())} passed!")
            else:
                print(f"image {str(args.image.absolute())} failed!")

    if args.pdf:
        import pdf_parse
        index = 1
        for img in pdf_parse.get_images(args.pdf):
            if AA_test(img):
                print(f"page {index} passed!")
            else:
                print(f"page {index} failed!")
            index+=1

    print("done.")