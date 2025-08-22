
yeast_count = [0]

class Region:
    def __init__(self, max_ys, min_xs, min_ys, max_xs):
        self.anchor = [(max_xs + min_xs) / 2, (max_ys + min_ys) / 2]
    def __str__(self):
        return str(self.anchor).replace(",", "")



class Background(Region):
    def __init__(self, max_ys, min_xs, min_ys, max_xs):
        super().__init__(max_ys, min_xs, min_ys, max_xs)





class Yeast(Region):
    def __init__(self, max_ys, min_xs, min_ys, max_xs, area):
        super().__init__(max_ys, min_xs, min_ys, max_xs)
        self.area = area
        self.id = yeast_count[0]
        yeast_count[0] += 1
        self.yeast_manager = None
    
    def get_area(self):
        return self.area
    
    def __str__(self):
        per_unit = ""
        if self.yeast_manager != None:
            per_unit =  "," + str(self.area * (self.yeast_manager.unit_per_pixel ** 2))
        return str(self.id) + "," + super().__str__() + "," + str(self.area) + per_unit



class BuddedYeast(Yeast):
    def __init__(self, max_ys, min_xs, min_ys, max_xs, yeast1 : Yeast, yeast2 : Yeast):
        super().__init__(max_ys, min_xs, min_ys, max_xs, yeast1.get_area() + yeast2.get_area())
        self.yeast = [yeast1, yeast2]
        self.yeast.sort(key=lambda y : y.get_area(), reverse=True)
        

        if self.yeast[0].id  > self.yeast[1].id:
            second_id = self.yeast[0].id
            self.yeast[0].id = self.yeast[1].id
            self.yeast[1].id = second_id

    def get_all_areas(self):
        return [self.yeast[0].get_area(), self.yeast[1].get_area()]
    
    def __str__(self):
        other_yeasties = ""
        for y in self.yeast:
            other_yeasties += str(y) + ","

        per_unit = ""
        if self.yeast_manager != None:
            per_unit =  "," + str(self.area * (self.yeast_manager.unit_per_pixel ** 2))

        return str(self.area) + per_unit + "," + other_yeasties




class IgnoredYeast(Region):
    def __init__(self, max_ys, min_xs, min_ys, max_xs, yeasts):
        self.yeast = yeasts
        super().__init__(max_ys, min_xs, min_ys, max_xs)


    def get_all_areas(self):
        return (y.get_area() for y in self.yeast)
    




class YeastManager:
    def __init__(self, name, path, unit_per_pixel, units):
        self.name = name
        self.path = path
        self.unit_per_pixel = unit_per_pixel
        self.units = units


        self.regular = []
        self.regular_count = 0

        self.budded = []
        self.budded_count = 0

        self.cluster = []
        self.cluster_count = 0

        self.cluster = []
        self.cluster_count = 0


    

    def divide_areas(self, img, r, p1, p2):
        return []


    def add_region(self, regions, max_ys, min_xs, min_ys, max_xs, ignore = False):

        yeasts = []
        r_type = Yeast


        i = 0
        for r in regions:
            if len(r) == 0:
                break
                
            if ignore: # ignored? remember
                r_type = IgnoredYeast
                yeasts.append(Yeast(max_ys[i], min_xs[i], min_ys[i], max_xs[i], len(r)))

            else: # single cell :>
                yeasts.append(Yeast(max_ys[i], min_xs[i], min_ys[i], max_xs[i], len(r)))
                
            i += 1


        if len(yeasts) == 1 and r_type != IgnoredYeast:
            self.add_regular(yeasts[0])
            return Yeast
        
        elif len(yeasts) == 2 and r_type != IgnoredYeast:
            self.add_budded(BuddedYeast(max_ys[0], min_xs[0], min_ys[0], max_xs[0], yeasts[0], yeasts[1]))
            return BuddedYeast
        
        elif len(yeasts) > 2 or r_type == IgnoredYeast:
            self.add_cluster(IgnoredYeast(max_ys[0], min_xs[0], min_ys[0], max_xs[0], yeasts))

        return IgnoredYeast



    def add_regular(self, yeast : Yeast):
        yeast.yeast_manager = self
        self.regular.append(yeast)
        self.regular_count += 1

    def add_budded(self, budded : BuddedYeast):
        budded.yeast[0].yeast_manager = self
        budded.yeast[1].yeast_manager = self
        budded.yeast_manager = self
        self.budded.append(budded)
        self.budded_count += 1

    def add_cluster(self, cluster : IgnoredYeast):
        self.cluster.append(cluster)
        self.cluster_count += 1

    def add_background(self, bg : Background):
        pass


    def generate_output(self, fname, header, array):
        '''
        Generates a csv file inside the folder for this yeast manager
        with fname and the header given. Array should be a list of
        stringable objects which will be the rows, the strings should be
        already comma seperated
        '''
        file = open(self.path + self.name + "/" + fname + ".csv", "w")

        file.write(header + "\n")
        for b in array:
            file.write(str(b) + "\n")

        file.close()


    
    def get_regular_output(self):
        '''
        Generates csv files for regular yeast areas
        '''
        header = "Yeast ID,Anchor Coordinate,Area (px),Area (" + self.units + "²)"
        self.generate_output("regular_" + self.name, header, self.regular)


    
    def get_budded_output(self):
        '''
        Generates csv files for budded yeast areas
        '''
        header = "Total Area (px),Total Area (" + self.units + "²),Yeast 1 ID,Yeast 1 Anchor Coordinate,Yeast 1 Area (px),Yeast 1 Area (" + self.units + "²),Yeast 2 ID,Yeast 2 Anchor Coordinate,Yeast 2 Area (px),Yeast 2 Area (" + self.units + "²)"
        self.generate_output("budded_" + self.name, header, self.budded)


    def results(self):
        '''
        Generates csv files for both budded and regular yeast areas
        '''
        self.get_regular_output()
        self.get_budded_output()

