from rom import RomFile


class Tile:
    def __init__(self):
        self.characters = [0, 0, 0, 0]
        self.tile_type = 0

    def draw(self, canvas, x, y, palette, level, index):
        RomFile.get_chr(self.characters[0] + 0x40 * index, level).draw(canvas, x, y, palette)
        RomFile.get_chr(self.characters[1] + 0x40 * index, level).draw(canvas, x+16, y, palette)
        RomFile.get_chr(self.characters[2] + 0x40 * index, level).draw(canvas, x, y+16, palette)
        RomFile.get_chr(self.characters[3] + 0x40 * index, level).draw(canvas, x+16, y+16, palette)
