from chr import Chr


class RomFile:
    tile_sets = [[]] * 100000
    sprites = []
    tile_patterns = []
    sprite_patterns = []

    headers = []
    banks = []

    def load_tile_patterns(chr_data):
        RomFile.tile_patterns.clear()
        for i in range(0, 256):
            # self.characters.append(self.chr_to_indexed_image(chr_data, i))
            RomFile.tile_patterns.append(Chr.make_indexed_chr(chr_data[i * 0x10: i * 0x10 + 0x10]))

    def load_sprite_patterns(chr_data, palette):
        RomFile.sprite_patterns.clear()
        for j in range(0, 256):
            RomFile.sprite_patterns.append(Chr.make_chr_with_alpha(chr_data[j * 0x10: j * 0x10 + 0x10], palette))

