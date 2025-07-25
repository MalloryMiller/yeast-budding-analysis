
from utils import *
from numpy import abs, mean
from PIL import ImageDraw



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
            draw.text((s.anchor[0], s.anchor[1]), str(s.id), (255,255,255))
        for b in self.ym.budded:
            for s in b.yeast:
                draw.text((s.anchor[0], s.anchor[1]), str(s.id), (255,255,255))

        
        

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
    


    def add_region(self, region):
        '''
        Adds the area to the record as the appropriate kind of yeast based on
        the nature of its content
        '''


        return self.ym.add_region(region, self.x, self.y)
    

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

                if is_surrounded(neighbor_vector[y][x], surrounded_by) and neighbor_vector[y][x] != ORIGINAL and \
                    x + left > 0 and y + right > 0 and \
                        x + left < self.img.size[0] and y + right < self.img.size[0]:
                    to_add.append([x + left, y + top])
        
        return to_add

    
    def get_one_area(self, x, y, current, desired_color = lambda color: color == colorKey['New'], find_divot = True, max_dist = MAX_BUDDING_DISTANCE):
        Q = [[x, y]]
        starting_color = self.img.getpixel((x, y))[0]

        top = y
        bottom = y
        left = x
        right = x

        include = True
        while Q:

            while Q:
                cur = Q.pop(0)
                color = self.img.getpixel((cur[0], cur[1]))
                if not desired_color(color):
                    continue

                data = self.img.load()
                data[cur[0], cur[1]] = colorKey[Background]

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
                    if cur[0] < max_dist or cur[1] < max_dist or \
                        cur[0] > self.width-max_dist or cur[1] == self.length-max_dist:
                        include = False # too close to edge of image, not valid cell

                    Q = self.Q_around(cur[0], cur[1], Q, desired_color, True)

            
            fill_section = self.cascade_fill(x, y, current, top, bottom, right, left)
            current.extend(fill_section)
            # corners get messy if a line moves diagonally, double run through catches those cases.
            fill_section2 = self.cascade_fill(x, y, current, top, bottom, right, left) 
            current.extend(fill_section2)
            fill_section.extend(fill_section2)

            if find_divot:
                divots = self.cascade_fill(x, y, current, top, bottom, right, left, 4)

            self.flood_fill(current, colorKey[Background])
            for new in fill_section:
                    Q = self.Q_around(cur[0], cur[1], Q, desired_color, True)

            if find_divot:
                self.flood_fill(divots, colorKey['Divot'])

        

        return bottom - top, right - left, include, divots




    def get_region(self, x, y, desired_color = lambda color: color == colorKey['New'], max_dist = MAX_BUDDING_DISTANCE):
        '''
        identifies the potential cell region at coordinate
        (x, y) and returns the pixels it includes, its height,
        and its width.
        '''

        areas = []
        current = []
        widths = []
        lengths = []
    
        width, length, validity, divots = self.get_one_area(x, y, current, max_dist=max_dist, desired_color=desired_color)
        widths.append(width)
        lengths.append(length)
        areas.append(current)

        Q = WeightedSetQueue()
        for x in current:
            Q.append(list(x), 0)

        while Q:

            cur = Q.pop(0)
            if cur[2] > max_dist:
                continue
            
            if desired_color(self.img.getpixel((cur[0], cur[1]))):
                new_areas, new_widths, new_lengths, new_validity, new_divots = self.get_region(cur[0], cur[1], desired_color=desired_color)
                new_areas, new_widths, new_lengths, new_validity = self.divvy_by_divot(new_areas, new_widths, new_lengths, new_validity, new_divots)
                areas.extend(new_areas)
                widths.extend(new_widths)
                lengths.extend(new_lengths)
                validity = new_validity and validity

            else:
                new_points = self.Q_around(cur[0], cur[1], [], 
                                           lambda color: color != colorKey['Added'] and color != colorKey['Old'])
                for x in new_points:
                    Q.append(list(x), cur[2] + 1)


        return areas, widths, lengths, validity, divots
    


    def divvy_by_divot(self, to_change, heights, widths, validity, divots):
        '''
        Returns the to_change area list but divided by divot if a valid output can be found, 
        along with its validity
        '''

        if not validity or len(divots) == 0:
            return to_change, heights, widths, validity
        

        divot_xs = []
        divot_ys = []
        
        while divots:
            cur = divots.pop()
            new_divot, ____, ___, _, __ = self.get_region(cur[0], cur[1], desired_color=lambda color: colorKey['Divot'] == color, max_dist=MAX_DIVOT_DISTANCE)

            to_add = []

            for x in new_divot:
                to_add.extend(list(x))

            if not to_add:
                continue

            divot_xs.append(to_add[0][0])
            divot_ys.append(to_add[0][1])



        if len(divot_xs) == 1:
            return to_change, heights, widths, validity # could be okay, test to see if bad

        if len(divot_xs) != 2 or len(to_change) != 1:
            return to_change, heights, widths, False # too many divots to be a divide or too many cells to be sorted into parent and bud
        
        
        point1 = [int(mean(divot_xs[0])), int(mean(divot_ys[0]))]
        point2 = [int(mean(divot_xs[1])), int(mean(divot_ys[1]))]


        if point1[0] == point2[0]: #perfectly vertical
            validation = lambda x, y : x > point1[0]
        
        else:
            validation = lambda x, y : y > (((point2[1] - point1[1]) / (point2[0] - point1[0])) * (x - point1[0])) + point1[1]
            
        new_set = [[], []]
        print(widths, heights)
        xmaxs = [point1[0] - widths[0], point1[0] - widths[0]]
        xmins = [point1[0] + widths[0], point1[0] + widths[0]]
        ymaxs = [point1[1] - heights[0], point1[1] - heights[0]]
        ymins = [point1[1] + heights[0], point1[1] + heights[0]]

        for x in to_change[0]:
            if validation(x[0], x[1]):
                new_set[0].append(x)

                if x[0] > xmaxs[0]:
                    xmaxs[0] = x[0]
                if x[0] < xmins[0]:
                    xmins[0] = x[0]

                if x[1] > ymaxs[0]:
                    ymaxs[0] = x[1]
                if x[1] < xmins[0]:
                    ymins[0] = x[1]
            else:
                new_set[1].append(x)

                if x[0] > xmaxs[1]:
                    xmaxs[1] = x[0]
                if x[0] < xmins[1]:
                    xmins[1] = x[0]

                if x[1] > ymaxs[1]:
                    ymaxs[1] = x[1]
                if x[1] < xmins[1]:
                    ymins[1] = x[1]

        print(len(new_set[0]), len(new_set[1]))
        new_set = list(filter(lambda set : len(set) > 0, new_set))

        heights = [ymaxs[0] - ymins[0], ymaxs[1] - ymins[1]]
        widths = [xmaxs[0] - xmins[0], xmaxs[1] - xmins[1]]

        return new_set, heights, widths, validity



    def analyze(self):
        '''
        identifies, colors, and records all potential cell regions 
        (areas of self.img with color colorKey['New'])
        '''

        while self.next_item():
            
            to_change, heights, widths, validity, divots = self.get_region(self.x, self.y) 
            to_change, heights, widths, validity = self.divvy_by_divot(to_change, heights, widths, validity, divots)
            self.flood_fill(divots, colorKey['Divot'])
            
            should_ignore = not (len(to_change) == 1 and len(to_change[0]) < IGNORE_ISOLATED_SIZE)

            should_ignore = []

            '''
            Ignore all bad areas caught in this item
            '''
            
            if not validity: # all of areas bad, too close to edge
                for x in range(len(to_change)):
                    should_ignore.append(x)
            '''
            else:
                for area in range(len(to_change)): # if any of the areas are insufficiently round, see as background
                    if insufficiently_round(len(to_change[area]), heights[area], widths[area]) or \
                        len(to_change[area]) < IGNORE_ALL_SIZE:
                        should_ignore.append(area)
                        break
            '''

            should_ignore.reverse()
            for area in should_ignore:
                    self.flood_fill(to_change.pop(area), colorKey[IgnoredYeast]) #colors and removes areas for removal

            '''
            Parse through remaining areas
            '''

            if to_change: # if not all of them were ignored add what's left
                for area in to_change:
                    self.flood_fill(area, colorKey['New']) 

                region_type = self.add_region(to_change)

                for i, area in enumerate(to_change):
                    color = region_type
                    if region_type == BuddedYeast and i == 1:
                        color = 'BuddedYeast2'
                    self.flood_fill(area, colorKey[color]) 

                    


