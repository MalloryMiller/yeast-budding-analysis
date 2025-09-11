

from config import *
from math import pi
from numpy import abs
from colorsys import rgb_to_hsv
from numpy import inf, abs, mean

TOP = 1
BOTTOM = 2
LEFT = 4
RIGHT = 8

TOPLEFT = 16
TOPRIGHT = 32
BOTTOMLEFT = 64
BOTTOMRIGHT = 128


SIDES_FOR_SURROUNDED = [ # must be in descending order.
        BOTTOMRIGHT, 
        BOTTOMLEFT, 
        TOPRIGHT, 
        TOPLEFT, 
        RIGHT, 
        LEFT, 
        BOTTOM, 
        TOP,

]

ORIGINAL = sum(SIDES_FOR_SURROUNDED) + 256


DIVOT_THRESHHOLD = 4


POSN_ADJUSTMENT = {
        BOTTOMRIGHT : [-1, -1], 
        BOTTOMLEFT : [1, -1], 
        TOPRIGHT : [-1, 1], 
        TOPLEFT : [1, 1], 
        LEFT : [1, 0], 
        RIGHT : [-1, 0], 
        BOTTOM : [0, -1], 
        TOP : [0, 1], 
}

DISPLAY_COLORKEY = {
    colorKey[Background]: 'Background',
    colorKey[Yeast] : 'Single Yeast',
    colorKey[BuddedYeast]: 'Parent Budded Yeast',
    colorKey['BuddedYeast2']: 'Child Budded Yeast',
    colorKey[IgnoredYeast]: 'Disregarded Shape'
}


FINAL_COLOR_LABELS = [
    Background,
    Yeast,
    'BuddedYeast2',
    IgnoredYeast
]


hue_colorKey = {}

for c in list([Yeast, BuddedYeast, 'BuddedYeast2', IgnoredYeast, 'Divot']):
    hue_colorKey[rgb_to_hsv(colorKey[c][0]/255, 
                                 colorKey[c][1]/255, 
                                 colorKey[c][2]/255)[0]] = c
 

print(hue_colorKey)




def hue_dist(hue1, hue2):

    smaller = min([hue1, hue2])
    bigger = max([hue1, hue2])

    return min([abs(hue1-hue2), abs(smaller + 1 - bigger)])



def nearest_color(color):
    hsv = rgb_to_hsv(color[0]/255, color[1]/255, color[2]/255)
    h = hsv[0]
    s = hsv[1]

    if s < .1:
        return Background
    
    dist = inf
    cur = None

    for hs in hue_colorKey.keys():
        d = hue_dist(h, hs)
        if d < dist:
            dist = d
            cur = hs

    return hue_colorKey[cur]




def ppi_to_micronpp(ppi):
    print(float(1 / (ppi * 25400)))
    return float(1 / (ppi * 25400))



def get_adj(posn, dir):
    print(posn, POSN_ADJUSTMENT[dir][0])
    return [
        posn[0] + POSN_ADJUSTMENT[dir][0], 
        posn[1] + POSN_ADJUSTMENT[dir][1]
        ]


def update_matrix_in_direction(matrix, direction):
        ys = list(range(len(matrix)))
        xs = list(range(len(matrix[0])))
        y_max = ys[-1]
        x_max = xs[-1]
        

        if POSN_ADJUSTMENT[direction][0] < 0:
            xs.reverse()
            xs.pop(0)
        elif POSN_ADJUSTMENT[direction][0] != 0:
            xs.pop()

        if POSN_ADJUSTMENT[direction][1] < 0:
            ys.reverse()
            ys.pop(0)
        elif POSN_ADJUSTMENT[direction][1] != 0:
            ys.pop()
            
        for y in ys:
            for x in xs:
                x_other = x - POSN_ADJUSTMENT[direction][0]
                y_other = y - POSN_ADJUSTMENT[direction][1]
                if x_other < 0 or x_other > x_max or y_other < 0 or y_other > y_max:
                    continue
                
                if matrix[y_other][x_other] & direction and \
                    not matrix[y][x] & direction:
                    matrix[y][x] += direction

                    
def surrounded_sides(score):
    
    sides = 0

    for s in SIDES_FOR_SURROUNDED:
        if (score - s) >= 0:
            sides += 1
            score -= s

    return sides


def is_surrounded(score, needed_sides = 5):
    return surrounded_sides(score) > needed_sides #len(SIDES_FOR_SURROUNDED) / 1.5 # MORE than half of the evaluated sides were surrounded
     


def insufficiently_round(area, width, height):
    '''
    Returns True if the area is not big enough or too big 
    to be considered round based on the REQUIRED_ROUNDNESS.
    Returns False otherwise
    '''

    return False
    

    expected_area = (pi * (abs(width) / 2) * (abs(height) / 2)) #pi * r * r

    if(area / expected_area > MAX_ROUNDNESS or \
        area / expected_area < 1/(MAX_ROUNDNESS)):

        return True
    

    return False


def filter_out_grays(img, thresh = THRESHOLD):
    '''
    Eliminates all gray values such that grayscale values over the threshold
    become only the color colorKey[Background]
    '''
    data = img.load()

    for x in range(img.size[0]):
        for y in range(img.size[1]):
            if mean(img.getpixel((x, y))) > thresh:
                data[x, y] = colorKey[Background]



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






