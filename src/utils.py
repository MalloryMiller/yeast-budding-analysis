

from yeast import *
from math import pi


colorKey = { # values can be changed but MUST be distinct
    Background: (255, 255, 255),
    Yeast: (255, 200, 200),
    BuddedYeast: (0, 255, 0),
    ClusteredYeast: (255, 255, 255),

    'New': (0, 0, 0),
    'Added': (100, 100, 100),
}


UNIT_PER_PIXEL = 20/78 # reference scale of 20 micrometers that is 78 pixels long
UNITS = "μm"

THRESHOLD = 20 # in grayscale space 0-255
IGNORE_SIZE = 30 # in px
MAX_BUDDING_DISTANCE = 3 # in px
REQUIRED_ROUNDNESS = .5 # in % of expected ovular area based on height and width

SMOOTHING = 0 # reduces accuracy, probably don't use
CONTRAST_CUTOFF = 2
CONTRAST_IGNORE = 1



def insufficiently_round(area, width, height):
    '''
    Returns True if the area is not big enough or too big 
    to be considered round based on the REQUIRED_ROUNDNESS.
    Returns False otherwise
    '''

    expected_area = (pi * (width / 2) * (height / 2))

    if expected_area > area * (1+REQUIRED_ROUNDNESS) or \
        expected_area < area * REQUIRED_ROUNDNESS:

        return True
    
    return False


def filter_out_grays(img):
    '''
    Eliminates all gray values such that only the colors
    colorKey[Background] and colorKey['New'] are in the image
    '''
    data = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if img.getpixel((x, y))[0] > THRESHOLD:
                data[x, y] = colorKey[Background]
            else:
                data[x, y] = colorKey['New']



