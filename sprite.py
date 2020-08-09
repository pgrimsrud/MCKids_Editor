from rom import RomFile


class Sprite:
    def __init__(self, width, height, chr_pointers, palette_index):
        self.width = width
        self.height = height
        self.chr_pointers = chr_pointers
        self.palette_index = palette_index

    @staticmethod
    def load_sprite(sprite_index):
        if sprite_index >= 0x80 and sprite_index <= 0x97:
            sprite_index = 0x50
        val_614 = RomFile.banks[3][0x10D3 + sprite_index]
        if sprite_index == 0x4A or sprite_index == 0x4B:
            val_614 = RomFile.banks[3][0x10D3 + 0x1F]
        elif val_614 == 0:
            val_614 = RomFile.banks[3][0x10D3 + 0xA]
        old_22 = (RomFile.banks[0][0xF6D + val_614] << 8) + RomFile.banks[0][0xF59 + val_614]
        old_24 = (RomFile.banks[0][0xF95 + val_614] << 8) + RomFile.banks[0][0xF81 + val_614]
        val_624 = RomFile.banks[3][0x1153 + sprite_index]
        if sprite_index == 0x4A or sprite_index == 0x4B:
            val_624 = RomFile.banks[3][0x1153 + 0x1F]
        elif sprite_index == 0x29 or sprite_index == 0x28:
            val_624 = RomFile.banks[3][0x1153 + 0xA]
        elif sprite_index == 0x6C:
            val_624 = RomFile.banks[3][0x1153 + 0x6F]
        elif sprite_index == 0x2A:
            val_624 = 1
        # print("0x%X" % sprite_index)
        # print("0x%X" % old_22)
        # print("0x%X" % old_24)
        # print("0x%X" % val_624)
        new_22 = (RomFile.banks[0][old_24 - RomFile.BANK_BASE + val_624] << 8) + RomFile.banks[0][old_22 - RomFile.BANK_BASE + val_624]
        # print("0x%X" % new_22)
        val_5A4 = RomFile.banks[0][new_22 - RomFile.BANK_BASE + 1]
        val_584 = val_614
        val_F45 = RomFile.banks[0][0xF45 + val_584]
        old_1A = (RomFile.banks[0][0xEF5 + val_584] << 8) + RomFile.banks[0][0xEE1 + val_584]
        old_1C = (RomFile.banks[0][0xF1D + val_584] << 8) + RomFile.banks[0][0xF09 + val_584]
        new_1A = (RomFile.banks[0][old_1C - RomFile.BANK_BASE + val_5A4] << 8) + RomFile.banks[0][old_1A - RomFile.BANK_BASE + val_5A4]

        spawn_pattern_flags = RomFile.banks[0][new_1A - RomFile.BANK_BASE]
        if sprite_index == 0x3A:
            sprite_width = 2
            sprite_height = 3
        elif spawn_pattern_flags == 0x80 or spawn_pattern_flags == 0x82:
            sprite_width = 2
            sprite_height = 4
        else:
            sprite_width = RomFile.banks[0][new_1A - RomFile.BANK_BASE + 3]
            sprite_height = RomFile.banks[0][new_1A - RomFile.BANK_BASE + 4]

        # Below here is stuff that goes into the RomFile object
        sprite_bytes = RomFile.banks[0][new_1A - RomFile.BANK_BASE:new_1A - RomFile.BANK_BASE + 5 + (sprite_width * sprite_height) + 200]
        chr_pointers = []

        if sprite_index == 0x3A:
            chr_pointers.append(sprite_bytes[0x03] | val_F45)
            chr_pointers.append(sprite_bytes[0x06] | val_F45)
            chr_pointers.append(sprite_bytes[0x09] | val_F45)
            chr_pointers.append(sprite_bytes[0x0C] | val_F45)
            chr_pointers.append(sprite_bytes[0x11] | val_F45)
            chr_pointers.append(sprite_bytes[0x14] | val_F45)
        elif spawn_pattern_flags == 0x80:
            for j in range(0, 4):
                chr_pointers.insert(0, sprite_bytes[j * 6 + 6] | val_F45)
                chr_pointers.insert(0, sprite_bytes[j * 6 + 3] | val_F45)
        elif spawn_pattern_flags == 0x82:
            chr_pointers.append(sprite_bytes[0x25] | val_F45)
            chr_pointers.append(sprite_bytes[0x28] | val_F45)
            chr_pointers.append(sprite_bytes[0x5D] | val_F45)
            chr_pointers.append(sprite_bytes[0x60] | val_F45)
            chr_pointers.append(sprite_bytes[0x79] | val_F45)
            chr_pointers.append(sprite_bytes[0x7C] | val_F45)
            chr_pointers.append(sprite_bytes[0x7F] | val_F45)
            chr_pointers.append(sprite_bytes[0x82] | val_F45)
        else:
            for j in range(5, 5 + sprite_width * sprite_height):
                chr_pointers.append(sprite_bytes[j] | val_F45)

        return Sprite(sprite_width, sprite_height, chr_pointers, sprite_bytes[0] & 0x3)
        # RomFile.sprites[sprite_index] = Sprite(sprite_width, sprite_height, chr_pointers, sprite_bytes[0] & 0x3)