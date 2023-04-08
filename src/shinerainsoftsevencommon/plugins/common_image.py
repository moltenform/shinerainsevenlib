
def getImageType(inPath):
    from PIL import Image
    im = Image.open(inPath)
    format = im.format
    if format == 'MPO':
        format = 'JPG'

    return format

