
from PIL import Image
import numpy as np
from colorthief import ColorThief
import pytesseract as tesseract

class IMColorThief(ColorThief):
    def __init__(self, img:Image):
        self.image = img

def relative_luminance(hue:np.array):
    if any(hue < 0) or any(hue > 255):
        raise ValueError(f"invalid hue value! {hue}")
    norm_hue = hue/255
    sRGB_hue = ((norm_hue+0.055)/1.055)**2.4
    thresh_mask = sRGB_hue <= 0.03928
    rollover = norm_hue/12.92
    sRGB_hue = (~thresh_mask*sRGB_hue) + (thresh_mask*rollover)
    return np.sum(np.array([0.2126, 0.7152, 0.0722]) * sRGB_hue)+0.05

def contrast_ratio(img: Image) -> float:
    thief = IMColorThief(img)
    palette = thief.get_palette(color_count=2, quality=1)
    print(f"palette: {palette}")
    color1, color2 = np.array(palette[0]), np.array(palette[1])
    rlum1 = relative_luminance(color1)
    rlum2 = relative_luminance(color2)
    return rlum1/rlum2 if rlum1>rlum2 else rlum2/rlum1

def get_text_height(img: Image) -> int:
    img = img.convert('L')
    tres = tesseract.image_to_data(img, output_type=tesseract.Output.DICT)
    if len(tres['level']) == 0:
        print("no text found! Please adjust tesseract settings")
        return 0
    return int(np.array(tres['height'][1:]).mean())

def AA_test(img: Image) -> bool:
    big_text_threshold = 4.5
    reg_text_threshold = 3
    size = get_text_height(img)
    print(f"text height (best guess): {size}")
    cratio = contrast_ratio(img)
    print(f"contrast ratio: {cratio:2.1f}")
    if 3 < cratio < 4.5:
        print("Double check your font size - font sizes less than 18 are not compliant.")
    return cratio > reg_text_threshold if size < 18 else cratio > big_text_threshold 



