from PIL import Image


class Chr:
    INDEXED = 0
    WITH_ALPHA = 1

    def __init__(self, images, chr_type):
        self.images = images
        self.type = chr_type

    def draw(self, canvas, x, y, palette):
        if self.type == Chr.INDEXED:
            self.images[0].putpalette(palette)
            canvas.paste(self.images[0], (x, y))
        elif self.type == Chr.WITH_ALPHA:
            canvas.paste(self.images[palette], (x, y), mask=self.images[palette])

    @staticmethod
    def make_indexed_chr(chr_data):
        pixels = Chr.pattern_map(chr_data)
        img = Image.new('P', (8, 8))
        for x in range(8):
            for y in range(8):
                img.putpixel((x, y), pixels[x + y * 8])
        img = img.resize((16, 16))
        return Chr([img], Chr.INDEXED)

    @staticmethod
    def make_chr_with_alpha(chr_data, palettes):
        pixels = Chr.pattern_map(chr_data)
        images = []
        for p in palettes:
            img = Image.new('RGBA', (8, 8))
            for x in range(8):
                for y in range(8):
                    img.putpixel((x, y), p[pixels[x + y * 8]])
            img = img.resize((16, 16), resample=Image.NEAREST)
            images.append(img)
        return Chr(images, Chr.WITH_ALPHA)

    # this converts the 16 byte pattern table data to an array of color indexes 0-3 for the 8x8 tile
    @staticmethod
    def pattern_map(pattern):
        pixels = []
        for i in range(0, 64):
            pixels.append(
                (((pattern[(i >> 3) + 8] >> (7 - (i & 7))) & 1) << 1) + (pattern[i >> 3] >> (7 - (i & 7)) & 1))
        return pixels
