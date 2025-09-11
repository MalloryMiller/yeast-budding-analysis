
from utils import *
from numpy import abs, mean, array, inf
from PIL import ImageDraw
import os


class Analyzer:
    def __init__(self, img, ym: YeastManager):
        self.ym = ym 
        self.img = img

        self.width = img.size[0]
        self.length = img.size[1]

        self.x = 0
        self.y = 0


    


    def label_img(self, img):
        draw = ImageDraw.Draw(img)
        
        for s in self.ym.regular:
            draw.text((s.anchor[0], s.anchor[1]), str(s.id), (255,255,255), anchor='mm')
        for b in self.ym.budded:
            for s in b.yeast:
                draw.text((s.anchor[0], s.anchor[1]), str(s.id), (255,255,255), anchor='mm')
        for b in self.ym.cluster:
            for s in b.yeast:
                draw.text((s.anchor[0], s.anchor[1]), str(s.id), (255,255,255), anchor='mm')

        
        

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
        for i, x in enumerate(to_change):
            data[x[0], x[1]] = color
        return
    


    def add_region(self, region, max_ys, min_xs, min_ys, max_xs, type_override = False):
        '''
        Adds the area to the record as the appropriate kind of yeast based on
        the nature of its content
        '''
        return self.ym.add_region(region, max_ys, min_xs, min_ys, max_xs, type_override)
    

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
            







    def Q_around(self, x, y, Q, validate_color, corners=False, left=True):
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
            self.Q_pixel(x+1, y-1, Q, validate_color)

        return Q


    def cascade_fill(self, x, y, current, top, bottom, right, left, surrounded_by = 5):
        to_add = []
        neighbor_vector = []
        width = right - left + 2
        height = bottom - top + 2

        xs = []
        ys = []

            
        
        if not width-2 or not height-2:
            return to_add

        for y in range(height):
            cur = []
            for x in range(width):
                cur.append(0)
            neighbor_vector.append(cur)

        for c in current:
            neighbor_vector[c[1] - top][c[0] - left] = ORIGINAL


        for dr in SIDES_FOR_SURROUNDED:
            update_matrix_in_direction(neighbor_vector, dr)


        for y in range(height):
            for x in range(width):

                if is_surrounded(neighbor_vector[y][x], surrounded_by) \
                    and neighbor_vector[y][x] != ORIGINAL \
                    and x + left > 0 and y + right > 0 \
                    and x + left < self.img.size[0] and y + top < self.img.size[0]:
                    
                    to_add.append([x + left, y + top])
                    xs.append(x+left)
                    ys.append(y+top)
                    #neighbor_vector[y][x] = 1
                #else:
                    #neighbor_vector[y][x] = 0

        return to_add

    
    def get_one_area(self, x, y, current, desired_color = lambda color: color == colorKey['New'], find_divot = True, max_dist = MAX_BUDDING_DISTANCE):
        Q = [[x, y]]

        top = y
        bottom = y
        left = x
        right = x


        validity = True
    
        while Q:
            cur = Q.pop(0)
            color = self.img.getpixel((cur[0], cur[1]))
            if not desired_color(color):
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

            current.append(cur)
            if cur[0] < max_dist or cur[1] < max_dist or \
                cur[0] > self.width-max_dist or cur[1] == self.length-max_dist:
                validity = False # too close to edge of image, not valid cell

            Q = self.Q_around(cur[0], cur[1], Q, desired_color, True)
    

        
        fill_section = self.cascade_fill(x, y, current, top, bottom, right, left)
        current.extend(fill_section)


        # corners get messy if a line moves diagonally, double run through catches those cases.
        fill_section2 = self.cascade_fill(x, y, current, top, bottom, right, left) 
        current.extend(fill_section2)
        fill_section.extend(fill_section2)

        self.flood_fill(current, colorKey[Background])
        
        if find_divot:
            divots = self.cascade_fill(x, y, current, top, bottom, right, left, DIVOT_THRESHHOLD)
            self.flood_fill(divots, colorKey['Divot'])


        for new in fill_section:
                Q = self.Q_around(cur[0], cur[1], Q, desired_color, True)

    

        return right, left, bottom, top, validity, divots




    def get_region(self, x, y, desired_color = lambda color: color == colorKey['New'], max_dist = MAX_BUDDING_DISTANCE):
        '''
        identifies the potential cell region at coordinate
        (x, y) and returns the pixels it includes its height
        and its width.
        '''

        areas   = []
        current = []
        max_xs = []
        min_xs = []
        max_ys = []
        min_ys = []
    
        maxx, minx, maxy, miny, validity, divots = self.get_one_area(x, y, current, max_dist=max_dist, desired_color=desired_color)
        
        max_xs.append(maxx)
        min_xs.append(minx)
        max_ys.append(maxy)
        min_ys.append(miny)
        areas.append(current)

        D = divots.copy()

        areas, max_ys, min_xs, min_ys, max_xs, validity = self.divvy_by_divot(areas, max_ys, min_xs, min_ys, max_xs, validity, divots)
        

        Q = WeightedSetQueue()
        for x in current:
            Q.append(list(x), 0)
        
        
        self.flood_fill(D, colorKey['Divot'])
        
        while Q:

            cur = Q.pop(0) # format of [x, y, dist]
            if cur[2] > max_dist:
                continue

            
            if desired_color(self.img.getpixel((cur[0], cur[1]))):

                new_areas, maxy, minx, miny, maxx, new_validity, new_divots = self.get_region(cur[0], cur[1], desired_color=desired_color)
                areas.extend(new_areas)

                max_ys.extend(maxy)
                min_xs.extend(minx)
                min_ys.extend(miny)
                max_xs.extend(maxx)
                validity = new_validity and validity

            else:
                new_points = self.Q_around(cur[0], cur[1], [],
                                           lambda color: color != colorKey['Added'] and color != colorKey['Old'])
                for x in new_points:
                    Q.append(list(x), cur[2] + 1)


        return areas, max_ys, min_xs, min_ys, max_xs, validity, divots
    

    def find_nearest_pair(self, divots):
        '''
        Takes a list of two different areas and returns the points in each area
        where they are closest to one another.
        '''

        min_dist = inf

        
            
    
        for pos in divots[0]:
            for pos2 in divots[1]:
                dist = ((pos[0] - pos2[0])**2 + (pos[1] - pos2[1])**2)**0.5
                if dist < min_dist:
                    min_dist = dist
                    point1 = pos
                    point2 = pos2

        return point1, point2
    

    def filter_small_areas(self, areas, area_sizes, ratio = .5):
        if len(areas) <= 2:
            return areas, area_sizes
        avg = mean(area_sizes)
        sizes = []
        a = []
        for A in (range(len(areas))):
            if area_sizes[A] > avg * ratio:
                sizes.append(area_sizes[A])
                a.append(areas[A])
        return a, sizes





    def divvy_by_divot(self, to_change, max_ys, min_xs, min_ys, max_xs, validity, divots):
        '''
        Returns the to_change area list but divided by divot if a valid output can be found, 
        along with its validity
        '''

        if not validity or len(divots) == 0:
            return to_change, max_ys, min_xs, min_ys, max_xs, validity
        
        
        divot_areas = []

        
        while divots:
            cur = divots.pop()
            new_divot, ____, ___, _, __, _____, _____ = self.get_region(cur[0], cur[1], desired_color=lambda color: colorKey['Divot'] == color, max_dist=MAX_DIVOT_DISTANCE)
            for d in new_divot:
                if d:
                    divot_areas.extend(new_divot)
            to_add = []

            for x in new_divot:
                to_add.extend(list(x))
            

            if not to_add:
                continue

        
        divot_sizes = []

        for d in divot_areas:
            divot_sizes.append(len(d))

        # TODO: maybe filter out divots that are small relative to other divots?
        

        divot_areas, divot_sizes = self.filter_small_areas(divot_areas, divot_sizes)



        if len(divot_areas) == 1 or (len(divot_areas) == 2 and not divot_areas[1] or not divot_areas[0]):
            return to_change, max_ys, min_xs, min_ys, max_xs, validity # could be okay, test to see if bad
        

        if len(divot_areas) != 2 or len(to_change) != 1:
            return to_change, max_ys, min_xs, min_ys, max_xs, False # too many divots to be a divide or too many cells to be sorted into parent and bud
        #print(divot_areas)
        point1, point2 = self.find_nearest_pair(divot_areas)
        



        if point1[0] == point2[0]: #perfectly vertical
            validation = lambda x, y : x > point1[0]
        
        else:
            validation = lambda x, y : y > (((point2[1] - point1[1]) / (point2[0] - point1[0])) * (x - point1[0])) + point1[1]
            
        new_set = [[], []]
        max_xs_new = [min_xs[0], min_xs[0]]
        min_xs_new = [max_xs[0], max_xs[0]]
        max_ys_new = [min_ys[0], min_ys[0]]
        min_ys_new = [max_ys[0], max_ys[0]]

        for pos in to_change[0]:
            if validation(pos[0], pos[1]):
                new_set[0].append(pos)
                self.update_record(min_xs_new, max_xs_new, 0, pos[0])
                self.update_record(min_ys_new, max_ys_new, 0, pos[1])

            else:
                new_set[1].append(pos)
                self.update_record(min_xs_new, max_xs_new, 1, pos[0])
                self.update_record(min_ys_new, max_ys_new, 1, pos[1])


        return new_set, max_ys_new, min_xs_new, min_ys_new, max_xs_new, validity

    def update_record(self, min, max, pos, value):
        if min[pos] > value:
            min[pos] = value
        if max[pos] < value:
            max[pos] = value

    def analyze(self):
        '''
        identifies, colors, and records all potential cell regions 
        (areas of self.img with color colorKey['New'])
        '''

        while self.next_item():
            
            to_change, max_ys, min_xs, min_ys, max_xs, validity, divots = self.get_region(self.x, self.y) 
            
            validity = validity and not (len(to_change) == 1 and len(to_change[0]) < IGNORE_ISOLATED_SIZE)

            should_ignore = []

            '''
            Ignore all bad areas caught in this item
            '''
            
            if not validity: # all of areas bad, too close to edge
                for x in range(len(to_change)):
                    should_ignore.append(x)
            else:
                for area in range(len(to_change)): # if any of the areas are insufficiently round, see as background

                    if insufficiently_round(len(to_change[area]), max_xs[area] - min_xs[area], max_ys[area] - min_ys[area]) or \
                        len(to_change[area]) < IGNORE_ALL_SIZE:
                        should_ignore.append(area)
                        break

            should_ignore.reverse()
            for area in should_ignore:
                    self.flood_fill(to_change.pop(area), colorKey[IgnoredYeast]) #colors for removal

            '''
            Parse through remaining areas
            '''

            if to_change: # if not all of them were ignored add what's left
                for area in to_change:
                    self.flood_fill(area, colorKey['New']) 

                region_type = self.add_region(to_change, max_ys, min_xs, min_ys, max_xs)
                
                for i, area in enumerate(to_change):
                    color = region_type
                    if region_type == BuddedYeast and i == 1:
                        color = 'BuddedYeast2'
                    self.flood_fill(area, colorKey[color]) 

                    



class ManualAnalyzer(Analyzer):
    def __init__(self, img, preset, ym: YeastManager):
        super().analyze(img, ym)

        self.preset = preset

    def nearest_color(self, color):
        return color

    def analyze(self):
        pass


