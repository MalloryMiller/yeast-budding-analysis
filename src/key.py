from PIL import Image, ImageDraw, ImageFont


class Key():
    def __init__(self, img, colors):
        self.img = img
        self.colors = colors

        self.width = img.size[0]
        self.length = img.size[1]

        self.key_height = 75
        self.key_color_height = 50
        self.key_color_width = 170
        
        self.font_size = 18
        self.radius = 15

        self.key_color_text_padding = 17

        self.font = ImageFont.truetype("arial.ttf", self.key_color_height - (self.key_color_text_padding * 2))

        self.background_color = (255, 255, 255)
        self.text_color= (0,0,0)


        self.key_color_box_padding = (self.width - (self.key_color_width * len(colors.keys()))) // len(colors.keys())
        self.key = self.generate_key()

        

    def append_key(self, img):

        new = Image.new(mode="RGB", size=(self.width, self.length + self.key_height))
        new.paste(img)
        new.paste(self.key, (0,self.length))
        return new
    
    def generate_key(self):
        cur_pos = self.key_color_width // 2
        new = Image.new(mode="RGB", size=(self.width, self.key_height), color=self.background_color)

        for x in self.colors.keys():
            cur = self.generate_single_color_label(self.colors[x], x)
            new.paste(cur, (cur_pos, (self.key_height - self.key_color_height) // 2))
            cur_pos += cur.size[0] + self.key_color_width // 2
        

        return new

    def generate_single_color_label(self, label, color):
        key_label = Image.new(mode="RGB", size=(self.key_color_width, self.key_color_height), color=self.background_color)
        #key_label.paste(swatch)
        d = ImageDraw.Draw(key_label)
        d.rounded_rectangle(((0,0), (self.key_color_width, self.key_color_height)), self.radius, color)
        d.text((self.key_color_width // 2, self.key_color_height // 2), label, self.text_color, anchor='mm', align='center', font=self.font)
        return key_label

