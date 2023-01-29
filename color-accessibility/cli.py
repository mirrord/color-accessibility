import argparse
from pathlib import Path
from tqdm import tqdm
from . import distinguish

def cli():
    parser = argparse.ArgumentParser(description="Test an image or pdf for WGAC20 AA compliance")
    parser.add_argument("--image", type=Path, help="test an image")
    parser.add_argument("--pdf", type=Path, help="parse a pdf and analyze each page")

    args = parser.parse_args()
    if args.image:
        from PIL import Image
        with Image.open(args.image) as img:
            if distinguish.AA_test(img)[0]:
                print(f"image {str(args.image.absolute())} passed!")
            else:
                print(f"image {str(args.image.absolute())} failed!")

    if args.pdf:
        from . import pdf_parse
        imgs = []
        page_num = 1
        for page_img in tqdm(pdf_parse.get_pages_as_images(args.pdf)):
            #print(f"************** Image {page_num} **************")
            #page_img.show()
            # for clip in distinguish.multi_crop_text(page_img):
            #     test_pass, cratio, c1, c2 = distinguish.AA_test(clip)
            #     imgs.append(clip)
            #     stats.append((cratio, c1, c2))
            imgs.append(distinguish.additive_analysis(page_img))
            page_num+=1
            #print("******************************************")
            #if page_num > 5: break

        pdf_parse.create_pdf_simple(imgs)

    print("done.")