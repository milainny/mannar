import pytesseract

def labelToText(img):
    text = pytesseract.image_to_string(img)
    return text
