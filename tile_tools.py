import tkinter as tk
from PIL import Image, ImageTk
from rom import RomFile
from colors import rgba_to_rgb_palette


class TileTools:
    def __init__(self, parent):
        self.selected_tile = 0x00
        self.tile_palette = tk.Frame(parent)
        self.button_photos = []
        self.current_level = 0
        self.tile_palette.pack(side=tk.LEFT)

    def update_tiles(self, current_level):
        self.current_level = current_level
        self.__empty_tile_palette()
        level = RomFile.levels[current_level]
        for tile_index in range(256):
            button_img = Image.new('RGBA', (32, 32))
            p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[tile_index]]])
            level.get_tile(tile_index).draw(button_img, 0, 0, p, level, int(tile_index / 64))
            photo = ImageTk.PhotoImage(button_img)
            self.button_photos.append(photo)
            if self.selected_tile == tile_index:
                button_bg = "red"
            else:
                button_bg = "white"
            btn = tk.Button(self.tile_palette, image=photo, borderwidth=4, bg=button_bg,
                            command=lambda index=tile_index: self.select_tile(index))
            btn.grid(row=int(tile_index / 10), column=tile_index % 10)

    def select_tile(self, tile_index):
        self.selected_tile = tile_index
        # self.update_tiles(self.current_level)
        counter = 0
        for widget in self.tile_palette.winfo_children():
            if counter == tile_index:
                widget['bg'] = "red"
            else:
                widget['bg'] = "white"
            counter += 1


    def __empty_tile_palette(self):
        for widget in self.tile_palette.winfo_children():
            widget.destroy()
        for photo in self.button_photos:
            photo.__del__()
        self.button_photos = []
