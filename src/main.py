from PIL import Image, ImageOps, ImageFilter, ImageChops
import cv2 
import os


from utils import * 
from fill import Analyzer
from key import Key



class main():
    def __init__(self):
        return 
    


    def read_flags(self):
        pass



    
    def analyze(self, filename):
        path = '/'.join(filename.split('/')[:-1]) + "/"
        title = filename.split('/')[-1].split(".")[0]
        os.makedirs(path + title, exist_ok=True)
        
        ym = YeastManager(title, path, UNIT_PER_PIXEL, UNITS)

        

        img = Image.open(filename)

        #img = ImageOps.grayscale(img) 
        
        #img = img.filter(ImageFilter.GaussianBlur(SMOOTHING))
        #img = img.convert("RGB")
        #img = ImageOps.autocontrast(img, cutoff = CONTRAST_CUTOFF, ignore = CONTRAST_IGNORE)
        #filter_out_grays(img)


        raw = cv2.imread(filename)
        canny = cv2.Canny(raw, THRESHOLD1,THRESHOLD2)
        color_coverted = cv2.cvtColor(canny, cv2.COLOR_BGR2RGB)
        
        img = Image.fromarray(color_coverted)
        img = ImageOps.invert(img)
        img.save(path + title + "/cleaned_" + title + ".png", "PNG")

        a = Analyzer(img, ym)
        a.analyze()
        k=Key(img,DISPLAY_COLORKEY)

        original = Image.open(filename)
        img = ImageChops.multiply(original, img)

        
        img = k.append_key(img)


        img.save(path + title + "/results_of_" + title + ".png", "PNG")
        ym.results()

        a.label_img(img)
        img.save(path + title + "/labeled_" + title + ".png", "PNG")
        
    



m = main()

'''m.analyze("tests/test.jpg")
print("partial done")
m.analyze("tests/full_test.jpg")
print("full done")'''

m.analyze("tests/cleaner_test.jpg")
print("cleaner done")