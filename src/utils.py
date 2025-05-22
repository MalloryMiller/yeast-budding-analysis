

from config import *
from math import pi


TOP = 1
BOTTOM = 2
LEFT = 4
RIGHT = 8

TOPLEFT = 16
TOPRIGHT = 32
BOTTOMLEFT = 64
BOTTOMRIGHT = 128

SIDES_FOR_SURROUNDED = [ # must be in descending order.
        #BOTTOMRIGHT, 
        #BOTTOMLEFT, 
        #TOPRIGHT, 
        #TOPLEFT, 
        RIGHT, 
        LEFT, 
        BOTTOM, 
        TOP,

]
ORIGINAL = sum(SIDES_FOR_SURROUNDED) + 256



def is_surrounded(score):
    
    sides = 0

    for s in SIDES_FOR_SURROUNDED:
        if (score - s) >= 0:
            sides += 1
            score -= s

    return sides > len(SIDES_FOR_SURROUNDED) // 2
     

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




class WeightedSetQueue():

    def __init__(self):

        '''
        list of coordinates (values are [x, y]), but without repeated values.
        Weights may repeat, but values themselves may not.
        weights are remembered first come first serve if a value
        is repeated.

        Weights are returned as a third entry in the array when values are popped.
        '''
        self.Q = []
        self.values = set([])

    def __bool__(self):
        return len(self.Q).__bool__()

    def pop(self, index=0, remove=False):
        '''
        returns an array of [x, y, weight]

        if remove=True, the value that was popped can be appended again and restored.
        Otherwise that value will not be reentered into the Q ever.
        '''
        if remove:
            value = [self.Q[index][0], self.Q[index][1]]
            self.values.remove(value)
        return self.Q.pop(index)
    
    def append(self, value, weight):
        '''
        value must be in the form [x, y]
        weight may be anything
        '''
        if str(value) in self.values:
            return
        self.values.add(str(value))
        value.extend([weight])
        self.Q.append(value)






