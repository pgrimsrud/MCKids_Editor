from tkinter import *
from PIL import Image, ImageTk

file_name = "mckids.nes"

rom = open(file_name, "rb").read()
ines = rom[0:0x10]
rom = rom[0x10:]
chr_rom = rom[0x20000:0x20400]

# this is a magic number and we'll need to figure out how the game points to the leves
# and do that instead
stage_data = rom[0xE000:]

# need to do general bank mapping instead
bank1 = rom[0x2000:]

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

# these are magic numbers for stage 1
# will need to figure out how the stage game does this instead
tile_map_comp = []
tile_map_comp.append(rom[0x13061:])
tile_map_comp.append(rom[0x12E79:])
tile_map_comp.append(rom[0x1393D:])
tile_map_comp.append(rom[0x13605:])

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
chr_map = bank1[0x111:]

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

# need to figure out how the game does this
palette = [(0,0,0),
           (100,100,100),
           (200,200,200),
           (255,255,255)]

# haven't even started on attribute tables

#this converts the 16 byte pattern table data to an array of color indexes 0-3 for the 8x8 tile
def pattern_map(pattern):
    pixels = []
    for i in range(0,64):
        pixels.append((((pattern[(i>>3) + 8] >> (7 - (i & 7))) & 1) << 1) + (pattern[i>>3] >> (7 - (i & 7)) & 1))
    return pixels

# the main window
window = Tk()
window.geometry("1024x" + str(stage_height*16*2 + 16))

# this creates an image for the tile from the pattern table and palette
def GetImage(num):
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

# this needs to be reworked probably, but for now it is the live set of tiles in the pattern table in image form
photo = []

for i in range(0,256):
    photo.append(GetImage(i))


# use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
canvas = []

scrollbar = Scrollbar(window, orient=HORIZONTAL)
scrollbar.place(x=0, y = stage_height*16*2, width = 1024)

stage_canvas = Canvas(window, width=512, height=16*stage_height*2, borderwidth=0, highlightthickness=0)
stage = Image.new('RGB', (stage_width*16*2,stage_height*16*2))
for i in range(stage_width * stage_height):
    ImageCopy(stage, photo[tile_map[0][stage_tile_info[i]]], (i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2, 16, 16)
    ImageCopy(stage, photo[tile_map[1][stage_tile_info[i]]], (i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2, 16, 16)
    ImageCopy(stage, photo[tile_map[2][stage_tile_info[i]]], (i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2 + 16, 16, 16)
    ImageCopy(stage, photo[tile_map[3][stage_tile_info[i]]], (i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2 + 16, 16, 16)

pi = ImageTk.PhotoImage(stage)
stage_canvas.create_image(0, 0, anchor=NW, image=pi)
stage_canvas.place(x=0, y=0, width = stage_width*16*2, anchor=NW, height = stage_height*16*2)
scrollbar.config(command=stage_canvas.xview)

window.mainloop()