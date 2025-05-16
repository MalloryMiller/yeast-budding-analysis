

from yeast import *


colorKey = {
    Background: (255, 255, 255),
    Yeast: (155, 0, 255),
    BuddedYeast: (0, 0, 255),
    ClusteredYeast: (255, 0, 0),

    'New': (0, 0, 0),
    'Added': (200, 200, 200),
    'Q': (100, 100, 100),
}


TOLERANCE  = 0
THRESHOLD = 70
IGNORE_SIZE = 5
MAX_BUDDING_DISTANCE = 3


SMOOTHING = 0 # reduces accuracy, probably don't use
CONTRAST_CUTOFF = 2
CONTRAST_IGNORE = 1



def sufficiently_round(area, width, height):
    return True


def filter_out_grays(img):
    data = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img.getpixel((x, y))[0] > THRESHOLD:
                data[x, y] = (255, 255, 255)
            else:
                data[x, y] = (0,0,0)



