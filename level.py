from compression import compress, decompress
from spawnpoint import SpawnPoint
from rom import RomFile
from colors import colors
from tileset import TileSet
from sprite import Sprite


class Level:  # This class needs a lot of clean up.
    def __init__(self):
        self.width = 0
        self.height = 0
        self.tile_map = []
        self.tile_set_indices = [0, 0, 0, 0]
        self.spawn_points = []
        self.sprites = []
        self.palette = None
        self.stage_sprite_index = 0

    def decompress(self, compressed_data):
        self.width = compressed_data[0]
        self.height = compressed_data[1]

        self.tile_set_indices = compressed_data[2:6]

        stage_data = decompress(compressed_data[7:], compressed_data[6] >> 4, compressed_data[6] & 0xF)

        spawn_count = stage_data[0]
        stage_spawn_info = stage_data[1:spawn_count * 4 + 1]
        self.tile_map = stage_data[spawn_count * 4 + 1:]

        self.spawn_points.clear()
        for i in range(spawn_count):
            self.add_spawn_point(SpawnPoint(
                stage_spawn_info[i], stage_spawn_info[spawn_count + i],
                stage_spawn_info[spawn_count * 2 + i], stage_spawn_info[spawn_count * 3 + i]
            ))

    def compress(self):
        output = [self.width, self.height,
                  self.tile_set_indices[0],
                  self.tile_set_indices[1],
                  self.tile_set_indices[2],
                  self.tile_set_indices[3]]

        spawn_count = len(self.spawn_points)
        stage_data = [spawn_count]
        for i in range(spawn_count):
            stage_data.append(self.spawn_points[i].x)
        for i in range(spawn_count):
            stage_data.append(self.spawn_points[i].y)
        for i in range(spawn_count):
            stage_data.append(self.spawn_points[i].sprite_index)
        for i in range(spawn_count):
            stage_data.append(self.spawn_points[i].index)

        stage_data += self.tile_map

        best_size = 100000
        best_offset = 0
        best_length = 0
        best_result = []
        for offset in range(8, 13):
            for length in range(4, 10):
                result = compress(stage_data, offset, length)
                print(f'Compressing {offset}:{length} = {len(result)} bytes')
                if len(result) < best_size:
                    best_size = len(result)
                    best_offset = offset
                    best_length = length
                    best_result = result

        output.append((best_offset << 4) + (best_length & 0x0F))
        return output + best_result

    def get_tile(self, tile_index):
        return RomFile.tile_sets[self.tile_set_indices[tile_index >> 6]].tiles[tile_index & 0x3F]

    def get_tile_at(self, index):
        return self.get_tile(self.tile_map[index])

    def add_spawn_point(self, sprite):
        self.spawn_points.append(sprite)

    @staticmethod
    def load_level(stage_num, stage_data):
        level = Level()

        palette_index = []
        palette_data = []
        level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(2, 6):
            palette_bank = RomFile.banks[1][0xE5 + stage_data[i]]
            palette_addr = (RomFile.banks[1][0xB9 + stage_data[i]] << 8) + RomFile.banks[1][0x8D + stage_data[i]]
            # print("stage_data[%d] = 0x%x" % (i, stage_data[i]))
            # print(palette_bank)
            # print("0x%X" % palette_addr)
            palette_data.append(decompress(RomFile.banks[palette_bank][palette_addr + 1 - RomFile.BANK_BASE:],
                                                 RomFile.banks[palette_bank][palette_addr - RomFile.BANK_BASE] >> 4,
                                                 RomFile.banks[palette_bank][palette_addr - RomFile.BANK_BASE] & 0xF))
            # print(palette_data[i-2])
            for j in range(0, 4):
                # print(palette_data[i-2][j])
                if palette_data[i - 2][j] in palette_index or len(palette_index) == 4:
                    continue
                else:
                    # print("index 0x%x" % (palette_data[i-2][j]))
                    # print("attribute 0x%x" % (3-len(palette_index)))
                    level.attribute_lookup[palette_data[i - 2][j]] = 3 - len(palette_index)
                    palette_index.insert(0, palette_data[i - 2][j])
                if len(palette_index) == 4:
                    break
        for i in range(0, 4 - len(palette_index)):
            palette_index.insert(0, 0x6)
        # attribute_count = 3
        # for i in range(0,8):
        #    if i in palette_index:
        #        attribute_lookup[i] = attribute_count
        #        attribute_count -= 1

        # the code has a special case to replace the palette indexes for stage index 29
        if stage_num == 29:
            level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
            for i in range(0, 4):
                level.attribute_lookup[RomFile.banks[0xD][0x41 + i]] = i
                palette_index[i] = RomFile.banks[0xD][0x41 + i]
        # the code has a special case to replace the palette indexes for stage index 48 & 50
        if stage_num == 48 or stage_num == 50:
            level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
            for i in range(0, 4):
                level.attribute_lookup[RomFile.banks[0xD][0xA5 + i] & 7] = i
                palette_index[i] = RomFile.banks[0xD][0xA5 + i]
        # the code has a special case to replace the palette indexes for stage index 70
        if stage_num == 70:
            level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
            for i in range(0, 4):
                level.attribute_lookup[RomFile.banks[0xD][0x23A + i] & 7] = i
                palette_index[i] = RomFile.banks[0xD][0x23A + i]
        # the code has a special case to replace the palette indexes for stage index 73
        if stage_num == 73:
            level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
            for i in range(0, 4):
                level.attribute_lookup[RomFile.banks[0xD][0x22A + i] & 7] = i
                palette_index[i] = RomFile.banks[0xD][0x22A + i]
        # the code has a special case to replace the palette indexes for stage index 76
        if stage_num == 76:
            level.attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
            for i in range(0, 4):
                level.attribute_lookup[RomFile.banks[0xD][0x25A + i] & 7] = i
                palette_index[i] = RomFile.banks[0xD][0x25A + i]

        # print(palette_index)
        # print(attribute_lookup)

        level.palette = []
        palette_flags = RomFile.banks[1][0x254:]
        for i in range(0, 4):
            # the first (or 0) color for each group of 4 colors is always the stage background color
            level.palette.append([colors[RomFile.banks[1][0x1F7 + stage_num]]])
        # print(palette)
        for i in range(0, 4):
            for j in range(0, 3):
                level.palette[i].append(
                    colors[RomFile.banks[1][0x20 * j + ((palette_index[i] & 0xF) + ((palette_index[i] & 0xF0) >> 1))
                                            + ((palette_flags[stage_num] & 1) << 3)
                                            + (((palette_flags[stage_num] & 4) >> 2) * 0x18)]])

        chr_palette_index = [0, 1, RomFile.banks[1][0x30E + stage_num], RomFile.banks[1][0x36B + stage_num]]
        RomFile.chr_palette = []
        for i in range(0, 4):
            # the first (or 0) color for each group of 4 chr colors is always the alpha no matter what the value is
            RomFile.chr_palette.append([(0, 0, 0, 0)])
        # print(palette)
        for i in range(0, 4):
            for j in range(0, 3):
                RomFile.chr_palette[i].append(colors[RomFile.banks[1][0x60 + 0xF * j + chr_palette_index[i]]])
                # + ((palette_index[i] & 0xF0) >> 1))
                # + ((palette_flags[stage_num] & 1) << 3)
                # + (((palette_flags[stage_num] & 4) >> 2) * 0x18)]])

        # here we're checking for the stage num, but in the game code it calls special
        # code for world 5 (0x77A == 4) that adjusts this color to 0x1C
        # same for world 3 (0x77A == 1) to adjust to 0x30
        for i in range(0, 4):
            if palette_index[i] == 0:
                if stage_num == 4:
                    level.palette[i][1] = colors[0x1C]
                if stage_num == 1:
                    level.palette[i][1] = colors[0x30]
                if stage_num == 5:
                    level.palette[i][1] = colors[0x29]
                if stage_num == 6:
                    level.palette[i][1] = colors[0x00]
                if stage_num == 12:
                    level.palette[i][1] = colors[0x30]
                if stage_num == 13:
                    level.palette[i][1] = colors[0x30]
                if stage_num == 19:
                    level.palette[i][1] = colors[0x00]
                if stage_num == 20:
                    level.palette[i][1] = colors[0x29]
        # print(palette)

        # attribute tables. looks like the tile id is used to index an array at 0x6400
        # that data is probably unpacked from somewhere. that info is then used to index a table at 0x782
        # it looks like the real used values are 0, 1, 2, and 4 and the table at 0x782
        # ends up with 0xFF, 0xAA, 0x55, and 0x00 in those slots, probably for attribute table convenience
        # we were storing stuff to the 0x6300 range until we got to the count stored in 0x761
        # the count in 0x671 came from 0x6704, and it got there by being unpacked.
        # the 6700 data was unpacked from bank 9 0xB061 and the first 3 bytes went to palette info
        # it looks for the next byte in the palette index list which was just partially
        # populated by the previous 3 bytes. It then takes byte 4 as a length and copies groups
        # of length bytes to 0x6000, 0x6100, etc.
        # I think it just ends up being take that thing we decompressed for palette index pointers
        # byte 4 is a length, group the rest into chunks that size, grab the 5th group to
        # copy into your 64 byte chunk of the 6400s, pad with 0s
        # I think this only gets us an index to the table at 0x782 though. that table tells us which palette
        # depending on quadrant
        # print(len(palette_data))
        level.tile_palette_map = []
        for i in range(0, 4):
            level.tile_palette_map.extend(
                palette_data[i][5 + palette_data[i][4] * 4:5 + palette_data[i][4] * 5])
            for j in range(0, 64 * (i + 1) - len(level.tile_palette_map)):
                level.tile_palette_map.append(0)

        level.stage_sprite_index = RomFile.banks[1][0x2B1 + stage_num]

        level.decompress(stage_data)
        spawn_count = len(level.spawn_points)

        for i in range(0, spawn_count):
            if RomFile.sprites[level.spawn_points[i].sprite_index] is None:
                RomFile.sprites[level.spawn_points[i].sprite_index] = Sprite.load_sprite(
                    level.spawn_points[i].sprite_index)

        for i in range(0, 4):
            tile_set_compressed = RomFile.banks[RomFile.banks[1][0xE5 + stage_data[i + 2]]][
                         (RomFile.banks[1][0xB9 + stage_data[i + 2]] << 8) + RomFile.banks[1][
                             0x8D + stage_data[i + 2]] - RomFile.BANK_BASE:]
            tile_set_raw = decompress(tile_set_compressed[1:], tile_set_compressed[0] >> 4, tile_set_compressed[0] & 0xF)

            RomFile.tile_sets[level.tile_set_indices[i]] = TileSet()
            RomFile.tile_sets[level.tile_set_indices[i]].from_decompressed_bytes(tile_set_raw)

        return level
