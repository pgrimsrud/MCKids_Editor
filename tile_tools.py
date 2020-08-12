import tkinter as tk
from tkinter import messagebox
from tkinter import *
from PIL import Image, ImageTk
from colors import rgba_to_rgb_palette


class TileTools:
    def __init__(self, parent, editor):
        self.selected_tile = 0x00

        self.tile_set_indexes = [tk.StringVar(), tk.StringVar(), tk.StringVar(), tk.StringVar()]

        self.canvas = parent
        self.editor = editor
        self.outer_frame = tk.Frame(self.canvas)
        self.frame = tk.Frame(self.outer_frame)
        self.button_photos = []
        self.current_level = 0
        self.canvas.create_window((0, 0), window=self.outer_frame, anchor="nw", tags="tile_tools_frame")
        self.xscrollbar = Scrollbar(self.canvas, orient=HORIZONTAL)
        #self.xscrollbar.place(x=0, y=500, width=500)
        self.xscrollbar.pack(side=tk.BOTTOM, fill="x")
        self.yscrollbar = Scrollbar(self.canvas, orient=VERTICAL)
        #self.yscrollbar.place(x=1024, y=0, height=500)
        self.yscrollbar.pack(side=tk.RIGHT, fill="y")

        inputs = tk.Frame(self.outer_frame)
        tk.Label(inputs, text="Tile sets:").pack(side=tk.LEFT, padx=10)
        for i in range(4):
            tk.Entry(inputs, width=4, textvariable=self.tile_set_indexes[i]).pack(side=tk.LEFT, padx=10)
        tk.Button(inputs, text="Update", command=self.update_tile_sets).pack(side=tk.LEFT, padx=10)
        inputs.pack(side=tk.TOP, pady=5)

        self.canvas.config(scrollregion=(0, 0, 450, 1125))
        self.canvas.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command=self.canvas.xview)
        self.yscrollbar.config(command=self.canvas.yview)

        self.frame.pack(side=tk.TOP)

    def update_tiles(self, current_level, rom_file):
        self.current_level = current_level
        self.__empty_tile_palette()
        level = rom_file.levels[current_level]

        for i in range(4):
            self.tile_set_indexes[i].set(level.tile_set_indices[i])

        for tile_index in range(256):
            button_img = Image.new('RGBA', (32, 32))
            p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[tile_index]]])
            level.get_tile(tile_index, rom_file).draw(button_img, 0, 0, p, level, int(tile_index / 64), rom_file)
            photo = ImageTk.PhotoImage(button_img)
            self.button_photos.append(photo)
            if self.selected_tile == tile_index:
                button_bg = "red"
            else:
                button_bg = "white"
            btn = tk.Button(self.frame, image=photo, borderwidth=4, bg=button_bg,
                            command=lambda index=tile_index: self.select_tile(index))
            btn.grid(row=int(tile_index / 10), column=tile_index % 10)

        #self.canvas.config(scrollregion=(0, 0, self.canvas.winfo_width(), self.canvas.winfo_height()))

    def select_tile(self, tile_index):
        self.selected_tile = tile_index
        # self.update_tiles(self.current_level)
        counter = 0
        for widget in self.frame.winfo_children():
            if counter == tile_index:
                widget['bg'] = "red"
            else:
                widget['bg'] = "white"
            counter += 1

    def __empty_tile_palette(self):
        for widget in self.frame.winfo_children():
            widget.destroy()
        for photo in self.button_photos:
            photo.__del__()
        self.button_photos = []

    def update_tile_sets(self):
        level = self.editor.rom_file.levels[self.editor.current_stage]
        for i in range(4):
            value = int(self.tile_set_indexes[i].get())
            if value > 44 or value < 1:
                messagebox.showerror("Out of range", "Tile set indexes needs to be between 1 and 43")
                return

        for i in range(4):
            level.tile_set_indices[i] = int(self.tile_set_indexes[i].get())
        self.update_tiles(self.editor.current_stage, self.editor.rom_file)
        self.editor.draw_stage()
