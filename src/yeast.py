


class Region:
    def __init__(self, x, y):
        self.anchor = [x, y]



class Background(Region):
    def __init__(self, x, y):
        super().__init__(x, y)





class Yeast(Region):
    def __init__(self, x, y, area):
        super().__init__(x, y)
        self.area = area
    
    def get_area(self):
        return self.area



class BuddedYeast(Yeast):
    def __init__(self, x, y, yeast1 : Yeast, yeast2 : Yeast):
        super().__init__(x, y, yeast1.get_area() + yeast2.get_area())
        self.yeast = [yeast1, yeast2]

    def get_all_areas(self):
        return [self.yeast[0].get_area(), self.yeast[1].get_area()]




class ClusteredYeast(Yeast):
    def __init__(self, x, y, yeasts):
        self.yeast = yeasts
        super().__init__(x, y, sum(y.get_area() for y in self.yeast))


    def get_all_areas(self):
        return (y.get_area() for y in self.yeast)




class YeastManager:
    def __init__(self):
        self.regular = []
        self.regular_count = 0

        self.budded = []
        self.budded_count = 0

        self.cluster = []
        self.cluster_count = 0

        self.cluster = []
        self.cluster_count = 0


    def add_regular(self, yeast : Yeast):
        self.regular.append(yeast)
        self.regular_count += 1

    def add_budded(self, budded : BuddedYeast):
        self.regular.append(budded)
        self.budded_count += 1

    def add_cluster(self, cluster : ClusteredYeast):
        self.cluster.append(cluster)
        self.cluster_count += 1

    def add_background(self, bg : Background):
        pass



