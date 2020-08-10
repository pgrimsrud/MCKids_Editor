from chr import Chr


class RomFile:
    BANK_BASE = 0xA000
    CHR_BANK_BASE = 0x8000

    tile_sets = [[]] * 10000
    sprites = [None] * 10000
    tile_patterns = [None] * 100
    sprite_patterns = [[None] * 100] * 16  # Are there 16 palettes?

    ines_header = []
    rom = []
    banks = []
    chr_banks = []
    chr_map = []
    chr_palette = []

    stage_pointers = []
    levels = [None] * 100

    @staticmethod
    def load_rom(filename):
        rom = open(filename, "rb").read()
        RomFile.ines_header = rom[0:0x10]
        RomFile.rom = bytearray(rom[0x10:])
        chr_rom = RomFile.rom[0x20000:]

        # After the header the next 128k consists of 16 8k chunks called banks
        # the routine at 0xF077 loads the bank you pass in the A register
        # the requested bank is loaded at 0xA000
        # the last two banks are always statically loaded at 0xC000 and 0xE000
        for i in range(0, 16):
            RomFile.banks.append(RomFile.rom[0x2000 * i: 0x2000 * i + 0x2000])
            RomFile.chr_banks.append(chr_rom[0x2000 * i: 0x2000 * i + 0x2000])

        RomFile.chr_map = RomFile.banks[1][0x111:]

        # stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
        # The three arrays are lower address byte, upper address byte, bank number
        # note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
        RomFile.stage_pointers = []
        for i in range(0, 0x5D):
            RomFile.stage_pointers.append({'bank': RomFile.banks[1][0x5F6 + i],
                           'offset': ((RomFile.banks[1][0x599 + i] << 8) + RomFile.banks[1][0x53C + i])})

    @staticmethod
    def load_tile_set_patterns(tile_set_index):
        RomFile.tile_patterns[tile_set_index] = []
        offset = 0x20000 + (0x400 * RomFile.chr_map[tile_set_index])
        chr_data = RomFile.rom[offset:offset + 0x0400]
        for i in range(0, 64):
            RomFile.tile_patterns[tile_set_index].append(Chr.make_indexed_chr(chr_data[i * 0x10: i * 0x10 + 0x10]))

    @staticmethod
    def get_chr(character_index, level):
        tile_set_index = level.tile_set_indices[int(character_index / 64)]
        chr_index = character_index % 64
        if RomFile.tile_patterns[tile_set_index] is None:
            RomFile.load_tile_set_patterns(tile_set_index)
        character = RomFile.tile_patterns[tile_set_index][chr_index]
        return character

    @staticmethod
    def load_sprite_set_patterns(tile_set_index, palette):
        RomFile.sprite_patterns[palette][tile_set_index] = []
        chr_data_ptr = 0x20000 + (0x400 * RomFile.banks[0][0xF31 + tile_set_index])
        chr_data = RomFile.rom[chr_data_ptr:chr_data_ptr + 0x800]
        for j in range(0, 128):
            RomFile.sprite_patterns[palette][tile_set_index].append(Chr.make_chr_with_alpha(chr_data[j * 0x10: j * 0x10 + 0x10], RomFile.chr_palette[palette]))

    @staticmethod
    def get_sprite_chr(character_index, palette, level):
        if character_index < 128:
            tile_set_index = 13
        else:
            tile_set_index = level.stage_sprite_index
        chr_index = character_index % 128
        if RomFile.sprite_patterns[palette][tile_set_index] is None:
            RomFile.load_sprite_set_patterns(tile_set_index, palette)
        character = RomFile.sprite_patterns[palette][tile_set_index][chr_index]
        return character

    @staticmethod
    def write_to_rom(data, destination):
        length = len(data)
        for i in range(length):
            RomFile.rom[destination + i] = data[i]

    @staticmethod
    def save_level(index):
        level = RomFile.levels[index]
        data = level.compress()
        bank = RomFile.stage_pointers[index]['bank']
        pointer = bank * 0x2000 + RomFile.stage_pointers[index]['offset'] - RomFile.BANK_BASE
        RomFile.write_to_rom(data, pointer)

    @staticmethod
    def write_rom(filename):
        with open(filename, "wb") as fp:
            fp.write(bytearray(RomFile.ines_header) + bytearray(RomFile.rom))

