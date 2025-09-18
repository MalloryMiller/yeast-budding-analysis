from PIL import Image, ImageOps, ImageFilter, ImageChops
import cv2 
import os


from utils import * 
from fill import Analyzer, ManualAnalyzer
from key import Key



class main():
    def __init__(self):
        return 
    


    def read_flags(self):
        pass




    def setup_folder(self, filename):
        path = '/'.join(filename.split('/')[:-1]) + "/"
        title = filename.split('/')[-1].split(".")[0]
        os.makedirs(path + title, exist_ok=True)
        return title, path
    

    def save(self, img, title):
        print("Saving", title)
        img.save(title, "PNG")
    

    def make_ym(self, img, title, path):

        micronpp = UNIT_PER_PIXEL

        if 'ppi' in img.info:
            micronpp = ppi_to_micronpp(img.info['ppi'][0])
        else:
            print("No PPI metadata found. Using default image PPI. Ensure this is accurate for conversions to microns.")


        return YeastManager(title, path, micronpp, UNITS)


    def grayscale_image_copy(self, filename):
        original = Image.open(filename)
        original = ImageOps.grayscale(original) 
        original = original.convert("RGB")
        return original

    
    def analyze(self, filename, key=True):
        '''
        Analyzes given file and generates output files

        '''
        title, path = self.setup_folder(filename)
        img = Image.open(filename)
        
        ym = self.make_ym(img, title, path)
        

        img = ImageOps.grayscale(img) 
        img = img.convert("RGB")
        
        #img = img.filter(ImageFilter.GaussianBlur(SMOOTHING))
        
        #img = ImageOps.autocontrast(img, cutoff = CONTRAST_CUTOFF, ignore = CONTRAST_IGNORE)
        #filter_out_grays(img)


        raw = cv2.imread(filename)
        canny = cv2.Canny(raw, THRESHOLD1,THRESHOLD2)
        color_coverted = cv2.cvtColor(canny, cv2.COLOR_BGR2RGB)
        
        img = Image.fromarray(color_coverted)
        img = ImageOps.invert(img)
        self.save(img, path + title + "/cleaned_" + title + ".png")

        a = Analyzer(img, ym)
        a.analyze()

        original = self.grayscale_image_copy(filename)

        img = ImageChops.multiply(original, img)

        if key:
            k=Key(img, DISPLAY_COLORKEY)
            img = k.append_key(img)


        self.save(img,path + title + "/results_of_" + title + ".png")
        ym.results()

        a.label_img(img)
        self.save(img, path + title + "/labeled_" + title + ".png")
        
    

    def manual_analyze(self, filename, key=True):
        title, path = self.setup_folder(filename)
        img = Image.open(filename)

        
        img = Image.open(filename)
        ym = self.make_ym(img, title, path)
        a = ManualAnalyzer(img, ym)
        self.save(a.img, path + title + "/READPRESET" + title + ".png")
        a.refine_preset()
        a.analyze()


        ym.results()


        original = self.grayscale_image_copy(filename)

        img = ImageChops.multiply(original, a.output)

        if key:
            k=Key(img, DISPLAY_COLORKEY)
            img = k.append_key(img)

        self.save(img, path + title + "/results_of_" + title + ".png")

        a.label_img(img)
        self.save(img, path + title + "/labeled_" + title + ".png")






m = main()

m.analyze("tests/test.jpg")
print("partial done")
m.analyze("tests/full_test.jpg")
print("full done")

m.analyze("tests/cleaner_test.jpg")
#m.manual_analyze("tests/cleaner_test.jpg")
#m.manual_analyze("tests/test.jpg")
print("cleaner done")