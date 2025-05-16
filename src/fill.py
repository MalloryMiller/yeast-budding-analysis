
from utils import *
from numpy import abs
import heapq



class Analyzer:
    def __init__(self, registry, img, ym):
        self.registry = registry
        self.ym = ym
        self.img = img

        self.width = img.size[0]
        self.length = img.size[1]

        self.x = 0
        self.y = 0
        


    def next_item(self):
        '''
        Moves self.x and self.y to the next black (unvisited) coordinate in self.registry
        '''

        cur  = [1] 

        while sum(cur) != 0: # will run once since cur = [1]
            self.x += 1

            if self.x == self.width:
                if self.y == self.length-1:
                    return False
                self.x = 0
                self.y += 1

            cur = self.registry.getpixel((self.x, self.y))
        
        return True
    

    def flood_fill(self, to_change, color):
        data = self.registry.load()
        for x in to_change:
            data[x[0], x[1]] = color
        return
    


    def add_area(self, type, content):
        if type == Background:
            self.ym.add_background(Background(self.x, self.y))
        if type == Yeast:
            self.ym.add_regular(Yeast(self.x, self.y, len(content[0])))
        return
    

    def Q_pixel(self, x, y, Q):
        r_type = False

        if x >= 0 and x < self.width and y >= 0 and y < self.length:
            availability_left = self.registry.getpixel((x, y))
            print(x, y, availability_left, colorKey['Q'], colorKey['New'])
            if availability_left == colorKey['Q']:
                r_type = True
            elif availability_left == colorKey['New']:
                print("QUEED")
                data = self.registry.load()
                data[x, y] = colorKey['Q']
                Q.append((x, y))

        return r_type



    def get_region(self, x, y):
        regions = []
        current = []
        starting_color = self.img.getpixel((x, y))[0]
        r_type = Yeast
        Q = []
        Q.append([x, y])

        while Q:
            cur = Q.pop(0)
            color = self.img.getpixel((cur[0], cur[1]))[0]

            if abs(color - starting_color) <= TOLERANCE:
                current.append(cur)
                data = self.registry.load()
                data[cur[0], cur[1]] = colorKey['Added']

                bg_found = False

                bg_found |= self.Q_pixel(cur[0]-1, cur[1], Q)
                bg_found |= self.Q_pixel(cur[0], cur[1]-1, Q)
                bg_found |= self.Q_pixel(cur[0]+1, cur[1], Q)
                bg_found |= self.Q_pixel(cur[0], cur[1]+1, Q)

                if bg_found:
                    r_type = Background


            else:
                data = self.registry.load()
                data[cur[0], cur[1]] = colorKey['New']


            
        
        regions.append(current)

        if r_type != Background and len(regions) > 2:
            r_type = ClusteredYeast

        if r_type != Background and len(regions) == 2:
            r_type = BuddedYeast

        return r_type, regions



    def analyze(self):
        '''
        does a flood search starting at self.x and self.y and continuing to the end of the file
        '''

        while True:

            region_type, to_change = \
                self.get_region(self.x, self.y) 
            

            self.add_area(region_type, to_change)
            for region in to_change:
                self.flood_fill(region, colorKey[region_type]) 

            if (not self.next_item()):
                break #stop when there's no more

