from chr import Chr


class RomFile:
    BANK_BASE = 0xA000
    CHR_BANK_BASE = 0x8000

    tile_sets = [[]] * 10000
    sprites = [None] * 10000
    tile_patterns = []
    sprite_patterns = []

    ines_header = []
    rom = []
    banks = []
    chr_banks = []

    stage_pointers = []

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

        # stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
        # The three arrays are lower address byte, upper address byte, bank number
        # note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
        RomFile.stage_pointers = []
        for i in range(0, 0x5D):
            RomFile.stage_pointers.append({'bank': RomFile.banks[1][0x5F6 + i],
                           'offset': ((RomFile.banks[1][0x599 + i] << 8) + RomFile.banks[1][0x53C + i])})

    @staticmethod
    def load_tile_patterns(chr_data):
        RomFile.tile_patterns.clear()
        for i in range(0, 256):
            RomFile.tile_patterns.append(Chr.make_indexed_chr(chr_data[i * 0x10: i * 0x10 + 0x10]))

    @staticmethod
    def load_sprite_patterns(chr_data, palette):
        RomFile.sprite_patterns.clear()
        for j in range(0, 256):
            RomFile.sprite_patterns.append(Chr.make_chr_with_alpha(chr_data[j * 0x10: j * 0x10 + 0x10], palette))

    @staticmethod
    def write_to_rom(data, destination):
        length = len(data)
        for i in range(length):
            RomFile.rom[destination + i] = data[i]

    @staticmethod
    def save_level(index, level):
        data = level.compress()
        bank = RomFile.stage_pointers[index]['bank']
        pointer = bank * 0x2000 + RomFile.stage_pointers[index]['offset'] - RomFile.BANK_BASE
        RomFile.write_to_rom(data, pointer)

    @staticmethod
    def write_rom(filename):
        with open(filename, "wb") as fp:
            fp.write(bytearray(RomFile.ines_header) + bytearray(RomFile.rom))

