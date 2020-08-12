from chr import Chr
from sprite import Sprite
from compression import decompress
from tileset import TileSet


class RomFile:
    BANK_BASE = 0xA000
    CHR_BANK_BASE = 0x8000


    def __init__(self, filename, from_project):
        self.tile_sets = [None] * 45
        self.sprites = [None] * 10000
        self.tile_patterns = [None] * 45
        self.sprite_patterns = [[None] * 100] * 16  # Are there 16 palettes?
        self.palettes = [[]] * 45
        self.level_index_lookup = [-1] * 0x5D

        self.level_names = [" "] * 56
        self.start_pos_x = [0] * 0x5D
        self.start_pos_y = [0] * 0x5D

        self.ines_header = []
        self.rom = []
        self.banks = []
        self.chr_banks = []
        self.chr_map = []
        self.chr_palette = []

        self.stage_pointers = []
        self.levels = [None] * 0x5D

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
        self.__read_level_names()
        self.__load_level_index_lookup()
        self.__load_starting_positions()

        self.load_tile_sets()

        # stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
        # The three arrays are lower address byte, upper address byte, bank number
        # note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
        self.stage_pointers = []
        for i in range(0, 0x5D):
            self.stage_pointers.append({'bank': self.banks[1][0x5F6 + i],
                           'offset': ((self.banks[1][0x599 + i] << 8) + self.banks[1][0x53C + i])})

    def __read_level_names(self):
        for i in range(56):
            addr = (self.banks[1][0x0B54 + i] << 8) + self.banks[1][0x0B1B + i] - RomFile.BANK_BASE
            self.level_names[i] = ""
            while self.banks[1][addr] != 0:
                self.level_names[i] += chr(self.banks[1][addr])
                addr += 1

    def __load_level_index_lookup(self):
        for i in range(56):
            self.level_index_lookup[self.banks[1][0x077F + i]] = i

    def __load_starting_positions(self):
        for i in range(0x5D):
            self.start_pos_x[i] = self.banks[1][0x13D + i]
            self.start_pos_y[i] = self.banks[1][0x19A + i]

    def __write_start_positions(self):
        for i in range(0x5D):
            self.rom[0x2000 + 0x13D + i] = self.start_pos_x[i]
            self.rom[0x2000 + 0x19A + i] = self.start_pos_y[i]

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

    def get_sprite(self, index):
        if self.sprites[index] is None:
            self.sprites[index] = Sprite.load_sprite(index, self)

        return self.sprites[index]

    def write_to_rom(self, data, destination):
        length = len(data)
        for i in range(length):
            self.rom[destination + i] = data[i]

    def load_tile_sets(self):
        for index in range(1, 44):
            tile_set_compressed = self.banks[self.banks[1][0xE5 + index]][
                         (self.banks[1][0xB9 + index] << 8) + self.banks[1][
                             0x8D + index] - RomFile.BANK_BASE:]
            tile_set_raw = decompress(tile_set_compressed[1:], tile_set_compressed[0] >> 4, tile_set_compressed[0] & 0xF)

            self.tile_sets[index] = TileSet()
            self.tile_sets[index].from_decompressed_bytes(tile_set_raw)

    def save_level(self, index):
        level = self.levels[index]
        data = level.compress()
        bank = self.stage_pointers[index]['bank']
        pointer = bank * 0x2000 + self.stage_pointers[index]['offset'] - RomFile.BANK_BASE
        self.write_to_rom(data, pointer)

    def write_rom(self, filename):
        self.__write_start_positions()
        with open(filename, "wb") as fp:
            fp.write(bytearray(self.ines_header) + bytearray(self.rom))

