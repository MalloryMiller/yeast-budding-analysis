from PIL import Image, ImageOps, ImageFilter, ImageChops

from utils import * 
from fill import Analyzer



class main():
    def __init__(self):
        return 
    
    def analyze(self, filename):
        ym = YeastManager()

        img = Image.open(filename)
        img = ImageOps.grayscale(img) 
        img = img.filter(ImageFilter.GaussianBlur(SMOOTHING))
        img = img.convert("RGB")
        img = ImageOps.autocontrast(img, cutoff = CONTRAST_CUTOFF, ignore = CONTRAST_IGNORE)
        filter_out_grays(img)
        img.save("cleaned_" + filename)

        #registry = Image.new('RGB', img.size, color=colorKey['New'])

        a = Analyzer(img, ym)
        a.analyze()

        original = Image.open(filename)
        img = ImageChops.multiply(original, img)


        img.save("results_of_" + filename,"PNG")
    



m = main()

m.analyze("test.jpg")
m.analyze("full_test.jpg")
