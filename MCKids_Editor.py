from tkinter import filedialog
from tkinter import *
from PIL import Image, ImageDraw, ImageTk
from compression import decompress
from level import Level
from rom import RomFile
from colors import colors
from tileset import TileSet
from sprite import Sprite


RomFile.load_rom("mckids.nes")

# supplementary table at 0xA08D lower, 0xA0B9 upper, 0xA0E5 bank
# index came from 0x77D. this is for stuff in banks 0xD-0xF in the other table,
# but the data is actually in CHR memory space, so it pulls it from the ppu

# stage ID comes from an array at bank 1 offset 0x77F. The index to that array
# comes from 0x6DE which is updated when walking on the map

# haven't even started on attribute tables

# the main window
window = Tk()
window.geometry("1084x1084")# + str(stage_height*16*2 + 16))

stage_canvas = Canvas(window, width=1024, height=1024, borderwidth=0, highlightthickness=0)

xscrollbar = Scrollbar(window, orient=HORIZONTAL)
xscrollbar.place(x=40, y = 1064, width = 1024)
yscrollbar = Scrollbar(window, orient=VERTICAL)
yscrollbar.place(x=1064, y = 40, height = 1024)

stage = None
pi = None
photo = None
ti = None


def rgba_to_rgb_palette(rgbaPalette):
    palette = []
    for i in range(len(rgbaPalette)):
        palette.append(rgbaPalette[i][0])
        palette.append(rgbaPalette[i][1])
        palette.append(rgbaPalette[i][2])
    return palette

level = Level()
palette = None
attribute_lookup = None
tile_palette_map = None

def draw_stage():
    pass


def render_stage(canvas, stage_num):
    global rom
    global window
    global photo
    global stage
    global stage_width
    global stage_tile_info
    global palette
    global attribute_lookup
    global tile_palette_map

    #print("loading bank 0x%X address 0x%X" %(stages[stage_num]['bank'], stages[stage_num]['offset']))
    if RomFile.stage_pointers[stage_num]['bank'] < 0xD:
        stage_data = RomFile.banks[RomFile.stage_pointers[stage_num]['bank']][RomFile.stage_pointers[stage_num]['offset'] - RomFile.BANK_BASE:]
    else:
        stage_data = RomFile.chr_banks[RomFile.stage_pointers[stage_num]['bank']][RomFile.stage_pointers[stage_num]['offset']:]


    palette_index = []
    general_stage_data = []
    attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
    for i in range(2,6):
        palette_bank = RomFile.banks[1][0xE5 + stage_data[i]]
        palette_addr = (RomFile.banks[1][0xB9 + stage_data[i]] << 8) + RomFile.banks[1][0x8D + stage_data[i]]
        #print("stage_data[%d] = 0x%x" % (i, stage_data[i]))
        #print(palette_bank)
        #print("0x%X" % palette_addr)
        general_stage_data.append(decompress(RomFile.banks[palette_bank][palette_addr + 1 - RomFile.BANK_BASE:], RomFile.banks[palette_bank][palette_addr - RomFile.BANK_BASE] >> 4, RomFile.banks[palette_bank][palette_addr - RomFile.BANK_BASE] & 0xF))
        #print(general_stage_data[i-2])
        for j in range(0,4):
            #print(general_stage_data[i-2][j])
            if general_stage_data[i-2][j] in palette_index or len(palette_index) == 4:
                continue
            else:
                #print("index 0x%x" % (general_stage_data[i-2][j]))
                #print("attribute 0x%x" % (3-len(palette_index)))
                attribute_lookup[general_stage_data[i-2][j]] = 3-len(palette_index)
                palette_index.insert(0, general_stage_data[i-2][j])
            if len(palette_index) == 4:
                break
    for i in range(0,4-len(palette_index)):
        palette_index.insert(0,0x6)
    #attribute_count = 3
    #for i in range(0,8):
    #    if i in palette_index:
    #        attribute_lookup[i] = attribute_count
    #        attribute_count -= 1


    # the code has a special case to replace the palette indexes for stage index 29
    if stage_num == 29:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[RomFile.banks[0xD][0x41 + i]] = i
            palette_index[i] = RomFile.banks[0xD][0x41 + i]
    # the code has a special case to replace the palette indexes for stage index 48 & 50
    if stage_num == 48 or stage_num == 50:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[RomFile.banks[0xD][0xA5 + i] & 7] = i
            palette_index[i] = RomFile.banks[0xD][0xA5 + i]
    # the code has a special case to replace the palette indexes for stage index 70
    if stage_num == 70:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[RomFile.banks[0xD][0x23A + i] & 7] = i
            palette_index[i] = RomFile.banks[0xD][0x23A + i]
    # the code has a special case to replace the palette indexes for stage index 73
    if stage_num == 73:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[RomFile.banks[0xD][0x22A + i] & 7] = i
            palette_index[i] = RomFile.banks[0xD][0x22A + i]
    # the code has a special case to replace the palette indexes for stage index 76
    if stage_num == 76:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[RomFile.banks[0xD][0x25A + i] & 7] = i
            palette_index[i] = RomFile.banks[0xD][0x25A + i]

    #print(palette_index)
    #print(attribute_lookup)

    palette = []
    palette_flags = RomFile.banks[1][0x254:]
    for i in range(0,4):
        # the first (or 0) color for each group of 4 colors is always the stage background color
        palette.append([colors[RomFile.banks[1][0x1F7 + stage_num]]])
    #print(palette)
    for i in range(0,4):
        for j in range(0,3):
            palette[i].append(colors[RomFile.banks[1][0x20*j + ((palette_index[i] & 0xF) + ((palette_index[i] & 0xF0) >> 1))
                              + ((palette_flags[stage_num] & 1) << 3)
                              + (((palette_flags[stage_num] & 4) >> 2) * 0x18)]])

    chr_palette_index = [0, 1]
    chr_palette_index.append(RomFile.banks[1][0x30E + stage_num])
    chr_palette_index.append(RomFile.banks[1][0x36B + stage_num])
    chr_palette = []
    for i in range(0,4):
        # the first (or 0) color for each group of 4 chr colors is always the alpha no matter what the value is
        chr_palette.append([(0, 0, 0, 0)])
    #print(palette)
    for i in range(0,4):
        for j in range(0,3):
            chr_palette[i].append(colors[RomFile.banks[1][0x60 + 0xF*j + chr_palette_index[i]]])
                                                    #+ ((palette_index[i] & 0xF0) >> 1))
                                                    #+ ((palette_flags[stage_num] & 1) << 3)
                                                    #+ (((palette_flags[stage_num] & 4) >> 2) * 0x18)]])


    # here we're checking for the stage num, but in the game code it calls special
    # code for world 5 (0x77A == 4) that adjusts this color to 0x1C
    # same for world 3 (0x77A == 1) to adjust to 0x30
    for i in range(0,4):
        if palette_index[i] == 0:
            if stage_num == 4:
                palette[i][1] = colors[0x1C]
            if stage_num == 1:
                palette[i][1] = colors[0x30]
            if stage_num == 5:
                palette[i][1] = colors[0x29]
            if stage_num == 6:
                palette[i][1] = colors[0x00]
            if stage_num == 12:
                palette[i][1] = colors[0x30]
            if stage_num == 13:
                palette[i][1] = colors[0x30]
            if stage_num == 19:
                palette[i][1] = colors[0x00]
            if stage_num == 20:
                palette[i][1] = colors[0x29]
    #print(palette)

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
    #print(len(general_stage_data))
    tile_palette_map = []
    for i in range(0,4):
        tile_palette_map.extend(general_stage_data[i][5 + general_stage_data[i][4]*4:5 + general_stage_data[i][4]*5])
        #print(len(tile_palette_map))
        for j in range(0,64*(i+1)-len(tile_palette_map)):
            tile_palette_map.append(0)
        #print(len(tile_palette_map))
    #print(tile_palette_map)
    #print(len(tile_palette_map))


    # There is a table that points to the bank and address of the tile map
    # The table consists of 3 arrays of length 0x2C (44). The three arrays are
    # lower address byte, upper address byte, bank number
    # note that the address in the table includes the base bank offset of 0xA000
    tile_map_comp = []
    tile_map_comp.append(RomFile.banks[RomFile.banks[1][0xE5 + stage_data[2]]][(RomFile.banks[1][0xB9 + stage_data[2]] << 8) + RomFile.banks[1][0x8D + stage_data[2]] - RomFile.BANK_BASE:])
    tile_map_comp.append(RomFile.banks[RomFile.banks[1][0xE5 + stage_data[3]]][(RomFile.banks[1][0xB9 + stage_data[3]] << 8) + RomFile.banks[1][0x8D + stage_data[3]] - RomFile.BANK_BASE:])
    tile_map_comp.append(RomFile.banks[RomFile.banks[1][0xE5 + stage_data[4]]][(RomFile.banks[1][0xB9 + stage_data[4]] << 8) + RomFile.banks[1][0x8D + stage_data[4]] - RomFile.BANK_BASE:])
    tile_map_comp.append(RomFile.banks[RomFile.banks[1][0xE5 + stage_data[5]]][(RomFile.banks[1][0xB9 + stage_data[5]] << 8) + RomFile.banks[1][0x8D + stage_data[5]] - RomFile.BANK_BASE:])


    # will need to make functions to reload these, and gui options to drive them
    tile_map_raw = []
    tile_map_raw.append(decompress(tile_map_comp[0][1:], tile_map_comp[0][0] >> 4, tile_map_comp[0][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[1][1:], tile_map_comp[1][0] >> 4, tile_map_comp[1][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[2][1:], tile_map_comp[2][0] >> 4, tile_map_comp[2][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[3][1:], tile_map_comp[3][0] >> 4, tile_map_comp[3][0] & 0xF))

    #this probably needs to become class based and gui driven
    stage_width = stage_data[0]
    stage_height = stage_data[1]

    # this is a magic number for stage 1, need to figure out how the game is doing this
    chr_map = RomFile.banks[1][0x111:]

    # rom = bytearray(RomFile.rom)
    chr_data = bytearray([])
    for i in range(2, 6):
        offset = 0x20000 + (0x400 * chr_map[stage_data[i]])
        chr_data += RomFile.rom[offset:offset + 0x0400]

    # The sprite chr banks IDs are put into 0x31A and 0x31B
    # 0x31A was loaded from an array at bank 0 offset 0xF31.
    # the index to this array came from an array at bank 0xE offset 0xF9E
    # the index to this array came from 0x414 + 0xCFA6[0x3FA]
    # 0x3FA came from 0x3F7. 0x3F7 is set to 3, but only because 0x4A0 was positive
    # 0x414 is 0 for Mack and 1 for Mick
    # 0x31B was loaded from an array at bank 0 offset 0xF31.
    # The index to this array came from an array at bank 1 offset 0x2B1
    # The index to that was the stage num
    mick_mack = 1
    sprite_chr_data  = RomFile.rom[0x20000 + (0x400 * RomFile.banks[0][0xF31 + RomFile.banks[0xE][0xF9E + RomFile.banks[0xE][0xFA6 + 3] + mick_mack]]):0x20000 + (0x400 * RomFile.banks[0][0xF31 + RomFile.banks[0xE][0xF9E + RomFile.banks[0xE][0xFA6 + 3] + mick_mack]]) + 0x800]
    sprite_chr_data += RomFile.rom[0x20000 + (0x400 * RomFile.banks[0][0xF31 + RomFile.banks[1][0x2B1 + stage_num]]):0x20000 + (0x400 * RomFile.banks[0][0xF31 + RomFile.banks[1][0x2B1 + stage_num]]) + 0x800]

    level.decompress(stage_data)
    spawn_count = len(level.spawn_points)

    # spawn ID is used to index an array at bank 3 offset 0x11D3
    # that value is ANDed with 0x3C and ORed with 0x1 and stored to an array at 0x4C0
    # spawn ID is used to index an array at bank 3 offset 0x1253
    # that value is ANDed with 0xC and stored to an array at 0x594
    # spawn ID is used to index an array at bank 3 offset 0x11D3
    # that value is ANDed with 0x2 and 0x55B is only incremented if the result is 0
    # spawn ID is used to index an array at bank 3 offset 0x1153
    # that value is pushed to the stack
    # spawn ID is used to index an array at bank 3 offset 0x10D3
    # that value is stored to 0x746
    # the values from the arrays at 0x1153 and 0x10D3 are used as the A and Y arguments
    # to the routine at 0xD18E
    # the value from bank 3 0x10D3 index spawn ID gets stored to an array at 0x614
    # the value from bank 3 0x1153 index spawn ID gets stored to an array at 0x624
    # 0 gets stored to the arrays at 0x634 and 0x654
    # 1 gets stored to the array at 0x664 but it gets decremented if the 0x10D3 value wasn't 0
    # the value from 0x10D3 is used to load 0x22-0x25 by indexing arrays at bank 0 0xF59, 0xF6D, 0xF81, 0xF95
    # (0x22) and (0x24) are used as a pointers to an arrays. The arrays are indexed by the 0x1153 value
    # and used to put a new pointer at 0x22-0x23
    # the new pointer at (0x22) is used to access an array indexed by the value from the array at 0x634
    # it is pushed to the stack twice and stored in the array at 0x664
    # it is pulled off the stack once ANDed with 0x40 and stored to 0x27
    # a value from an array at 0x5D4 is ANDed with 0xBF, ORed with that value we just put into 0x27 and stored back to the array at 0x5D4
    # it is pulled off the stack again ANDed with 0x80 and stored to 0x27
    # a value from an array at 0x5E4 is ANDed with 0x7F, ORed with that value we just put into 0x27 and stored back to the array at 0x5E4
    # the index that we originally got from 0x634 is incremented
    # we pull a new value from the new array at (0x22) and store it to the array at 0x5A4
    # a value from the array at 0x614 is stored to the array at 0x584
    # the index is incremented again and stored back to the array at 0x634
    # a value is pulled from the array at bank 3 offset 0x13D3 indexed by the spawn ID and stored to 0x301
    # if it was not zero a value is pulled from the array at bank 3 offset 0x1353 indexed by the spawn ID and stored to 0x300
    # a value is loaded from the array at bank 3 offset 0x1653 indexed by the spawn ID and that chr bank is loaded
    # the array index (enemy slot?) is pushed to the stack along with 0xE8 and 0xDF are pushed to the stack
    # the function we just loaded into 0x300 as a pointer is called. it does nothing in this case
    # values from 0x57, 0x55, 0x58, and 0x56 are loaded into the arrays at 0x470, 0x450, 0x460, and 0x440
    #
    # 0x201 came from (0x1A) which is bank 0 offset 0x14E6 index Y
    # Y was 5, looked like index 5 of a structure of some kind
    # 0x1A was loaded from (0x1A) which was bank 0 offset 0x141F indexed by the value from the array at 0x5A4 index 0
    # 0x5A4 came from (0x22) index (0x624 index X) + 2
    # 0x624 was loaded with 0
    # This new 0x22 was build from an old (0x22) as the lower and (0x24) as the upper, both indexed by 0x624 index X
    # The old 0x22-0x25 came from bank 0 offsets 0xF59, 0xF6D, 0xF81, 0xF95 indexed by Y
    # Y came from 0x614 index X. X was loaded with 0
    # 0x1A was loaded from bank 0 offset 0xEE1 index Y and 0x1B was loaded from bank 0 offset 0xEF5 index Y
    # Y came from the array at 0x584 offset 0 which came from 0x614 offset 0
    # 0x614 came from bank 0xE offset 0xFA2 index Y
    # Y came from bank 0xE offset 0xFA6 index Y
    # Y came from 0x3FA which came from 0x3F7 which was set to 0
    #
    # new 1A is A191
    # old 1A is A189 any Y came from 584
    # 584 came from 614
    for i in range(0, spawn_count):
        if RomFile.sprites[level.spawn_points[i].sprite_index] is None:
            RomFile.sprites[level.spawn_points[i].sprite_index] = Sprite.load_sprite(level.spawn_points[i].sprite_index)

    for i in range(0, 4):
        RomFile.tile_sets[level.tile_set_indices[i]] = TileSet()
        RomFile.tile_sets[level.tile_set_indices[i]].from_decompressed_bytes(tile_map_raw[i], i)

    RomFile.load_tile_patterns(chr_data)
    RomFile.load_sprite_patterns(sprite_chr_data, chr_palette)


    # DRAW THE STAGE:

    # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
    stage = Image.new('RGBA', (level.width*16*2,level.height*16*2))
    if show_overlay.get() == 1:
        overlay = Image.new('RGBA', (level.width*16*2, level.height*16*2))
        overlay_draw = ImageDraw.Draw(overlay)

    for i in range(level.width * level.height):
        x = (i % level.width) * 16 * 2
        y = int(i / level.width) * 16 * 2
        p = rgba_to_rgb_palette(palette[attribute_lookup[tile_palette_map[level.tile_map[i]]]])
        level.get_tile_at(i).draw(stage, x, y, p)

        if show_overlay.get() == 1:
            tile_type = level.get_tile_at(i).tile_type
            solid_color = (255, 0, 0, 200)
            if tile_type in completely_solid_types:
                overlay_draw.rectangle([x, y, x + 32, y + 32], solid_color)
            if tile_type == 0x02 or tile_type == 0x18 or tile_type == 0x21:
                overlay_draw.polygon([(x, y+32), (x+32, y), (x+32, y+32)], solid_color)
            if tile_type == 0x03 or tile_type == 0x17 or tile_type == 0x22:
                overlay_draw.polygon([(x, y), (x, y+32), (x+32, y+32)], solid_color)
            if tile_type == 0x04 or tile_type == 0x16 or tile_type == 0x23:
                overlay_draw.polygon([(x, y), (x+32, y), (x+32, y+32)], solid_color)
            if tile_type == 0x05 or tile_type == 0x15 or tile_type == 0x24:
                overlay_draw.polygon([(x, y), (x+32, y), (x, y+32)], solid_color)

            if tile_type == 0x09:
                overlay_draw.polygon([(x, y+32), (x+32, y+32), (x+32, y+16)], solid_color)
            if tile_type == 0x0A:
                overlay_draw.polygon([(x, y+16), (x+32, y), (x+32, y+32), (x, y+32)], solid_color)
            if tile_type == 0x0B:
                overlay_draw.polygon([(x, y), (x + 32, y+16), (x+32, y + 32), (x, y+32)], solid_color)
            if tile_type == 0x0C:
                overlay_draw.polygon([(x, y+16), (x+32, y+32), (x, y+32)], solid_color)

            if tile_type == 0x70:
                overlay_draw.line([(x, y+32), (x+16, y+16), (x+32, y+16)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x71:
                overlay_draw.line([(x+32, y), (x+16, y+16), (x+16, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x72:
                overlay_draw.line([(x, y+16), (x+16, y+16), (x+32, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x73:
                overlay_draw.line([(x, y), (x+16, y+16), (x+16, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x74:
                overlay_draw.line([(x+16, y), (x+16, y+16), (x+32, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x75:
                overlay_draw.line([(x, y), (x+16, y+16), (x+32, y+16)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x76:
                overlay_draw.line([(x, y+16), (x+16, y+16), (x+32, y)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x77:
                overlay_draw.line([(x+16, y), (x+16, y+16), (x, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x78:
                overlay_draw.line([(x, y+16), (x+32, y+16)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x79:
                overlay_draw.line([(x+16, y), (x+16, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x7A:
                overlay_draw.line([(x, y), (x+32, y+32)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x7B:
                overlay_draw.line([(x, y+32), (x+32, y)], fill=(0, 255, 0, 200), width=4)
            if tile_type == 0x7C:
                overlay_draw.line([(x, y+16), (x+32, y+16)], fill=(0, 255, 0, 200), width=4)
                overlay_draw.line([(x+16, y), (x+16, y+32)], fill=(0, 255, 0, 200), width=4)

            overlay_draw.rectangle([x, y, x + 32, y + 32], outline=(255,255,255,100))

    for i in range(0,spawn_count):#min(2,spawn_count)):
        # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage

        sprite = RomFile.sprites[level.spawn_points[i].sprite_index]
        for j in range(sprite.width * sprite.height):
            x = level.spawn_points[i].x * 16 * 2 + (j % sprite.width) * 8 * 2
            y = level.spawn_points[i].y * 16 * 2 + int(j / sprite.width) * 8 * 2 - ((sprite.height - 2) * 16)
            RomFile.sprite_patterns[sprite.chr_pointers[j]].draw(stage, x, y, sprite.palette_index)

    if show_overlay.get() == 1:
        stage = Image.alpha_composite(stage, overlay)
    canvas.config(scrollregion=(0, 0, level.width*16*2, level.height*16*2))

completely_solid_types = [0x08, 0x01, 0x1B, 0x20, 0x25]
somewhat_solid_types = []

#something = decompress(bank[9][0x193E:],bank[9][0x193D] >> 4,bank[9][0x193D] & 0xF)
#print(something)
#print(len(something))

stage_num_list = {}
for i in range(0,0x5D):
    stage_num_list[str(i)] = i

tkvar = StringVar(window)
tkvar.set(stage_num_list['0'])
stage_dropdown = OptionMenu(window, tkvar, *stage_num_list)
show_overlay = IntVar()
overlay_checkbox = Checkbutton(window, text="Show solids", variable=show_overlay)
info_var = StringVar(window)
info_label = Label(window, textvariable=info_var)

def change_stage_dropdown(*args):
    global window
    global stage_canvas
    global stage
    global ti
    #print(stage_num_list[tkvar.get()])
    render_stage(stage_canvas, stage_num_list[tkvar.get()])
    ti = ImageTk.PhotoImage(stage)

    stage_canvas.create_image(0, 0, anchor=NW, image=ti, tags="img")
    stage_canvas.place(x=40, y=40, anchor=NW)
    stage_canvas.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
    xscrollbar.config(command=stage_canvas.xview)
    yscrollbar.config(command=stage_canvas.yview)


def update_info_label(event):
    global stage_width
    global stage_tile_info
    global stage_canvas

    canvas = event.widget
    x = (int)(canvas.canvasx(event.x) / 32)
    y = (int)(canvas.canvasy(event.y) / 32)
    index = level.width * y + x
    if len(level.tile_map) > index:
        type = level.get_tile_at(index).tile_type
        tile_set_index = level.tile_map[index]
        info_var.set(f'Tile type: 0x{format(type, "02x")}, ' +
                     f' Tile set index: 0x{format(tile_set_index, "02x")},' +
                     f' Data index: 0x{format(index, "04x")}, ' +
                     f' X: {x}, Y: {y}')
    else:
        info_var.set(f'Out of range: {index}')


def save_level_button_clicked():
    RomFile.save_level(int(tkvar.get()), level)


def save_rom_button_clicked():
    filename = filedialog.asksaveasfilename(defaultextension=".nes")
    if len(filename) > 0:
        RomFile.write_rom(filename)


def canvas_clicked(event):
    canvas = event.widget
    x = int(canvas.canvasx(event.x) / 32)
    y = int(canvas.canvasy(event.y) / 32)
    paint_tile(canvas, x, y)

def paint_tile(canvas, x, y):
    global stage
    global stage_canvas
    global palette
    global attribute_lookup
    global tile_palette_map
    global ti

    paint_with_index = 0x5B # throwable block in stage 1-1
    index = level.width * y + x
    if level.tile_map[index] != paint_with_index:
        level.tile_map[index] = paint_with_index
        p = rgba_to_rgb_palette(palette[attribute_lookup[tile_palette_map[paint_with_index]]])
        level.get_tile(paint_with_index).draw(stage, x*32, y*32, p)
        ti = ImageTk.PhotoImage(stage)
        stage_canvas.itemconfig("img",image=ti)

save_level_btn = Button(window, text="Save level", command=save_level_button_clicked)
save_rom_btn = Button(window, text="Save ROM", command=save_rom_button_clicked)

tkvar.trace('w', change_stage_dropdown)
show_overlay.trace('w', change_stage_dropdown)

render_stage(stage_canvas, stage_num_list[tkvar.get()])
stage_dropdown.place(x=5, y=5)
overlay_checkbox.place(x=60, y=8)
info_label.place(x=160, y=10)
save_level_btn.place(x=800, y=8)
save_rom_btn.place(x=880, y=8)

stage_canvas.bind('<Motion>', update_info_label)
stage_canvas.bind('<Button-1>', canvas_clicked)
stage_canvas.bind('<B1-Motion>', canvas_clicked)

ti = ImageTk.PhotoImage(stage)
stage_canvas.create_image(0, 0, anchor=NW, image=ti, tags="img")

stage_canvas.place(x=40, y=40, anchor=NW)
stage_canvas.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
xscrollbar.config(command=stage_canvas.xview)
yscrollbar.config(command=stage_canvas.yview)

window.mainloop()
