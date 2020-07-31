from tkinter import *
from PIL import Image, ImageTk
from compression import compress, decompress

file_name = "mckids.nes"

rom = open(file_name, "rb").read()
ines = rom[0:0x10]
rom = rom[0x10:]
chr_rom = rom[0x20000:]


# After the header the next 128k consists of 16 8k chunks called banks
# the routine at 0xF077 loads the bank you pass in the A register
# the requested bank is loaded at 0xA000
# the last two banks are always statically loaded at 0xC000 and 0xE000
bank_base = 0xA000
bank = []
chr_bank = []
for i in range(0,16):
    bank.append(rom[0x2000*i : 0x2000*i + 0x2000])
    chr_bank.append(chr_rom[0x2000*i : 0x2000*i + 0x2000])

# stage data pointers are in bank 1. The data consists of 3 arrays of 0x5D (93) elements
# The three arrays are lower address byte, upper address byte, bank number
# note that the address in the table includes the base bank offset of 0xA000 unless it is fixed bank 0xE or 0xF
stages = []
for i in range(0,0x5D):
    stages.append({'bank': bank[1][0x5F6 + i], 'offset': ((bank[1][0x599 + i] << 8) + bank[1][0x53C + i])})

# supplementary table at 0xA08D lower, 0xA0B9 upper, 0xA0E5 bank
# index came from 0x77D. this is for stuff in banks 0xD-0xF in the other table,
# but the data is actually in CHR memory space, so it pulls it from the ppu

# stage ID comes from an array at bank 1 offset 0x77F. The index to that array
# comes from 0x6DE which is updated when walking on the map

# palette information is stored in arrays in bank 1 at 0x0000, 0x0020, and 0x0040
# indexes are pulled from 0x69A-0x69D
# looks like that was copied from 0x6700 territory which was unpacked from somewhere in bank 9
# 0x69A gets 4 from bank 9 0xB93D offset 1
# 0x69B gets 2 from bank 9 0xB061 offset 2
# 0x69C gets 1 from bank 9 0xB061 offset 1
# 0x69D gets 0 from bank 9 0xB061 offset 0
    # the 9/B061 came from arrays at 0x8D, 0xB9, 0xE5 in bank 1. the offset came from 0x77D
# I think it fills slots from back to front and ends if it finds a duplicate?
# table of base background colors at bank 1 0x1F7 indexed by stage ID

colors = [
          ( 84, 84, 84,255), #       DARK_GRAY          0x00
          (  0, 30,116,255), #       DARK_GRAY_BLUE     0x01
          (  8, 16,144,255), #       DARK_BLUE          0x02
          ( 48,  0,136,255), #       DARK_PURPLE        0x03
          ( 68,  0,100,255), #       DARK_PINK          0x04
          ( 92,  0, 48,255), #       DARK_FUCHSIA       0x05
          ( 84,  4,  0,255), #       DARK_RED           0x06
          ( 60, 24,  0,255), #       DARK_ORANGE        0x07
          ( 32, 42,  0,255), #       DARK_TAN           0x08
          (  8, 58,  0,255), #       DARK_GREEN         0x09
          (  0, 64,  0,255), #       DARK_LIME_GREEN    0x0A
          (  0, 60,  0,255), #       DARK_SEAFOAM_GREEN 0x0B
          (  0, 50, 60,255), #       DARK_CYAN          0x0C
          (  0,  0,  0,255), #            BLACK_2       0x0D
          (  0,  0,  0,255), #            BLACK         0x0E
          (  0,  0,  0,255), #            BLACK_3       0x0F
          (152,150,152,255), #            GRAY          0x10
          (  8, 76,196,255), #            GRAY_BLUE     0x11
          ( 48, 50,236,255), #            BLUE          0x12
          ( 92, 30,228,255), #            PURPLE        0x13
          (136, 20,176,255), #            PINK          0x14
          (160, 20,100,255), #            FUCHSIA       0x15
          (152, 34, 32,255), #            RED           0x16
          (120, 60,  0,255), #            ORANGE        0x17
          ( 84, 90,  0,255), #            TAN           0x18
          ( 40,114,  0,255), #            GREEN         0x19
          (  8,124,  0,255), #            LIME_GREEN    0x1A
          (  0,118, 40,255), #            SEAFOAM_GREEN 0x1B
          (  0,102,120,255), #            CYAN          0x1C
          (  0,  0,  0,255), #            BLACK_4       0x1D
          (  0,  0,  0,255), #            BLACK_5       0x1E
          (  0,  0,  0,255), #            BLACK_6       0x1F
          (255,255,255,255), #      LIGHT_GRAY          0x20
          ( 76,154,236,255), #      LIGHT_GRAY_BLUE     0x21
          (120,124,236,255), #      LIGHT_BLUE          0x22
          (176, 98,236,255), #      LIGHT_PURPLE        0x23
          (228, 84,236,255), #      LIGHT_PINK          0x24
          (236, 88,180,255), #      LIGHT_FUCHSIA       0x25
          (236,106,100,255), #      LIGHT_RED           0x26
          (212,136, 32,255), #      LIGHT_ORANGE        0x27
          (160,170,  0,255), #      LIGHT_TAN           0x28
          (116,196,  0,255), #      LIGHT_GREEN         0x29
          ( 76,208, 32,255), #      LIGHT_LIME_GREEN    0x2A
          ( 56,204,108,255), #      LIGHT_SEAFOAM_GREEN 0x2B
          ( 56,180,204,255), #      LIGHT_CYAN          0x2C
          ( 60, 60, 60,255), #       DARK_GRAY_2        0x2D
          (  0,  0,  0,255), #            BLACK_7       0x2E
          (  0,  0,  0,255), #            BLACK_8       0x2F
          (255,255,255,255), #            WHITE         0x30
          (168,204,236,255), # VERY_LIGHT_GRAY_BLUE     0x31
          (188,188,236,255), # VERY_LIGHT_BLUE          0x32
          (212,178,236,255), # VERY_LIGHT_PURPLE        0x33
          (236,174,236,255), # VERY_LIGHT_PINK          0x34
          (236,174,212,255), # VERY_LIGHT_FUCHSIA       0x35
          (236,180,176,255), # VERY_LIGHT_RED           0x36
          (228,196,144,255), # VERY_LIGHT_ORANGE        0x37
          (204,210,120,255), # VERY_LIGHT_TAN           0x38
          (180,222,120,255), # VERY_LIGHT_GREEN         0x39
          (168,226,144,255), # VERY_LIGHT_LIME_GREEN    0x3A
          (152,226,180,255), # VERY_LIGHT_SEAFOAM_GREEN 0x3B
          (160,214,228,255), # VERY_LIGHT_CYAN          0x3C
          (160,162,160,255), #            GRAY_2        0x3D
          (  0,  0,  0,255), #            BLACK_9       0x3E
          (  0,  0,  0,255)] #            BLACK_10      0x3F


# need to figure out how the game does this
#palette = [(0,0,0),
#           (100,100,100),
#           (200,200,200),
#           (255,255,255)]

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

#this converts the 16 byte pattern table data to an array of color indexes 0-3 for the 8x8 tile
def pattern_map(pattern):
    pixels = []
    for i in range(0,64):
        pixels.append((((pattern[(i>>3) + 8] >> (7 - (i & 7))) & 1) << 1) + (pattern[i>>3] >> (7 - (i & 7)) & 1))
    return pixels

game_characters = []

def load_game_characters(chr_data):
    game_characters.clear()
    for i in range(0,256):
        game_characters.append(chr_to_indexed_image(chr_data, i))

def chr_to_indexed_image(chr_data, num):
    pixels = pattern_map(chr_data[num * 0x10: num * 0x10 + 0x10])
    img = Image.new('P', (8, 8))
    for x in range(8):
        for y in range(8):
            img.putpixel((x, y), pixels[x + y * 8])
    img = img.resize((16, 16))
    return img


def draw_character(canvas, x, y, palette, num):
    game_characters[num].putpalette(palette)
    canvas.paste(game_characters[num], (x, y))

def rgba_to_rgb_palette(rgbaPalette):
    palette = []
    for i in range(len(rgbaPalette)):
        palette.append(rgbaPalette[i][0])
        palette.append(rgbaPalette[i][1])
        palette.append(rgbaPalette[i][2])
    return palette


def render_stage(canvas, stage_num):
    global rom
    global window
    global photo
    global stage

    stage_data = []
    #print("loading bank 0x%X address 0x%X" %(stages[stage_num]['bank'], stages[stage_num]['offset']))
    if stages[stage_num]['bank'] < 0xD:
        stage_data = bank[stages[stage_num]['bank']][stages[stage_num]['offset'] - bank_base:]
    else:
        stage_data = chr_bank[stages[stage_num]['bank']][stages[stage_num]['offset']:]


    palette_index = []
    general_stage_data = []
    attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
    for i in range(2,6):
        palette_bank = bank[1][0xE5 + stage_data[i]]
        palette_addr = (bank[1][0xB9 + stage_data[i]] << 8) + bank[1][0x8D + stage_data[i]]
        #print("stage_data[%d] = 0x%x" % (i, stage_data[i]))
        #print(palette_bank)
        #print("0x%X" % palette_addr)
        general_stage_data.append(decompress(bank[palette_bank][palette_addr + 1 - bank_base:], bank[palette_bank][palette_addr - bank_base] >> 4, bank[palette_bank][palette_addr - bank_base] & 0xF))
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
            attribute_lookup[bank[0xD][0x41 + i]] = i
            palette_index[i] = bank[0xD][0x41 + i]
    # the code has a special case to replace the palette indexes for stage index 48 & 50
    if stage_num == 48 or stage_num == 50:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[bank[0xD][0xA5 + i] & 7] = i
            palette_index[i] = bank[0xD][0xA5 + i]
    # the code has a special case to replace the palette indexes for stage index 70
    if stage_num == 70:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[bank[0xD][0x23A + i] & 7] = i
            palette_index[i] = bank[0xD][0x23A + i]
    # the code has a special case to replace the palette indexes for stage index 73
    if stage_num == 73:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[bank[0xD][0x22A + i] & 7] = i
            palette_index[i] = bank[0xD][0x22A + i]
    # the code has a special case to replace the palette indexes for stage index 76
    if stage_num == 76:
        attribute_lookup = [2, 2, 2, 2, 2, 2, 2, 2]
        for i in range(0,4):
            attribute_lookup[bank[0xD][0x25A + i] & 7] = i
            palette_index[i] = bank[0xD][0x25A + i]

    #print(palette_index)
    #print(attribute_lookup)

    palette = []
    palette_flags = bank[1][0x254:]
    for i in range(0,4):
        # the first (or 0) color for each group of 4 colors is always the stage background color
        palette.append([colors[bank[1][0x1F7 + stage_num]]])
    #print(palette)
    for i in range(0,4):
        for j in range(0,3):
            palette[i].append(colors[bank[1][0x20*j + ((palette_index[i] & 0xF) + ((palette_index[i] & 0xF0) >> 1))
                              + ((palette_flags[stage_num] & 1) << 3)
                              + (((palette_flags[stage_num] & 4) >> 2) * 0x18)]])


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
    tile_map_comp.append(bank[bank[1][0xE5 + stage_data[2]]][(bank[1][0xB9 + stage_data[2]] << 8) + bank[1][0x8D + stage_data[2]] - bank_base:])
    tile_map_comp.append(bank[bank[1][0xE5 + stage_data[3]]][(bank[1][0xB9 + stage_data[3]] << 8) + bank[1][0x8D + stage_data[3]] - bank_base:])
    tile_map_comp.append(bank[bank[1][0xE5 + stage_data[4]]][(bank[1][0xB9 + stage_data[4]] << 8) + bank[1][0x8D + stage_data[4]] - bank_base:])
    tile_map_comp.append(bank[bank[1][0xE5 + stage_data[5]]][(bank[1][0xB9 + stage_data[5]] << 8) + bank[1][0x8D + stage_data[5]] - bank_base:])


    # will need to make functions to reload these, and gui options to drive them
    tile_map_raw = []
    tile_map_raw.append(decompress(tile_map_comp[0][1:], tile_map_comp[0][0] >> 4, tile_map_comp[0][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[1][1:], tile_map_comp[1][0] >> 4, tile_map_comp[1][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[2][1:], tile_map_comp[2][0] >> 4, tile_map_comp[2][0] & 0xF))
    tile_map_raw.append(decompress(tile_map_comp[3][1:], tile_map_comp[3][0] >> 4, tile_map_comp[3][0] & 0xF))

    tile_map_size = []
    tile_map_size.append(tile_map_raw[0][4])
    tile_map_size.append(tile_map_raw[1][4])
    tile_map_size.append(tile_map_raw[2][4])
    tile_map_size.append(tile_map_raw[3][4])
    tile_map = [[],[],[],[]]
    for i in range(0,4):
        for j in range(5 + tile_map_size[0]*i,5 + tile_map_size[0]*(i+1)):
            tile_map[i].append(tile_map_raw[0][j])
        for j in range(0,64-tile_map_size[0]):
            tile_map[i].append(0)
        for j in range(5 + tile_map_size[1]*i,5 + tile_map_size[1]*(i+1)):
            tile_map[i].append(tile_map_raw[1][j] + 0x40)
        for j in range(0,64-tile_map_size[1]):
            tile_map[i].append(0)
        for j in range(5 + tile_map_size[2]*i,5 + tile_map_size[2]*(i+1)):
            tile_map[i].append(tile_map_raw[2][j] + 0x80)
        for j in range(0,64-tile_map_size[2]):
            tile_map[i].append(0)
        for j in range(5 + tile_map_size[3]*i,5 + tile_map_size[3]*(i+1)):
            tile_map[i].append(tile_map_raw[3][j] + 0xC0)
        for j in range(0,64-tile_map_size[3]):
            tile_map[i].append(0)

    #this probably needs to become class based and gui driven
    stage_width = stage_data[0]
    stage_height = stage_data[1]

    # this is a magic number for stage 1, need to figure out how the game is doing this
    chr_map = bank[1][0x111:]

    rom = bytearray(rom)
    chr_data  = rom[0x20000 + (0x400 * chr_map[stage_data[2]]):0x20000 + (0x400 * chr_map[stage_data[2]]) + 0x400]
    chr_data += rom[0x20000 + (0x400 * chr_map[stage_data[3]]):0x20000 + (0x400 * chr_map[stage_data[3]]) + 0x400]
    chr_data += rom[0x20000 + (0x400 * chr_map[stage_data[4]]):0x20000 + (0x400 * chr_map[stage_data[4]]) + 0x400]
    chr_data += rom[0x20000 + (0x400 * chr_map[stage_data[5]]):0x20000 + (0x400 * chr_map[stage_data[5]]) + 0x400]

    stage_decompressed = decompress(stage_data[7:], stage_data[6] >> 4, stage_data[6] & 0xF)

    spawn_count = stage_decompressed[0]
    stage_spawn_info = stage_decompressed[1:]

    spawn_x = []
    spawn_y = []
    spawn_id = []
    spawn_property = []

    for i in range(0,spawn_count):
        spawn_x.append(stage_spawn_info[i])
        spawn_y.append(stage_spawn_info[spawn_count+i])
        spawn_id.append(stage_spawn_info[2*spawn_count+i])
        spawn_property.append(stage_spawn_info[3*spawn_count+i])
    stage_tile_info = stage_spawn_info[4*spawn_count:]

    load_game_characters(chr_data)

    # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
    stage = Image.new('RGB', (stage_width*16*2,stage_height*16*2))
    for i in range(stage_width * stage_height):
        x = (i % stage_width) * 16 * 2
        y = int(i / stage_width) * 16 * 2
        p = rgba_to_rgb_palette(palette[attribute_lookup[tile_palette_map[stage_tile_info[i]]]])
        draw_character(stage, x, y, p, tile_map[0][stage_tile_info[i]])
        draw_character(stage, x + 16, y, p, tile_map[1][stage_tile_info[i]])
        draw_character(stage, x, y + 16, p, tile_map[2][stage_tile_info[i]])
        draw_character(stage, x + 16, y + 16, p, tile_map[3][stage_tile_info[i]])

    canvas.config(scrollregion=(0, 0, stage_width*16*2, stage_height*16*2))

#something = decompress(bank[9][0x193E:],bank[9][0x193D] >> 4,bank[9][0x193D] & 0xF)
#print(something)
#print(len(something))

stage_num_list = {}
for i in range(0,0x5D):
    stage_num_list[str(i)] = i

tkvar = StringVar(window)
tkvar.set(stage_num_list['0'])
stage_dropdown = OptionMenu(window, tkvar, *stage_num_list)

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

tkvar.trace('w', change_stage_dropdown)

render_stage(stage_canvas, stage_num_list[tkvar.get()])
stage_dropdown.place(x=5, y=5)


ti = ImageTk.PhotoImage(stage)
stage_canvas.create_image(0, 0, anchor=NW, image=ti, tags="img")

stage_canvas.place(x=40, y=40, anchor=NW)
stage_canvas.config(xscrollcommand=xscrollbar.set, yscrollcommand=yscrollbar.set)
xscrollbar.config(command=stage_canvas.xview)
yscrollbar.config(command=stage_canvas.yview)

window.mainloop()