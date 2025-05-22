
from utils import *
from numpy import abs
import heapq



class Analyzer:
    def __init__(self, img, ym: YeastManager):
        self.ym = ym 
        self.img = img

        self.width = img.size[0]
        self.length = img.size[1]

        self.x = 0
        self.y = 0
        

    def move_cursor(self, target_color, x_start, y_start, x_end, y_end, reset_lines = False):
        '''
        returns the coordinates of the next pixel that is the target_color in self.img

        When True, reset_lines will reset the x value to 0 insteaed of x_start when it reaches the end of a row.
        This is appropriate for when the function is intending to search the entire image rather than
        a square region. When set to False, it will only search that smaller region for the next pixel.
        '''

        x = x_start
        y = y_start

        cur  = None

        while cur != target_color: # will run once since cur = None
            x += 1

            if x == x_end:
                if y == y_end - 1: # end reached, False means no more items
                    return False, x, y
                
                if reset_lines:
                    x = 0
                else:
                    x = x_start

                y += 1
            cur = self.img.getpixel([x, y])
        
        return True, x, y # item found at [x, y]



    def next_item(self):
        '''
        Moves self.x and self.y to the next black (unvisited) coordinate in self.img
        '''

        status, self.x, self.y = self.move_cursor(colorKey['New'],
                                                  self.x, self.y,
                                                  self.width, self.length,
                                                  reset_lines=True)
        
        return status
    

    

    def flood_fill(self, to_change, color):
        '''
        Fills all of the pixels in the array to_change with 
        the given color
        '''

        data = self.img.load()
        for x in to_change:
            data[x[0], x[1]] = color
        return
    


    def add_area(self, content):
        '''
        Adds the area to the record as the appropriate kind of yeast based on
        the nature of its content
        '''
        r_type = Yeast
        if len(content) == 1:
            self.ym.add_regular(Yeast(self.x, self.y, len(content[0])))

        if len(content) == 2:
            r_type = BuddedYeast
            yeast1 = Yeast(self.x, self.y, len(content[0]))
            yeast2 = Yeast(content[1][0][0], content[1][0][1], len(content[1]))
            self.ym.add_budded(BuddedYeast(self.x, self.y, yeast1, yeast2))

        if len(content) > 2:
            r_type = ClusteredYeast
            yeasts = []
            for yeast in content:
                y = Yeast(yeast[0][0], yeast[0][1], len(yeast))
                yeasts.append(y)
            self.ym.add_cluster(ClusteredYeast(self.x, self.y, yeasts))

        return r_type
    

    def Q_pixel(self, x, y, Q, validate_color):
        '''
        Queues a coordinate (x, y) in Q only if the spot is valid 
        (exists within the size of the image and passes validate_color).

        validate_color must be a function which takes in a color and returns a boolean.
        Pixels with colors that return True from this function will be Queued in Q, False ones will be ignored.
        '''

        if x >= 0 and x < self.width and y >= 0 and y < self.length:
            color = self.img.getpixel((x, y))

            if validate_color(color):
                Q.append((x, y))
            

    def Q_around(self, x, y, Q, validate_color, corners=False):
        '''
        Queues the four pixles around the given coordinate (x, y) in Q for a 
        flood filling affect.
        '''
        self.Q_pixel(x, y-1, Q, validate_color)
        self.Q_pixel(x+1, y, Q, validate_color)
        self.Q_pixel(x, y+1, Q, validate_color)
        self.Q_pixel(x-1, y, Q, validate_color)

        if corners:
            self.Q_pixel(x-1, y-1, Q, validate_color)
            self.Q_pixel(x+1, y+1, Q, validate_color)
            self.Q_pixel(x-1, y+1, Q, validate_color)
            self.Q_pixel(x-1, y-1, Q, validate_color)

        return Q


    def cascade_fill(self, x, y, current, top, bottom, right, left):
        to_add = []
        start = [top, left]

        '''
        TODO

        ???
        '''

        return to_add

    
    def get_one_area(self, x, y, current):
        Q = [[x, y]]
        starting_color = self.img.getpixel((x, y))[0]

        top = y
        bottom = y
        left = x
        right = x

        while Q:
            cur = Q.pop(0)
            color = self.img.getpixel((cur[0], cur[1]))
            if sum(color) != 0:
                continue

            data = self.img.load()
            data[cur[0], cur[1]] = colorKey['Added']

            if cur[0] > right:
                right = cur[0]
            if cur[0] < left:
                left = cur[0]
            if cur[1] > bottom:
                bottom = cur[1]
            if cur[1] < top:
                top = cur[1]


            if abs(color[0] - starting_color) == 0:
                current.append(cur)

                Q = self.Q_around(cur[0], cur[1], Q, lambda color : color == colorKey['New'], True)

        current.extend(self.cascade_fill(x, y, current, top, bottom, right, left))
        return bottom - top, right - left




    def get_region(self, x, y):
        '''
        identifies the potential cell region at coordinate
        (x, y) and returns the pixels it includes, its height,
        and its width.
        '''

        areas = []
        current = []
        widths = []
        lengths = []
    
        width, length = self.get_one_area(x, y, current)
        widths.append(width)
        lengths.append(length)
        areas.append(current)

        Q = WeightedSetQueue()
        for x in current:
            Q.append(list(x), 0)

        while Q:
            cur = Q.pop(0)
            if cur[2] > MAX_BUDDING_DISTANCE:
                continue

            if self.img.getpixel((cur[0], cur[1])) == colorKey['New']:
                new_areas, new_widths, new_lengths = self.get_region(cur[0], cur[1])
                areas.extend(new_areas)
                widths.extend(new_widths)
                lengths.extend(new_lengths)

            else:
                new_points = self.Q_around(cur[0], cur[1], [], 
                                           lambda color: color == colorKey['Ignored'] or color == colorKey[Background] or color == colorKey['New'])
                for x in new_points:
                    Q.append(list(x), cur[2] + 1)


        return areas, widths, lengths



    def analyze(self):
        '''
        identifies, colors, and records
        all potential cell regions (areas of self.img with color colorKey['New'])
        '''

        while self.next_item():

            to_change, heights, widths = self.get_region(self.x, self.y) 
            should_ignore = not (len(to_change) == 1 and len(to_change[0]) < IGNORE_ISOLATED_SIZE)

            should_ignore = []
            
            for area in range(len(to_change)): # if any of the areas are insufficiently round, see as background
                if insufficiently_round(len(to_change[area]), heights[area], widths[area]) or \
                    len(to_change[area]) < IGNORE_ALL_SIZE:
                    should_ignore.append(area)
                    break

            should_ignore.reverse()
            for area in should_ignore:
                    self.flood_fill(to_change.pop(area), colorKey['Ignored']) 
                    



            if to_change:
                region_type = self.add_area(to_change)
                for area in to_change:
                    self.flood_fill(area, colorKey[region_type]) 


