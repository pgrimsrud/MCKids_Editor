import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
from rom import RomFile
from level import Level
from colors import rgba_to_rgb_palette
from time import sleep

class Editor:
    SOLID_TYPES = [0x08, 0x01, 0x1B, 0x20, 0x25]

    def __init__(self, window):
        self.current_stage = 0
        self.show_grid = tk.BooleanVar()
        self.show_solids = tk.BooleanVar()
        self.show_paths = tk.BooleanVar()
        self.info_var = tk.StringVar()
        self.window = window
        self.ti = None

        self.__setup_menu()

        self.root_pane = PanedWindow(bd=4, relief="raised")
        self.root_pane.pack(fill=BOTH, expand=1)

        # Add Canvas
        self.editor_canvas = Canvas(self.root_pane, width=1024, height=1024, borderwidth=0, highlightthickness=0)
        self.root_pane.add(self.editor_canvas)

        self.xscrollbar = Scrollbar(self.window, orient=HORIZONTAL)
        self.xscrollbar.place(x=0, y=1024, width=1024)
        self.yscrollbar = Scrollbar(self.window, orient=VERTICAL)
        self.yscrollbar.place(x=1024, y=0, height=1024)

        # Add "Palette/Tools"
        # Add status bar that shows "info_var"
        statusbar = tk.Label(self.root_pane, textvariable=self.info_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        statusbar.pack(side=tk.BOTTOM, fill=tk.X)
        # ......

        self.editor_canvas.bind('<Motion>', self.update_info_label)
        self.editor_canvas.bind('<Button-1>', self.canvas_clicked)
        self.editor_canvas.bind('<B1-Motion>', self.canvas_clicked)

        self.load_stage(0)

    def __setup_menu(self):
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)

        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Save level", command=self.save_level_button_clicked)
        file_menu.add_command(label="Write ROM file", command=self.save_rom_button_clicked)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        level_menu = Menu(self.menu_bar, tearoff=0)
        for i in range(0x5D):
            level_menu.add_command(label=f'Level {i}', command=lambda index=i: self.load_stage(index))
        self.menu_bar.add_cascade(label="Level", menu=level_menu)

        view_menu = Menu(self.menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Show grid", onvalue=1, offvalue=0, variable=self.show_grid)
        view_menu.add_checkbutton(label="Show solids", onvalue=1, offvalue=0, variable=self.show_solids)
        view_menu.add_checkbutton(label="Show paths", onvalue=1, offvalue=0, variable=self.show_paths)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

    def go_to_level(self):
        i = 0  # debug this to find how we can determine the level
        return

    def load_stage_str(self, stage_str):
        self.load_stage(int(stage_str))

    def load_stage(self, stage_index):
        self.current_stage = stage_index
        if RomFile.levels[self.current_stage] is None:
            # print("loading bank 0x%X address 0x%X" %(stages[stage_num]['bank'], stages[stage_num]['offset']))
            if RomFile.stage_pointers[self.current_stage]['bank'] < 0xD:
                stage_data = RomFile.banks[RomFile.stage_pointers[self.current_stage]['bank']][
                             RomFile.stage_pointers[self.current_stage]['offset'] - RomFile.BANK_BASE:]
            else:
                stage_data = RomFile.chr_banks[RomFile.stage_pointers[self.current_stage]['bank']][
                             RomFile.stage_pointers[self.current_stage]['offset']:]

            RomFile.levels[self.current_stage] = Level.load_level(self.current_stage, stage_data)
        self.draw_stage()

    def draw_stage(self):  # DRAW THE STAGE:
        level = RomFile.levels[self.current_stage]

        rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[0]]]])
        level.get_tile_at(0)
        # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
        stage_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
        if self.show_grid.get() == 1:
            overlay_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
            overlay_draw = ImageDraw.Draw(overlay_img)

        for i in range(level.width * level.height):
            x = (i % level.width) * 16 * 2
            y = int(i / level.width) * 16 * 2
            p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[i]]]])
            level.get_tile_at(i).draw(stage_img, x, y, p, level, int(level.tile_map[i] / 64))

            if self.show_grid.get() == 1:
                tile_type = level.get_tile_at(i).tile_type
                solid_color = (255, 0, 0, 200)
                if tile_type in Editor.SOLID_TYPES:
                    overlay_draw.rectangle([x, y, x + 32, y + 32], solid_color)
                if tile_type == 0x02 or tile_type == 0x18 or tile_type == 0x21:
                    overlay_draw.polygon([(x, y + 32), (x + 32, y), (x + 32, y + 32)], solid_color)
                if tile_type == 0x03 or tile_type == 0x17 or tile_type == 0x22:
                    overlay_draw.polygon([(x, y), (x, y + 32), (x + 32, y + 32)], solid_color)
                if tile_type == 0x04 or tile_type == 0x16 or tile_type == 0x23:
                    overlay_draw.polygon([(x, y), (x + 32, y), (x + 32, y + 32)], solid_color)
                if tile_type == 0x05 or tile_type == 0x15 or tile_type == 0x24:
                    overlay_draw.polygon([(x, y), (x + 32, y), (x, y + 32)], solid_color)

                if tile_type == 0x09:
                    overlay_draw.polygon([(x, y + 32), (x + 32, y + 32), (x + 32, y + 16)], solid_color)
                if tile_type == 0x0A:
                    overlay_draw.polygon([(x, y + 16), (x + 32, y), (x + 32, y + 32), (x, y + 32)], solid_color)
                if tile_type == 0x0B:
                    overlay_draw.polygon([(x, y), (x + 32, y + 16), (x + 32, y + 32), (x, y + 32)], solid_color)
                if tile_type == 0x0C:
                    overlay_draw.polygon([(x, y + 16), (x + 32, y + 32), (x, y + 32)], solid_color)

                if tile_type == 0x70:
                    overlay_draw.line([(x, y + 32), (x + 16, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x71:
                    overlay_draw.line([(x + 32, y), (x + 16, y + 16), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x72:
                    overlay_draw.line([(x, y + 16), (x + 16, y + 16), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x73:
                    overlay_draw.line([(x, y), (x + 16, y + 16), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x74:
                    overlay_draw.line([(x + 16, y), (x + 16, y + 16), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x75:
                    overlay_draw.line([(x, y), (x + 16, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x76:
                    overlay_draw.line([(x, y + 16), (x + 16, y + 16), (x + 32, y)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x77:
                    overlay_draw.line([(x + 16, y), (x + 16, y + 16), (x, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x78:
                    overlay_draw.line([(x, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x79:
                    overlay_draw.line([(x + 16, y), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x7A:
                    overlay_draw.line([(x, y), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x7B:
                    overlay_draw.line([(x, y + 32), (x + 32, y)], fill=(0, 255, 0, 200), width=4)
                if tile_type == 0x7C:
                    overlay_draw.line([(x, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
                    overlay_draw.line([(x + 16, y), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)

                overlay_draw.rectangle([x, y, x + 32, y + 32], outline=(255, 255, 255, 100))

        for i in range(0, len(level.spawn_points)):
            sprite = RomFile.sprites[level.spawn_points[i].sprite_index]
            for j in range(sprite.width * sprite.height):
                x = level.spawn_points[i].x * 16 * 2 + (j % sprite.width) * 8 * 2
                y = level.spawn_points[i].y * 16 * 2 + int(j / sprite.width) * 8 * 2 - ((sprite.height - 2) * 16)
                RomFile.get_sprite_chr(sprite.chr_pointers[j], sprite.palette_index, level).draw(stage_img, x, y, 0)

        if self.show_grid.get() == 1:
            stage_img = Image.alpha_composite(stage_img, overlay_img)
        self.ti = ImageTk.PhotoImage(stage_img)

        self.editor_canvas.config(scrollregion=(0, 0, level.width * 16 * 2, level.height * 16 * 2))
        self.editor_canvas.create_image(0, 0, anchor=NW, image=self.ti, tags="img")
        self.editor_canvas.place(x=0, y=0, anchor=NW)
        self.editor_canvas.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command=self.editor_canvas.xview)
        self.yscrollbar.config(command=self.editor_canvas.yview)

    def change_stage_dropdown(self, *args):
        self.load_stage(self.editor_canvas, self.current_stage)

    def update_info_label(self, event):
        level = RomFile.levels[self.current_stage]
        canvas = event.widget
        x = (int)(canvas.canvasx(event.x) / 32)
        y = (int)(canvas.canvasy(event.y) / 32)
        index = level.width * y + x
        if len(level.tile_map) > index:
            type = level.get_tile_at(index).tile_type
            tile_set_index = level.tile_map[index]
            self.info_var.set(f'Tile type: 0x{format(type, "02x")}, ' +
                         f' Tile set index: 0x{format(tile_set_index, "02x")},' +
                         f' Data index: 0x{format(index, "04x")}, ' +
                         f' X: {x}, Y: {y}')
        else:
            self.info_var.set(f'Out of range: {index}')

    def save_level_button_clicked(self):
        RomFile.save_level(self.current_stage)

    def save_rom_button_clicked(self):
        filename = filedialog.asksaveasfilename(defaultextension=".nes")
        if len(filename) > 0:
            RomFile.write_rom(filename)

    def canvas_clicked(self, event):
        canvas = event.widget
        x = int(canvas.canvasx(event.x) / 32)
        y = int(canvas.canvasy(event.y) / 32)
        self.paint_tile(canvas, x, y)

    def paint_tile(self, canvas, x, y):
        paint_with_index = 0x5B  # throwable block in stage 1-1
        level = RomFile.levels[self.current_stage]
        index = level.width * y + x
        if level.tile_map[index] != paint_with_index:
            level.tile_map[index] = paint_with_index
            self.draw_stage()
