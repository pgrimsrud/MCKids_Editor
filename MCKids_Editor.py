from tkinter import *
from PIL import Image, ImageTk

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

# need to figure out how the game does this
palette = [(0,0,0),
           (100,100,100),
           (200,200,200),
           (255,255,255)]

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

# this creates an image for the tile from the pattern table and palette
def GetImage(chr_data, num):
    pattern = pattern_map(chr_data[num*0x10:num*0x10+0x10])

    img = Image.new('RGB', (16,16))

    for i in range(0,8):
        for j in range(0,8):
            for k in range(0,2):
                for l in range(0,2):
                    img.putpixel((i*2+k,j*2+l), palette[pattern[(j<<3) + i]])

    return img

# this copies a tile into a specified location in a larger image
def ImageCopy(dst, src, x, y, width, height):
    for i in range(0, width):
        for j in range(0, height):
            dst.putpixel((x+i, y+j), src.getpixel((i, j)))

# this function does the same decompression that the game does and seems to be working
# for both stage 1 and the pattern table mapping. note that the offset_size and length_size are
# variable and each compressed thing will specify these values
def decompress(data, offset_size, length_size):
    bit_ptr = 0
    result = []
    while 1:
        if (data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1 == 1:
            bit_ptr += 1
            byte = 0
            for i in range(0,8):
                byte += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (7-i)
                bit_ptr += 1
            result.append(byte)
        else:
            bit_ptr += 1
            offset = 0
            for i in range(0,offset_size):
                offset += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (offset_size-1-i)
                bit_ptr += 1
            length = 0
            for i in range(0,length_size):
                length += ((data[bit_ptr>>3] >> (7-(bit_ptr & 7))) & 1) << (length_size-1-i)
                bit_ptr += 1
            if offset == 0 and length == 0:
                break
            length += 3
            for i in range(0,length):
                result.append(result[len(result)-offset])

    return result

def render_stage(canvas, stage_num):
    global rom
    global window
    global photo
    global stage

    stage_data = []
    print("loading bank 0x%X address 0x%X" %(stages[stage_num]['bank'], stages[stage_num]['offset']))
    if stages[stage_num]['bank'] < 0xD:
        stage_data = bank[stages[stage_num]['bank']][stages[stage_num]['offset'] - bank_base:]
    else:
        stage_data = chr_bank[stages[stage_num]['bank']][stages[stage_num]['offset']:]

    #for i in range(0,32):
    #    print("%X"%(stage_data[i]))


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
    #print(stage_decompressed)

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

    # this needs to be reworked probably, but for now it is the live set of tiles in the pattern table in image form
    photo = []

    for i in range(0,256):
        photo.append(GetImage(chr_data, i))


    # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage


    stage = Image.new('RGB', (stage_width*16*2,stage_height*16*2))
    for i in range(stage_width * stage_height):
        ImageCopy(stage, photo[tile_map[0][stage_tile_info[i]]], (i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2, 16, 16)
        ImageCopy(stage, photo[tile_map[1][stage_tile_info[i]]], (i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2, 16, 16)
        ImageCopy(stage, photo[tile_map[2][stage_tile_info[i]]], (i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2 + 16, 16, 16)
        ImageCopy(stage, photo[tile_map[3][stage_tile_info[i]]], (i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2 + 16, 16, 16)

    canvas.config(scrollregion=(0, 0, stage_width*16*2, stage_height*16*2))

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
    print(stage_num_list[tkvar.get()])
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