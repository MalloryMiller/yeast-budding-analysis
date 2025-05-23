from PIL import Image, ImageOps, ImageFilter, ImageChops
import os

from utils import * 
from fill import Analyzer



class main():
    def __init__(self):
        return 
    
    def analyze(self, filename):
        path = '/'.join(filename.split('/')[:-1]) + "/"
        title = filename.split('/')[-1].split(".")[0]
        os.makedirs(path + title, exist_ok=True)
        
        ym = YeastManager(title, path, UNIT_PER_PIXEL, UNITS)

        img = Image.open(filename)
        img = ImageOps.grayscale(img) 
        img = img.filter(ImageFilter.GaussianBlur(SMOOTHING))
        img = img.convert("RGB")
        img = ImageOps.autocontrast(img, cutoff = CONTRAST_CUTOFF, ignore = CONTRAST_IGNORE)
        filter_out_grays(img)
        img.save(path + title + "/cleaned_" + title + ".png")

        #registry = Image.new('RGB', img.size, color=colorKey['New'])

        a = Analyzer(img, ym)
        a.analyze()

        original = Image.open(filename)
        img = ImageChops.multiply(original, img)


        img.save(path + title + "/results_of_" + title + ".png","PNG")
        ym.results()
    



m = main()

m.analyze("tests/test.jpg")
print("first done")
m.analyze("tests/full_test.jpg")
print("second done")

m.analyze("tests/cleaner_test.jpg")
m.analyze("tests/hollow_test.jpg")