


class Region:
    def __init__(self, x, y):
        self.anchor = [x, y]
    def __str__(self):
        return str(self.anchor).replace(",", "")



class Background(Region):
    def __init__(self, x, y):
        super().__init__(x, y)





class Yeast(Region):
    def __init__(self, x, y, area):
        super().__init__(x, y)
        self.area = area
        self.yeast_manager = None
    
    def get_area(self):
        return self.area
    
    def __str__(self):
        per_unit = ""
        if self.yeast_manager != None:
            per_unit =  "," + str(self.area * (self.yeast_manager.unit_per_pixel ** 2))
        return super().__str__() + "," + str(self.area) + per_unit



class BuddedYeast(Yeast):
    def __init__(self, x, y, yeast1 : Yeast, yeast2 : Yeast):
        super().__init__(x, y, yeast1.get_area() + yeast2.get_area())
        self.yeast = [yeast1, yeast2]

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




class ClusteredYeast(Yeast):
    def __init__(self, x, y, yeasts):
        self.yeast = yeasts
        super().__init__(x, y, sum(y.get_area() for y in self.yeast))


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


    def add_regular(self, yeast : Yeast):
        yeast.yeast_manager = self
        self.regular.append(yeast)
        self.regular_count += 1

    def add_budded(self, budded : BuddedYeast):
        budded.yeast_manager = self
        self.budded.append(budded)
        self.budded_count += 1

    def add_cluster(self, cluster : ClusteredYeast):
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
        header = "Anchor Coordinate,Area (px),Area (" + self.units + "²)"
        self.generate_output("regular_" + self.name, header, self.regular)


    
    def get_budded_output(self):
        '''
        Generates csv files for budded yeast areas
        '''
        header = "Total Area (px),Total Area (" + self.units + "²),Yeast 1 Anchor Coordinate,Yeast 1 Area (px),Yeast 1 Area (" + self.units + "²),Yeast 2 Anchor Coordinate,Yeast 2 Area (px),Yeast 2 Area (" + self.units + "²)"
        self.generate_output("budded_" + self.name, header, self.budded)


    def results(self):
        '''
        Generates csv files for both budded and regular yeast areas
        '''
        self.get_regular_output()
        self.get_budded_output()

