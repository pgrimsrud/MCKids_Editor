from chr import Chr
from fast_compression import fast_decompress, fast_compress, fast_compression_length
from sprite import Sprite
from tileset import TileSet


class RomFile:
    BANK_BASE = 0xA000
    CHR_BANK_BASE = 0x8000
    CHR_BANK_START = 0x20000

    LEVEL_BANK_ARRAY_OFFSET = 0x05F6
    LEVEL_OFFSET_HI_ARRAY_OFFSET = 0x0599
    LEVEL_OFFSET_LO_ARRAY_OFFSET = 0x053C

    ERROR_NONE = 0
    ERROR_COULD_NOT_FIT_ALL_STAGES = 1

    def __init__(self, filename, from_project):
        self.tile_sets = [None] * 45
        self.sprites = [None] * 10000
        self.tile_patterns = [None] * 45
        self.sprite_patterns = [[None] * 100] * 16  # Are there 16 palettes?
        self.palettes = [[]] * 45
        self.level_index_lookup = [-1] * 0x5D

        self.level_names = [" "] * 56

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
        self.load_banks_from_rom()

        self.chr_map = self.banks[1][0x111:]
        self.__read_level_names()
        self.__load_level_index_lookup()

        self.load_tile_sets()
        self.load_stage_pointers_and_properties()


    def load_stage_pointers_and_properties(self):
        # stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
        # The three arrays are lower address byte, upper address byte, bank number
        # note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
        self.stage_pointers = []
        for i in range(0, 0x5D):
            bank = self.banks[1][RomFile.LEVEL_BANK_ARRAY_OFFSET + i]
            offset = ((self.banks[1][RomFile.LEVEL_OFFSET_HI_ARRAY_OFFSET + i] << 8)
                      + self.banks[1][RomFile.LEVEL_OFFSET_LO_ARRAY_OFFSET + i])
            if bank < 0x0D:
                if offset == 0:
                    b_offset = 0
                else:
                    b_offset = offset - RomFile.BANK_BASE
                size = fast_compression_length(
                        self.banks[bank][b_offset + 7:],
                        self.banks[bank][b_offset + 6] >> 4,
                        self.banks[bank][b_offset + 6] & 0x0f
                    ) + 7
            else:
                size = fast_compression_length(
                        self.chr_banks[bank][offset+7:],
                        self.chr_banks[bank][offset + 6] >> 4,
                        self.chr_banks[bank][offset + 6] & 0x0f
                    ) + 7
            self.stage_pointers.append({
                'stage_id': i,
                'bank': bank,
                'offset': offset,
                'size': size
            })

    def resuffle_data(self):
        # Containers are sorted by size
        containers = [
            {'bank': 9, 'start': 0x0000, 'stages': [], 'space_remaining': 0x07E5},
            {'bank': 3, 'start': 0x16D3, 'stages': [], 'space_remaining': 0x092D},
            {'bank': 2, 'start': 0x1680, 'stages': [], 'space_remaining': 0x0980},
            {'bank': 1, 'start': 0x1540, 'stages': [], 'space_remaining': 0x0AC0},
            {'bank': 4, 'start': 0x1500, 'stages': [], 'space_remaining': 0x0B00},
            {'bank': 0x0D, 'start': 0x0C00, 'stages': [], 'space_remaining': 0x1400},
            {'bank': 5, 'start': 0x0600, 'stages': [], 'space_remaining': 0x1A00},
            {'bank': 6, 'start': 0x0000, 'stages': [], 'space_remaining': 0x2000},
            {'bank': 7, 'start': 0x0000, 'stages': [], 'space_remaining': 0x2000},
            {'bank': 8, 'start': 0x0000, 'stages': [], 'space_remaining': 0x2000},
            {'bank': 0x0E, 'start': 0x0000, 'stages': [], 'space_remaining': 0x2000},
            {'bank': 0x0F, 'start': 0x0000, 'stages': [], 'space_remaining': 0x2000}
        ]

        def get_size(obj):
            return obj.get('size')

        by_size = self.stage_pointers.copy()
        # for stage in by_size:

        for i in range(len(by_size)):
            by_size[i]['placed'] = False
        by_size[7]['placed'] = True
        by_size[92]['placed'] = True


        # Fill in stage data
        for stage in by_size:
            if self.levels[stage['stage_id']] is not None:
                stage['data'] = self.levels[stage['stage_id']].compress()
                stage['size'] = len(stage['data'])
            else:
                bank = self.stage_pointers[stage['stage_id']]['bank']
                if bank < 0x0D:
                    if self.stage_pointers[stage['stage_id']]['offset'] == 0:
                        b_offset = 0
                    else:
                        b_offset = self.stage_pointers[stage['stage_id']]['offset'] - RomFile.BANK_BASE

                    stage['data'] = self.banks[bank][b_offset:b_offset + stage['size']]
                else:
                    offset = self.stage_pointers[stage['stage_id']]['offset']
                    stage['data'] = self.chr_banks[bank][offset:offset + stage['size']]

        by_size.sort(key=get_size, reverse=True)
        lvl28_bank = 0
        lvl28_offset = 0
        for i in range(len(containers)):
            # Fill containers with as many items as possible
            if containers[i]['bank'] < 0x0D:
                offset = RomFile.BANK_BASE
            else:
                offset = 0
            for stage in by_size:
                if not stage['placed'] and stage['size'] <= containers[i]['space_remaining']:
                    stage['bank'] = containers[i]['bank']
                    stage['offset'] = containers[i]['start'] + offset
                    stage['placed'] = True
                    containers[i]['space_remaining'] -= stage['size']
                    containers[i]['stages'].append(stage['stage_id'])
                    offset += stage['size']
                    if stage['stage_id'] == 28:
                        lvl28_bank = stage['bank']
                        lvl28_offset = stage['offset']

        for i in range(len(by_size)):
            if not by_size[i]['placed']:
                return RomFile.ERROR_COULD_NOT_FIT_ALL_STAGES

        for stage in by_size:
            if stage['stage_id'] == 92:
                stage['bank'] = lvl28_bank
                stage['offset'] = lvl28_offset

            if stage['bank'] < 0x0D:
                pointer = stage['bank'] * 0x2000 + stage['offset'] - RomFile.BANK_BASE
            else:
                pointer = RomFile.CHR_BANK_START + stage['bank'] * 0x2000 + stage['offset']

            # write level data
            if stage['stage_id'] != 7:
                self.write_to_rom(stage['data'], pointer)
            # write to bank array
            self.rom[0x2000 + RomFile.LEVEL_BANK_ARRAY_OFFSET + stage['stage_id']] = stage['bank']
            # write to address arrays
            offset_hi = (stage['offset'] >> 8) & 0xFF
            offset_lo = stage['offset'] & 0xFF
            self.rom[0x2000 + RomFile.LEVEL_OFFSET_HI_ARRAY_OFFSET + stage['stage_id']] = offset_hi
            self.rom[0x2000 + RomFile.LEVEL_OFFSET_LO_ARRAY_OFFSET + stage['stage_id']] = offset_lo

        self.load_banks_from_rom()
        self.load_stage_pointers_and_properties()
        # We could also clear all levels (except the current one)
        # That would cause the editor to not re-compress unless the levels where loaded again

        return RomFile.ERROR_NONE

    def load_banks_from_rom(self):
        chr_rom = self.rom[0x20000:]
        self.banks = []
        self.chr_banks = []
        for i in range(0, 16):
            self.banks.append(self.rom[0x2000 * i: 0x2000 * i + 0x2000])
            self.chr_banks.append(chr_rom[0x2000 * i: 0x2000 * i + 0x2000])

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

    def __write_level_properties(self):
        for i in range(0x5C):
            if self.levels[i] is not None:
                self.rom[0x2000 + 0x013D + i] = self.levels[i].start_x
                self.rom[0x2000 + 0x019A + i] = self.levels[i].start_y
                self.rom[0x2000 + 0x0254 + i] = self.levels[i].flags1
                self.rom[0x2000 + 0x07B8 + self.banks[1][0x077F + i]] = self.levels[i].flags2
                self.rom[0x2000 + 0x02B1 + i] = self.levels[i].stage_sprite_index
                self.rom[0x2000 + 0x01F7 + i] = self.levels[i].bg_color
                self.rom[0x2000 + 0x04DF + i] = self.levels[i].music

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
            tile_set_raw = fast_decompress(tile_set_compressed[1:], tile_set_compressed[0] >> 4, tile_set_compressed[0] & 0xF)

            self.tile_sets[index] = TileSet()
            self.tile_sets[index].from_decompressed_bytes(tile_set_raw)

    def save_level(self, index):
        level = self.levels[index]
        data = level.compress()
        bank = self.stage_pointers[index]['bank']
        pointer = bank * 0x2000 + self.stage_pointers[index]['offset'] - RomFile.BANK_BASE
        self.write_to_rom(data, pointer)

    def write_rom(self, filename):
        result = self.resuffle_data()
        if result != RomFile.ERROR_NONE:
            return result
        self.__write_level_properties()
        with open(filename, "wb") as fp:
            fp.write(bytearray(self.ines_header) + bytearray(self.rom))

