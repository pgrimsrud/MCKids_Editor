from tkinter import *
from PIL import Image, ImageTk

file_name = "mckids.nes"

rom = open(file_name, "rb").read()
ines = rom[0:0x10]
rom = rom[0x10:]
chr_rom = rom[0x20000:0x20400]
stage_data = rom[0xE000:]
bank1 = rom[0x2000:]

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
            #print("byte 0x%X" % byte)
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
            #print("offset 0x%X" % offset)
            #print("length 0x%X" % length)
            for i in range(0,length):
                print("%d %d" % (len(result), offset))
                result.append(result[len(result)-offset])

    return result

tile_map_comp = []
tile_map_comp.append(rom[0x13061:])
tile_map_comp.append(rom[0x12E79:])
tile_map_comp.append(rom[0x1393D:])
tile_map_comp.append(rom[0x13605:])
#for i in range(0,50):
#    print("0x%0X" % tile_map_comp[i])
tile_map_raw = []
tile_map_raw.append(decompress(tile_map_comp[0][1:], tile_map_comp[0][0] >> 4, tile_map_comp[0][0] & 0xF))
tile_map_raw.append(decompress(tile_map_comp[1][1:], tile_map_comp[1][0] >> 4, tile_map_comp[1][0] & 0xF))
tile_map_raw.append(decompress(tile_map_comp[2][1:], tile_map_comp[2][0] >> 4, tile_map_comp[2][0] & 0xF))
tile_map_raw.append(decompress(tile_map_comp[3][1:], tile_map_comp[3][0] >> 4, tile_map_comp[3][0] & 0xF))
#print(tile_map_raw)
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

print(tile_map_raw[1])
#tile_map.append(tile_map_raw[5+tile_map_size:5+tile_map_size*2])
#tile_map.append(tile_map_raw[5+tile_map_size*2:5+tile_map_size*3])
#tile_map.append(tile_map_raw[5+tile_map_size*3:5+tile_map_size*4])

stage_width = stage_data[0]
stage_height = stage_data[1]

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

print(stage_tile_info)
print(spawn_count)
print(spawn_x[0])

palette = [(0,0,0),
           (100,100,100),
           (200,200,200),
           (255,255,255)]

def pattern_map(pattern):
    pixels = []
    for i in range(0,64):
        pixels.append((((pattern[(i>>3) + 8] >> (7 - (i & 7))) & 1) << 1) + (pattern[i>>3] >> (7 - (i & 7)) & 1))
    return pixels

#first = pattern_map(chr_rom[0x20:0x30])

window = Tk()
window.geometry("1024x" + str(stage_height*16*2 + 16))
#container = Frame(window)

#canvas = Canvas(window, width=32, height=32, borderwidth=0, highlightthickness=0)
#canvas2 = Canvas(window, width=32, height=32, borderwidth=0, highlightthickness=0)

def GetImage(num):
    pattern = pattern_map(chr_data[num*0x10:num*0x10+0x10])

    img = Image.new('RGB', (16,16))

    for i in range(0,8):
        for j in range(0,8):
            for k in range(0,2):
                for l in range(0,2):
                    img.putpixel((i*2+k,j*2+l), palette[pattern[(j<<3) + i]])

    return img


#photo = ImageTk.PhotoImage(img)

#canvas.create_image(0,0,anchor=NW,image=photo)
#canvas2.create_image(32,0,anchor=NE,image=photo)
#canvas.place(x=0, y=0, width=32, height=32)
#canvas2.place(x=32, y=0, width=32, height=32)

#scrollable_frame = Frame(window)

photo = []
canvas = []

for i in range(0,256):
    photo.append(ImageTk.PhotoImage(GetImage(i)))
    #canvas.append(Canvas(window, width=32, height=32, borderwidth=0, highlightthickness=0))
    #canvas[i].create_image(0,0,anchor=NW,image=photo[i])
    #canvas[i].place(x=(i&0xF)*32, y=(i>>4)*32, width=32, height=32)

#scrollbar = Scrollbar(window, orient=HORIZONTAL)
#scrollbar.pack(side=BOTTOM, fill=Y)
#stage_canvas = Canvas(window, width=16*stage_width*2, height=16*stage_height*2, borderwidth=0, highlightthickness=0, xscrollcommand=scrollbar.set)

#scrollable_frame = Frame(stage_canvas)

#scrollable_frame.bind("<Configure>", lambda e: stage_canvas.configure( scrollregion=stage_canvas.bbox("all")))

#stage_canvas.create_window((0, 0), window=scrollable_frame, anchor=NW)

#stage_canvas.configure(xscrollcommand=scrollbar.set)

scrollbar = Scrollbar(window, orient=HORIZONTAL)
scrollbar.place(x=0, y = stage_height*16*2, width = 1024)

stage_canvas = Canvas(window, width=512, height=16*stage_height*2, borderwidth=0, highlightthickness=0)
for i in range(stage_width * stage_height):
    #print("%d %d" % (len(tile_map[0]), stage_tile_info[i]))
    #print("%d %d %d %d" % (tile_map[0][0], tile_map[1][19], tile_map[2][19], tile_map[3][19]))
    stage_canvas.create_image((i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2, anchor=NW, image=photo[tile_map[0][stage_tile_info[i]]])
    stage_canvas.create_image((i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2, anchor=NW, image=photo[tile_map[1][stage_tile_info[i]]])
    stage_canvas.create_image((i % stage_width) * 16 * 2, (int(i / stage_width)) * 16 * 2 + 16, anchor=NW, image=photo[tile_map[2][stage_tile_info[i]]])
    stage_canvas.create_image((i % stage_width) * 16 * 2 + 16, (int(i / stage_width)) * 16 * 2 + 16, anchor=NW, image=photo[tile_map[3][stage_tile_info[i]]])

stage_canvas.place(x=0, y=0, width = stage_width*16*2, anchor=NW, height = stage_height*16*2)
scrollbar.config(command=stage_canvas.xview)

#container.pack()

#stage_canvas.place(x=0, y=0, width=stage_width*32, height=stage_height*32)

#stage_canvas.pack()
#scrollbar.pack(side="bottom", fill="y")
#scrollbar.config(command=stage_canvas.xview)

#stage_canvas.configure(scrollregion=stage_canvas.bbox("all"))
#container.place(x=0, y=0, width=512, height=stage_height*32)
#scrollable_frame.place(x=0, y=0, width=512, height=stage_height*32)
#scrollbar.place(x=0, y=stage_height*32, width=512)




#this works
#sc = Scrollbar(window, orient=HORIZONTAL)
#sc.place(x=0, y=16, width=100)
#
#cv = Canvas(window, width=16*20, height=16)
#for l in range(20):
#    cv.create_image(l*16, 16, image = photo[l])
#
#cv.place(x=0, y=0, width=16*20, anchor=NW, height=16)
#sc.config(command=cv.xview)

print(tile_map[0])
print(tile_map[1])
print(tile_map[2])
print(tile_map[3])

window.mainloop()