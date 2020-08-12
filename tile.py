

class Tile:
    def __init__(self):
        self.characters = [0, 0, 0, 0]
        self.tile_type = 0

    def draw(self, canvas, x, y, palette, level, index, rom_file):
        rom_file.get_chr(self.characters[0] + 0x40 * index, level).draw(canvas, x, y, palette)
        rom_file.get_chr(self.characters[1] + 0x40 * index, level).draw(canvas, x+16, y, palette)
        rom_file.get_chr(self.characters[2] + 0x40 * index, level).draw(canvas, x, y+16, palette)
        rom_file.get_chr(self.characters[3] + 0x40 * index, level).draw(canvas, x+16, y+16, palette)
