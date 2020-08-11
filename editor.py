import tkinter as tk
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
from rom import RomFile
from level import Level
from colors import rgba_to_rgb_palette
from tile_tools import TileTools


class Editor:
    SOLID_TYPES = [0x08, 0x01, 0x1B, 0x20, 0x25]
    SOLID_COLOR = (255, 0, 0, 100)

    def __init__(self, window):
        self.current_stage = 0
        self.show_grid = tk.BooleanVar()
        self.show_solids = tk.BooleanVar()
        self.show_paths = tk.BooleanVar()
        self.info_var = tk.StringVar()
        self.window = window
        self.ti = None
        self.stage_img = None
        self.overlay_img = None

        self.__setup_menu()

        # Add status bar that shows "info_var"
        status_bar = tk.Label(self.window, textvariable=self.info_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root_pane = PanedWindow(bd=4, relief="raised", width=1024)
        self.root_pane.pack(fill=BOTH, expand=1)

        # Add "Palette/Tools"
        self.tools_pane = PanedWindow(self.root_pane, bd=4, relief="raised")
        self.root_pane.add(self.tools_pane)
        self.tools_canvas = Canvas(self.tools_pane, width=1024, height=1024, borderwidth=0, highlightthickness=0)
        self.tools_pane.add(self.tools_canvas, width=475)

        # Add Canvas
        self.canvas_pane = PanedWindow(self.root_pane, bd=0, relief="raised", width=2024, height=1024)
        self.editor_canvas = Canvas(self.canvas_pane, width=1024, height=1024, borderwidth=0, highlightthickness=0)
        self.canvas_pane.add(self.editor_canvas)

        self.xscrollbar = Scrollbar(self.canvas_pane, orient=HORIZONTAL)
        #self.xscrollbar.place(x=0, y=1024, width=1024)
        self.xscrollbar.pack(side=tk.BOTTOM, fill="x")
        self.yscrollbar = Scrollbar(self.canvas_pane, orient=VERTICAL)
        #self.yscrollbar.place(x=1024, y=0, height=1024)
        self.yscrollbar.pack(side=tk.RIGHT, fill="y")
        self.root_pane.add(self.canvas_pane)


        self.tile_tools = TileTools(self.tools_canvas)

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
        view_menu.add_checkbutton(label="Show grid", onvalue=1, offvalue=0, variable=self.show_grid, command=self.draw_stage)
        view_menu.add_checkbutton(label="Show solids", onvalue=1, offvalue=0, variable=self.show_solids, command=self.draw_stage)
        view_menu.add_checkbutton(label="Show paths", onvalue=1, offvalue=0, variable=self.show_paths, command=self.draw_stage)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

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

        self.tile_tools.update_tiles(stage_index)
        self.draw_stage()

    def redraw(self):
        complete_img = Image.alpha_composite(self.stage_img, self.overlay_img)
        self.ti = ImageTk.PhotoImage(complete_img)
        self.editor_canvas.create_image(0, 0, anchor=NW, image=self.ti, tags="img")

    def draw_tile(self, x, y):
        level = RomFile.levels[self.current_stage]
        i = y * level.width + x
        p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[i]]]])
        level.get_tile_at(i).draw(self.stage_img, x * 32, y * 32, p, level, int(level.tile_map[i] / 64))
        draw_context = ImageDraw.Draw(self.overlay_img)
        self.__clear_tile(draw_context, x, y)

        if self.show_solids.get() == 1:
            self.__draw_tile_solids(draw_context, i, level)
        if self.show_grid.get() == 1:
            self.__draw_tile_grid(draw_context, x, y)
        if self.show_paths.get() == 1:
            self.__draw_tile_paths(draw_context, i, level)

        self.redraw()

    def __clear_tile(self, draw_context, x, y):
        draw_context.rectangle((x * 32, y * 32, x * 32 + 32, y * 32 + 32), (0, 0, 0, 0))

    def __draw_tile_grid(self, img, x, y):
        img.line([(x * 32, y * 32), (x * 32 + 32, y * 32)], fill=(255, 255, 255, 100))
        img.line([(x * 32, y * 32), (x * 32, y * 32 + 32)], fill=(255, 255, 255, 100))

    def __draw_grid(self, img):
        level = RomFile.levels[self.current_stage]
        for x in range(1, level.width):
            img.line([(x * 32, 0), (x * 32, level.height * 32)], fill=(255, 255, 255, 100))
        for y in range(1, level.height):
            img.line([(0, y * 32), (level.width * 32, y * 32)], fill=(255, 255, 255, 100))

    def __draw_solids(self, img):
        level = RomFile.levels[self.current_stage]
        for i in range(level.width * level.height):
            self.__draw_tile_solids(img, i, level)

    def __draw_tile_solids(self, img, index, level):
        tile_type = level.get_tile_at(index).tile_type
        x = (index % level.width) * 16 * 2
        y = int(index / level.width) * 16 * 2
        if tile_type in Editor.SOLID_TYPES:
            img.rectangle([x, y, x + 32, y + 32], Editor.SOLID_COLOR)
        if tile_type == 0x02 or tile_type == 0x18 or tile_type == 0x21:
            img.polygon([(x, y + 32), (x + 32, y), (x + 32, y + 32)], Editor.SOLID_COLOR)
        if tile_type == 0x03 or tile_type == 0x17 or tile_type == 0x22:
            img.polygon([(x, y), (x, y + 32), (x + 32, y + 32)], Editor.SOLID_COLOR)
        if tile_type == 0x04 or tile_type == 0x16 or tile_type == 0x23:
            img.polygon([(x, y), (x + 32, y), (x + 32, y + 32)], Editor.SOLID_COLOR)
        if tile_type == 0x05 or tile_type == 0x15 or tile_type == 0x24:
            img.polygon([(x, y), (x + 32, y), (x, y + 32)], Editor.SOLID_COLOR)

        if tile_type == 0x09:
            img.polygon([(x, y + 32), (x + 32, y + 32), (x + 32, y + 16)], Editor.SOLID_COLOR)
        if tile_type == 0x0A:
            img.polygon([(x, y + 16), (x + 32, y), (x + 32, y + 32), (x, y + 32)], Editor.SOLID_COLOR)
        if tile_type == 0x0B:
            img.polygon([(x, y), (x + 32, y + 16), (x + 32, y + 32), (x, y + 32)], Editor.SOLID_COLOR)
        if tile_type == 0x0C:
            img.polygon([(x, y + 16), (x + 32, y + 32), (x, y + 32)], Editor.SOLID_COLOR)

    def __draw_paths(self, img):
        level = RomFile.levels[self.current_stage]
        for i in range(level.width * level.height):
            self.__draw_tile_paths(img, i, level)

    def __draw_tile_paths(self, img, index, level):
        tile_type = level.get_tile_at(index).tile_type
        x = (index % level.width) * 16 * 2
        y = int(index / level.width) * 16 * 2
        if tile_type == 0x70:
            img.line([(x, y + 32), (x + 16, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x71:
            img.line([(x + 32, y), (x + 16, y + 16), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x72:
            img.line([(x, y + 16), (x + 16, y + 16), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x73:
            img.line([(x, y), (x + 16, y + 16), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x74:
            img.line([(x + 16, y), (x + 16, y + 16), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x75:
            img.line([(x, y), (x + 16, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x76:
            img.line([(x, y + 16), (x + 16, y + 16), (x + 32, y)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x77:
            img.line([(x + 16, y), (x + 16, y + 16), (x, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x78:
            img.line([(x, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x79:
            img.line([(x + 16, y), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x7A:
            img.line([(x, y), (x + 32, y + 32)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x7B:
            img.line([(x, y + 32), (x + 32, y)], fill=(0, 255, 0, 200), width=4)
        if tile_type == 0x7C:
            img.line([(x, y + 16), (x + 32, y + 16)], fill=(0, 255, 0, 200), width=4)
            img.line([(x + 16, y), (x + 16, y + 32)], fill=(0, 255, 0, 200), width=4)

    def draw_sprites(self):
        level = RomFile.levels[self.current_stage]

        for i in range(0, len(level.spawn_points)):
            sprite = RomFile.sprites[level.spawn_points[i].sprite_index]
            for j in range(sprite.width * sprite.height):
                x = level.spawn_points[i].x * 16 * 2 + (j % sprite.width) * 8 * 2
                y = level.spawn_points[i].y * 16 * 2 + int(j / sprite.width) * 8 * 2 - ((sprite.height - 2) * 16)
                RomFile.get_sprite_chr(sprite.chr_pointers[j], sprite.palette_index, level).draw(self.stage_img, x, y, 0)

    def draw_stage(self):  # DRAW THE STAGE:
        level = RomFile.levels[self.current_stage]

        # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
        self.stage_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
        self.overlay_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
        overlay_draw = ImageDraw.Draw(self.overlay_img)

        for i in range(level.width * level.height):
            x = (i % level.width) * 16 * 2
            y = int(i / level.width) * 16 * 2
            p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[i]]]])
            level.get_tile_at(i).draw(self.stage_img, x, y, p, level, int(level.tile_map[i] / 64))

        if self.show_solids.get() == 1:
            self.__draw_solids(overlay_draw)
        if self.show_grid.get() == 1:
            self.__draw_grid(overlay_draw)
        if self.show_paths.get() == 1:
            self.__draw_paths(overlay_draw)

        self.draw_sprites()

        complete_img = Image.alpha_composite(self.stage_img, self.overlay_img)
        self.ti = ImageTk.PhotoImage(complete_img)

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
        # paint_with_index = 0x5B  # throwable block in stage 1-1
        paint_with_index = self.tile_tools.selected_tile
        level = RomFile.levels[self.current_stage]
        index = level.width * y + x
        if level.tile_map[index] != paint_with_index:
            level.tile_map[index] = paint_with_index
            self.draw_tile(x, y)
            self.draw_sprites()
            self.redraw()
            # self.draw_stage()
