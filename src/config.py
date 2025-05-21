

from yeast import *

colorKey = { # values can be changed but MUST be distinct
    Background: (255, 255, 255),
    Yeast: (255, 200, 200),
    BuddedYeast: (200, 255, 200),
    ClusteredYeast: (200, 200, 255),

    'New': (0, 0, 0),
    'Added': (100, 100, 100),
    'Old': (200, 200, 200),
}


UNIT_PER_PIXEL = 20/78 # reference scale of 20 micrometers that is 78 pixels long
UNITS = "μm"

THRESHOLD = 20 # in grayscale space 0-255
IGNORE_SIZE = 30 # in px
MAX_BUDDING_DISTANCE = 4 # in px
REQUIRED_ROUNDNESS = .50 # in % of expected ovular area based on height and width


SMOOTHING = 0 # reduces accuracy, probably don't use
CONTRAST_CUTOFF = 2
CONTRAST_IGNORE = 1

