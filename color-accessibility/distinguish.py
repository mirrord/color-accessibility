
from PIL import Image, ImageEnhance, ImageDraw
import numpy as np
import pytesseract as tesseract

def check_distance(c1:tuple, c2:tuple):
    def sqdif(a,b):
        return ((a - b)**2)
    return np.sqrt(sqdif(c1[0], c2[0])+sqdif(c1[1], c2[1])+sqdif(c1[2], c2[2])) < 10

def count_colors(img: Image):
    count = {}
    pixels = img.load() # this is not a list, nor is it list()'able
    width, height = img.size

    for x in range(width):
        for y in range(height):
            cpixel = tuple(pixels[x, y])
            if cpixel not in count:
                count[cpixel] = 0
            count[cpixel]+=1

    sorted_colors = sorted(list(count.keys()), key=lambda t: count[t], reverse=True)
    while check_distance(sorted_colors[0], sorted_colors[1]):
        sorted_colors.pop(1)
    return sorted_colors[:2]

def relative_luminance(hue:np.array):
    if any(hue < 0) or any(hue > 255):
        raise ValueError(f"invalid hue value! {hue}")
    norm_hue = hue/255
    sRGB_hue = ((norm_hue+0.055)/1.055)**2.4
    thresh_mask = sRGB_hue <= 0.03928
    rollover = norm_hue/12.92
    sRGB_hue = (~thresh_mask*sRGB_hue) + (thresh_mask*rollover)
    return np.sum(np.array([0.2126, 0.7152, 0.0722]) * sRGB_hue)+0.05

def contrast_ratio(img: Image):
    try:
        palette = count_colors(img)
    except IndexError:
        return -1, None, None
    #print(f"palette: {palette}")
    color1, color2 = np.array(palette[0]), np.array(palette[1])
    rlum1 = relative_luminance(color1)
    rlum2 = relative_luminance(color2)
    rat = rlum1/rlum2 if rlum1>rlum2 else rlum2/rlum1
    return rat, tuple(color1), tuple(color2)

def additive_analysis(img: Image):
    '''return the same image, but with individual words underlined with either bluegreen (pass), amber (unsure), or red (fail).'''
    RED = (255, 85, 25)
    YELLOW = (255, 200, 0)
    GREEN = (12, 170, 180)
    LINE_WIDTH = 10
    grey_img = img.convert('L')
    thresh_img = grey_img.point(lambda p: p > 140 and 255)
    tres = tesseract.image_to_data(thresh_img, output_type=tesseract.Output.DICT)
    annotated_img = img.copy()
    artist = ImageDraw.Draw(annotated_img)
    #print(tres)
    for idx, text in enumerate(tres["text"]):
        if text.isalpha() and len(text) > 3:
            (left, top, width, height) = (tres['left'][idx], tres['top'][idx], tres['width'][idx], tres['height'][idx])
            cropped = img.crop((left, top, left+width, top+height))
            img_to_test = ImageEnhance.Sharpness(cropped).enhance(5)
            cratio, c1, c2 = contrast_ratio(img_to_test)
            if cratio > 4.5:
                #artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = GREEN)
                artist.line([left, top+height, left+width, top+height], width=LINE_WIDTH, fill = GREEN)
            elif 0 < cratio < 3:
                #artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = RED)
                artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = RED)
            else:
                #artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = YELLOW)
                artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = YELLOW)
    return annotated_img

def additive_block_analysis(img: Image):
    '''as additive_analysis, but draws boxes around groupings of words and attempts to analyze them as a group.'''
    RED = (255, 85, 25)
    YELLOW = (255, 200, 0)
    GREEN = (12, 170, 180)
    LINE_WIDTH = 6
    grey_img = img.convert('L')
    thresh_img = grey_img.point(lambda p: p > 140 and 255)
    tres = tesseract.image_to_data(thresh_img, output_type=tesseract.Output.DICT)
    annotated_img = img.copy()
    artist = ImageDraw.Draw(annotated_img)
    #print(tres)
    current_block = 0
    current_level = 0
    current_start = (0,0)
    current_dims = (0,0)
    for idx, text in enumerate(tres["text"]):
        if text.isalpha() and len(text) > 3:
            (left, top, width, height) = (tres['left'][idx], tres['top'][idx], tres['width'][idx], tres['height'][idx])
            if current_dims == (0,0):
                current_start = (left, top)
                current_dims = (width, height)
                current_block = tres["block_num"][idx]
                current_level = tres["level"][idx]
            if tres["block_num"][idx] == current_block and current_level == tres["level"][idx]:
                current_start = (min(current_start[0], left), (min(current_start[1], top)))
                current_dims = (
                    max(current_dims[0], left+width-current_start[0]),
                    max(current_dims[1], top+height-current_start[1])
                )
            else:
                (oldleft, oldtop, oldwidth, oldheight) = *current_start, *current_dims
                cropped = img.crop((oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight))
                #cropped.show()
                #img_to_test = ImageEnhance.Sharpness(cropped).enhance(5)
                cratio, c1, c2 = contrast_ratio(cropped)
                if cratio > 4.5:
                    artist.rectangle([oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, outline = GREEN)
                    #artist.line([oldleft, oldtop+oldheight, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, fill = GREEN)
                elif 0 < cratio < 3:
                    #artist.rectangle([oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, outline = RED)
                    artist.rectangle([oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, outline = RED)
                    artist.rectangle([oldleft, oldtop+oldheight+10, oldleft+10, oldtop+oldheight+20], fill=c1)
                    artist.rectangle([oldleft+15, oldtop+oldheight+10, oldleft+25, oldtop+oldheight+20], fill=c2)
                else:
                    #artist.rectangle([oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, outline = YELLOW)
                    artist.rectangle([oldleft, oldtop, oldleft+oldwidth, oldtop+oldheight], width=LINE_WIDTH, outline = YELLOW)
                
                current_start = (left, top)
                current_dims = (width, height)
                current_block = tres["block_num"][idx]
                current_level = tres["level"][idx]
                t = tres["text"][idx]
                print(f"next text: {t}")

    (left, top, width, height) = *current_start, *current_dims
    cropped = img.crop((left, top, left+width, top+height))
    #img_to_test = ImageEnhance.Sharpness(cropped).enhance(5)
    cratio, c1, c2 = contrast_ratio(cropped)
    if cratio > 4.5:
        artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = GREEN)
        #artist.line([left, top+height, left+width, top+height], width=LINE_WIDTH, fill = GREEN)
    elif 0 < cratio < 3:
        #artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = RED)
        artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = RED)
        artist.rectangle([left, top+height+10, left+40, top+height+50], width=5, outline="black", fill=c1)
        artist.rectangle([left+55, top+height+10, left+95, top+height+50], width=5, outline="black", fill=c2)
    else:
        #artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = YELLOW)
        artist.rectangle([left, top, left+width, top+height], width=LINE_WIDTH, outline = YELLOW)
    return annotated_img