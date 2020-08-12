from chr import Chr


class RomFile:
    BANK_BASE = 0xA000
    CHR_BANK_BASE = 0x8000


    def __init__(self, filename, from_project):
        self.tile_sets = [[]] * 10000
        self.sprites = [None] * 10000
        self.tile_patterns = [None] * 100
        self.sprite_patterns = [[None] * 100] * 16  # Are there 16 palettes?

        self.ines_header = []
        self.rom = []
        self.banks = []
        self.chr_banks = []
        self.chr_map = []
        self.chr_palette = []

        self.stage_pointers = []
        self.levels = [None] * 100

        self.rom = open(filename, "rb").read()
        self.ines_header = self.rom[0:0x10]
        self.rom = bytearray(self.rom[0x10:])
        chr_rom = self.rom[0x20000:]

        # After the header the next 128k consists of 16 8k chunks called banks
        # the routine at 0xF077 loads the bank you pass in the A register
        # the requested bank is loaded at 0xA000
        # the last two banks are always statically loaded at 0xC000 and 0xE000
        for i in range(0, 16):
            self.banks.append(self.rom[0x2000 * i: 0x2000 * i + 0x2000])
            self.chr_banks.append(chr_rom[0x2000 * i: 0x2000 * i + 0x2000])

        self.chr_map = self.banks[1][0x111:]

        # stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
        # The three arrays are lower address byte, upper address byte, bank number
        # note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
        self.stage_pointers = []
        for i in range(0, 0x5D):
            self.stage_pointers.append({'bank': self.banks[1][0x5F6 + i],
                           'offset': ((self.banks[1][0x599 + i] << 8) + self.banks[1][0x53C + i])})

    def load_tile_set_patterns(self, tile_set_index):
        self.tile_patterns[tile_set_index] = []
        offset = 0x20000 + (0x400 * self.chr_map[tile_set_index])
        chr_data = self.rom[offset:offset + 0x0400]
        for i in range(0, 64):
            self.tile_patterns[tile_set_index].append(Chr.make_indexed_chr(chr_data[i * 0x10: i * 0x10 + 0x10]))

    def get_chr(self, character_index, level):
        tile_set_index = level.tile_set_indices[int(character_index / 64)]
        chr_index = character_index % 64
        if self.tile_patterns[tile_set_index] is None:
            self.load_tile_set_patterns(tile_set_index)
        character = self.tile_patterns[tile_set_index][chr_index]
        return character

    def load_sprite_set_patterns(self, tile_set_index, palette):
        self.sprite_patterns[palette][tile_set_index] = []
        chr_data_ptr = 0x20000 + (0x400 * self.banks[0][0xF31 + tile_set_index])
        chr_data = self.rom[chr_data_ptr:chr_data_ptr + 0x800]
        for j in range(0, 128):
            self.sprite_patterns[palette][tile_set_index].append(Chr.make_chr_with_alpha(chr_data[j * 0x10: j * 0x10 + 0x10], self.chr_palette[palette]))

    def get_sprite_chr(self, character_index, palette, level):
        if character_index < 128:
            tile_set_index = 13
        else:
            tile_set_index = level.stage_sprite_index
        chr_index = character_index % 128
        if self.sprite_patterns[palette][tile_set_index] is None:
            self.load_sprite_set_patterns(tile_set_index, palette)
        character = self.sprite_patterns[palette][tile_set_index][chr_index]
        return character

    def write_to_rom(self, data, destination):
        length = len(data)
        for i in range(length):
            self.rom[destination + i] = data[i]

    def save_level(self, index):
        level = self.levels[index]
        data = level.compress()
        bank = self.stage_pointers[index]['bank']
        pointer = bank * 0x2000 + self.stage_pointers[index]['offset'] - RomFile.BANK_BASE
        self.write_to_rom(data, pointer)

    def write_rom(self, filename):
        with open(filename, "wb") as fp:
            fp.write(bytearray(self.ines_header) + bytearray(self.rom))

