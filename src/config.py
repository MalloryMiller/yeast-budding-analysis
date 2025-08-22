

from yeast import *

colorKey = { # values can be changed but MUST be distinct
    Background: (255, 255, 255),
    'Ignored':(255,255,255),

    Yeast: (255, 200, 200),
    BuddedYeast: (200, 255, 200),
    'BuddedYeast2': (200, 255, 242),
    IgnoredYeast: (200, 200, 255),

    'New': (0, 0, 0),
    'Added': (100, 100, 100),
    'Old': (200, 200, 200),

    'Divot': (200, 200, 100)
}


UNIT_PER_PIXEL = 20/78 # reference scale of 20 micrometers that is 78 pixels long
UNITS = "μm"

THRESHOLD = 5 # in grayscale space 0-255


THRESHOLD2 = 254 # in grayscale space 0-255
THRESHOLD1 = 100 # in grayscale space 0-255

IGNORE_ISOLATED_SIZE = 30 # in px, doesn't count as a cell if by itself
IGNORE_ALL_SIZE = 20

MAX_BUDDING_DISTANCE = 6 # in px
MAX_ROUNDNESS = 1 # in % of expected ovular area based on height and width
ROUNDNESS_FORGIVENESS = .5 #MAX_ROUNDNESS will be +/- this


MAX_DIVOT_DISTANCE = 4
DIVOT_MIN_SIZE = 3

SMOOTHING = 0 # reduces accuracy, probably don't use
CONTRAST_CUTOFF = 2
CONTRAST_IGNORE = 4

