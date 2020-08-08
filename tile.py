from rom import RomFile


class Tile:
    def __init__(self):
        self.characters = [0, 0, 0, 0]
        self.tile_type = 0

    def draw(self, canvas, x, y, palette):
        RomFile.tile_patterns[self.characters[0]].draw(canvas, x, y, palette)
        RomFile.tile_patterns[self.characters[1]].draw(canvas, x+16, y, palette)
        RomFile.tile_patterns[self.characters[2]].draw(canvas, x, y+16, palette)
        RomFile.tile_patterns[self.characters[3]].draw(canvas, x+16, y+16, palette)
