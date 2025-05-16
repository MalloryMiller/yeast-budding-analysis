
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
        


    def next_item(self):
        '''
        Moves self.x and self.y to the next black (unvisited) coordinate in self.img
        '''

        cur  = [1] 

        while sum(cur) != 0: # will run once since cur = [1]
            self.x += 1

            if self.x == self.width:
                if self.y == self.length-1:
                    return False
                self.x = 0
                self.y += 1

            cur = self.img.getpixel((self.x, self.y))
        
        return True
    

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
            self.ym.add_regular(BuddedYeast(self.x, self.y, len(content[0])))
        if len(content) > 2:
            r_type = ClusteredYeast
            self.ym.add_regular(ClusteredYeast(self.x, self.y))
        return r_type
    

    def Q_pixel(self, x, y, Q, availability_matters = True):
        '''
        Queues a coordinate (x, y) in Q only if the spot is valid,
        also won't queue if the location is already visited (colorKey['New']) 
        or availability_matters is turned off
        '''

        if x >= 0 and x < self.width and y >= 0 and y < self.length:
            availability_left = self.img.getpixel((x, y))

            if availability_left == colorKey['New'] or not availability_matters:
                Q.append((x, y))
            

    def Q_around(self, x, y, Q, availability_matters = True):
        '''
        Queues the four pixles around the given coordinate (x, y) in Q for a 
        flood filling affect.
        '''
        self.Q_pixel(x-1, y, Q, availability_matters)
        self.Q_pixel(x, y-1, Q, availability_matters)
        self.Q_pixel(x+1, y, Q, availability_matters)
        self.Q_pixel(x, y+1, Q, availability_matters)
        return Q




    def get_region(self, x, y):
        '''
        identifies the potential cell region at coordinate
        (x, y) and returns the pixels it includes, its height,
        and its width.
        '''

        top = y
        bottom = y
        left = x
        right = x


        regions = []
        current = []
        starting_color = self.img.getpixel((x, y))[0]
        Q = [[x, y]]

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

                Q = self.Q_around(cur[0], cur[1], Q)

    
            
        regions.append(current)

        return regions, bottom - top, right - left



    def analyze(self):
        '''
        identifies, colors, and records
        all potential cell regions 
        (areas of the image with color colorKey['New'])
        '''

        while self.next_item():

            to_change, height, width = self.get_region(self.x, self.y) 
            


            for region in to_change:
                if (len(to_change) == 1 and \
                    len(region) < IGNORE_SIZE) or \
                    insufficiently_round(len(region), height, width):
                    self.flood_fill(region, colorKey[Background]) 

                else:
                    region_type = self.add_area(to_change)
                    self.flood_fill(region, colorKey[region_type]) 


