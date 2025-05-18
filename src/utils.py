

from config import *
from math import pi



def insufficiently_round(area, width, height):
    '''
    Returns True if the area is not big enough or too big 
    to be considered round based on the REQUIRED_ROUNDNESS.
    Returns False otherwise
    '''

    expected_area = (pi * (width / 2) * (height / 2))

    if expected_area * REQUIRED_ROUNDNESS > area or \
        expected_area < area * REQUIRED_ROUNDNESS :

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



