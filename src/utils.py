

from yeast import *
from math import pi


colorKey = {
    Background: (255, 255, 255),
    Yeast: (255, 200, 200),
    BuddedYeast: (0, 255, 0),
    ClusteredYeast: (255, 255, 255),

    'New': (0, 0, 0),
    'Added': (100, 100, 100),
}


THRESHOLD = 20
IGNORE_SIZE = 30
MAX_BUDDING_DISTANCE = 3
REQUIRED_ROUNDNESS = .5


SMOOTHING = 0 # reduces accuracy, probably don't use
CONTRAST_CUTOFF = 2
CONTRAST_IGNORE = 1



def insufficiently_round(area, width, height):
    expected_area = (pi * (width / 2) * (height / 2))
    
    if expected_area > area * (1+REQUIRED_ROUNDNESS) or \
        expected_area < area * REQUIRED_ROUNDNESS:

        return True
    
    return False


def filter_out_grays(img):
    data = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img.getpixel((x, y))[0] > THRESHOLD:
                data[x, y] = (255, 255, 255)
            else:
                data[x, y] = (0,0,0)



