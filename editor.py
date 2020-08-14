import tkinter as tk
from tkinter import messagebox
from tkinter import *
from tkinter import filedialog
from PIL import Image, ImageDraw, ImageTk
import pickle
from rom import RomFile
from level import Level
from colors import rgba_to_rgb_palette
from tile_tools import TileTools
from resize_tool import ResizeTool
from sprite_tools import SpriteTools
from level_properties import LevelProperties
import webbrowser

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
        self.rom_file = None
        self.project = None
        self.next_click_callback = None

        self.__setup_menu()

        # Add status bar that shows "info_var"
        status_bar = tk.Label(self.window, textvariable=self.info_var, bd=1, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.root_pane = PanedWindow(bd=4, relief="raised", width=1024)
        self.root_pane.pack(fill=BOTH, expand=1)

        # Add "Palette/Tools"
        self.tools_pane = PanedWindow(self.root_pane, bd=4, relief="raised", orient=VERTICAL)
        self.root_pane.add(self.tools_pane)
        self.tools_canvas = Canvas(self.tools_pane, width=1024, height=1024, borderwidth=0, highlightthickness=0)
        self.sprite_canvas = Canvas(self.tools_pane, highlightthickness=0)
        self.property_canvas = Canvas(self.tools_pane, highlightthickness=0)
        self.tools_pane.add(self.property_canvas)
        self.tools_pane.add(self.sprite_canvas)
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

        self.sprite_tools = SpriteTools(self.sprite_canvas, self)
        self.tile_tools = TileTools(self.tools_canvas, self)
        self.level_properties = LevelProperties(self.property_canvas, self)

        self.editor_canvas.bind('<Motion>', self.update_info_label)
        self.editor_canvas.bind('<Button-1>', self.canvas_clicked)
        self.editor_canvas.bind('<B1-Motion>', self.canvas_clicked)

    def __setup_menu(self):
        self.menu_bar = Menu(self.window)
        self.window.config(menu=self.menu_bar)

        file_menu = Menu(self.menu_bar, tearoff=0)
        file_menu.add_command(label="Open Project", command=self.open_project_button_clicked)
        file_menu.add_command(label="Save Project", command=self.save_project_button_clicked)
        file_menu.add_command(label="Save Project As...", command=self.save_project_as_button_clicked)
        file_menu.add_command(label="Save level", command=self.save_level_button_clicked)
        file_menu.add_command(label="Open ROM file", command=self.open_rom_button_clicked)
        file_menu.add_command(label="Save ROM file", command=self.save_rom_button_clicked)
        file_menu.add_separator()
        file_menu.add_command(label="Export level", command=self.export_level_clicked)
        file_menu.add_command(label="Import level", command=self.import_level_clicked)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.window.quit)
        self.menu_bar.add_cascade(label="File", menu=file_menu)

        edit_menu = Menu(self.menu_bar, tearoff=0)
        edit_menu.add_command(label="Resize level", command=self.resize_stage_clicked)
        edit_menu.add_command(label="Clear level", command=self.clear_stage_clicked)
        self.menu_bar.add_cascade(label="Edit", menu=edit_menu)

        self.level_menu = Menu(self.menu_bar, tearoff=0)
        for i in range(0x5D):
            self.level_menu.add_command(label=f'Level {i}', command=lambda index=i: self.load_stage(index))
        self.menu_bar.add_cascade(label="Level", menu=self.level_menu)

        view_menu = Menu(self.menu_bar, tearoff=0)
        view_menu.add_checkbutton(label="Show grid", onvalue=1, offvalue=0, variable=self.show_grid, command=self.draw_stage)
        view_menu.add_checkbutton(label="Show solids", onvalue=1, offvalue=0, variable=self.show_solids, command=self.draw_stage)
        view_menu.add_checkbutton(label="Show paths", onvalue=1, offvalue=0, variable=self.show_paths, command=self.draw_stage)
        self.menu_bar.add_cascade(label="View", menu=view_menu)

        help_menu = Menu(self.menu_bar, tearoff=0)
        help_menu.add_command(label="About", command=self.about_button_clicked)
        self.menu_bar.add_cascade(label="Help", menu=help_menu)

    def link_clicked(self, event):
        webbrowser.open_new(event.widget.cget("text"))

    def about_button_clicked(self):
        about_window = tk.Toplevel(self.window)
        about_window.title("About")
        about_window.resizable(False, False)
        #about_window.geometry("512x480")
        label1 = Label(about_window, borderwidth=8, text="M.C. Kids Editor")
        label2 = Label(about_window, borderwidth=8, text="Version X.X")
        label3 = Label(about_window, borderwidth=8, text="Written by:")
        label4 = Label(about_window, borderwidth=8, text="Phillip Grimsrud", justify=LEFT)
        label5 = Label(about_window, borderwidth=8, text="http://twitch.tv/link_7777", justify=LEFT, fg="blue", cursor="hand2")
        label6 = Label(about_window, borderwidth=8, text="Andreas Bernhardsen")
        label7 = Label(about_window, borderwidth=8, text="http://twitch.tv/schaaa", justify=LEFT, fg="blue", cursor="hand2")
        label8 = Label(about_window, borderwidth=8, text="https://github.com/pgrimsrud/MCKids_Editor", justify=LEFT, fg="blue", cursor="hand2")
        label1.grid(row=0, column=0, columnspan=2)
        label2.grid(row=1, column=0, columnspan=2)
        label3.grid(row=2, column=0, columnspan=2)
        label4.grid(row=3, column=0, columnspan=1)
        label5.grid(row=3, column=1, columnspan=1)
        label6.grid(row=4, column=0, columnspan=1)
        label7.grid(row=4, column=1, columnspan=1)
        label8.grid(row=5, column=0, columnspan=2)
        label5.bind('<Button-1>', self.link_clicked)
        label7.bind('<Button-1>', self.link_clicked)
        label8.bind('<Button-1>', self.link_clicked)
        about_window.mainloop()

    def open_project_button_clicked(self):
        filename = filedialog.askopenfilename(defaultextension=".mcp", filetypes=[("M.C. Kids Project", "*.mcp"), ("All Files", "*")])
        if len(filename):
            self.project = filename
            project_data = open(filename, "rb").read()
            self.rom_file = pickle.loads(project_data)
            self.load_stage(0)

    def save_project_button_clicked(self):
        if self.project != None:
            #self.rom_file.save_project(self.project)
            project_data = pickle.dumps(self.rom_file)
            with open(self.project, "wb") as fp:
                fp.write(bytearray(project_data))
        else:
            self.save_project_as_button_clicked()

    def save_project_as_button_clicked(self):
        if self.rom_file != None:
            filename = filedialog.asksaveasfilename(defaultextension=".mcp", initialfile=".mcp", filetypes=[("M.C. Kids Project", "*.mcp"), ("All Files", "*")])
            if len(filename):
                self.project = filename
                self.save_project_button_clicked()

    def open_rom_button_clicked(self):
        filename = filedialog.askopenfilename(defaultextension=".nes", filetypes=[("Nintendo Entertainment System ROM", "*.nes"), ("All Files", "*")])
        if len(filename):
            self.rom_file = RomFile(filename, 0)
            self.update_level_names()
            self.load_stage(0)

    def update_level_names(self):
        item_count = self.level_menu.index("end")
        for i in range(item_count + 1):
            level_index = self.rom_file.level_index_lookup[i]
            if i in [7, 92]:
                self.level_menu.entryconfigure(i, state="disabled")
            if level_index != -1:
                self.level_menu.entryconfigure(i, label=f'Level {i}: {self.rom_file.level_names[level_index]}')

    def resize_stage_clicked(self):
        ResizeTool(self.window, self.rom_file.levels[self.current_stage], self.draw_stage)

    def clear_stage_clicked(self):
        for i in range(len(self.rom_file.levels[self.current_stage].tile_map)):
            self.rom_file.levels[self.current_stage].tile_map[i] = self.tile_tools.selected_tile
        self.draw_stage()

    def export_level_clicked(self):
        filename = filedialog.asksaveasfilename(defaultextension=".mcl", initialfile=".mcl", filetypes=[("M.C. Kids Level", "*.mcl"), ("All Files", "*")])
        if len(filename):
            with open(filename, "wb") as fp:
                fp.write(bytearray(self.rom_file.levels[self.current_stage].compress()))

    def import_level_clicked(self):
        filename = filedialog.askopenfilename(defaultextension=".mcl", filetypes=[("M.C. Kids Level", "*.mcl"), ("All Files", "*")])
        if len(filename):
            with open(filename, "rb") as fp:
                data = fp.read()
                self.rom_file.levels[self.current_stage] = Level.load_level(self.current_stage, data, self.rom_file)
                self.draw_stage()

    def deselect(self):
        self.tile_tools.select_tile(None)

    def load_stage(self, stage_index):
        self.current_stage = stage_index
        if self.rom_file.levels[self.current_stage] is None:
            if self.rom_file.stage_pointers[self.current_stage]['bank'] < 0xD:
                stage_data = self.rom_file.banks[self.rom_file.stage_pointers[self.current_stage]['bank']][
                             self.rom_file.stage_pointers[self.current_stage]['offset'] - RomFile.BANK_BASE:]
            else:
                stage_data = self.rom_file.chr_banks[self.rom_file.stage_pointers[self.current_stage]['bank']][
                             self.rom_file.stage_pointers[self.current_stage]['offset']:]

            self.rom_file.levels[self.current_stage] = Level.load_level(self.current_stage, stage_data, self.rom_file)

        self.tile_tools.update_tiles(stage_index, self.rom_file)
        self.sprite_tools.load_from_level(self.rom_file.levels[self.current_stage])
        self.level_properties.change_level(stage_index)
        self.draw_stage()

    def redraw(self, box):
        complete_img = Image.alpha_composite(self.stage_img, self.overlay_img)
        self.ti.paste(complete_img, box)
        # self.editor_canvas.create_image(0, 0, anchor=NW, image=self.ti, tags="img")

    def draw_tile(self, x, y):
        level = self.rom_file.levels[self.current_stage]
        i = y * level.width + x
        p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[i]]]])
        level.get_tile_at(i, self.rom_file).draw(self.stage_img, x * 32, y * 32, p, level, int(level.tile_map[i] / 64), self.rom_file)
        draw_context = ImageDraw.Draw(self.overlay_img)
        self.__clear_tile(draw_context, x, y)

        if self.show_solids.get() == 1:
            self.__draw_tile_solids(draw_context, i, level)
        if self.show_grid.get() == 1:
            self.__draw_tile_grid(draw_context, x, y)
        if self.show_paths.get() == 1:
            self.__draw_tile_paths(draw_context, i, level)

    def __clear_tile(self, draw_context, x, y):
        draw_context.rectangle((x * 32, y * 32, x * 32 + 32, y * 32 + 32), (0, 0, 0, 0))

    def __draw_tile_grid(self, img, x, y):
        img.line([(x * 32, y * 32), (x * 32 + 32, y * 32)], fill=(255, 255, 255, 100))
        img.line([(x * 32, y * 32), (x * 32, y * 32 + 32)], fill=(255, 255, 255, 100))

    def __draw_grid(self, img):
        level = self.rom_file.levels[self.current_stage]
        for x in range(1, level.width):
            img.line([(x * 32, 0), (x * 32, level.height * 32)], fill=(255, 255, 255, 100))
        for y in range(1, level.height):
            img.line([(0, y * 32), (level.width * 32, y * 32)], fill=(255, 255, 255, 100))

    def __draw_solids(self, img):
        level = self.rom_file.levels[self.current_stage]
        for i in range(level.width * level.height):
            self.__draw_tile_solids(img, i, level)

    def __draw_tile_solids(self, img, index, level):
        tile_type = level.get_tile_at(index, self.rom_file).tile_type
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
        level = self.rom_file.levels[self.current_stage]
        for i in range(level.width * level.height):
            self.__draw_tile_paths(img, i, level)

    def __draw_tile_paths(self, img, index, level):
        tile_type = level.get_tile_at(index, self.rom_file).tile_type
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
        level = self.rom_file.levels[self.current_stage]

        for i in range(0, len(level.spawn_points)):
            sprite = self.rom_file.get_sprite(level.spawn_points[i].sprite_index)
            for j in range(sprite.width * sprite.height):
                x = level.spawn_points[i].x * 16 * 2 + (j % sprite.width) * 8 * 2
                y = level.spawn_points[i].y * 16 * 2 + int(j / sprite.width) * 8 * 2 - ((sprite.height - 2) * 16)
                self.rom_file.get_sprite_chr(sprite.chr_pointers[j], sprite.palette_index, level).draw(self.stage_img, x, y, 0)
            if i == self.sprite_tools.index:
                stage_draw = ImageDraw.Draw(self.stage_img)
                x = level.spawn_points[i].x * 32
                y = level.spawn_points[i].y * 32 - ((sprite.height - 2) * 16)
                stage_draw.rectangle(((x, y), (x + sprite.width * 16, y + sprite.height * 16)), outline="red", width=2)

    def draw_kid(self):
        x = self.rom_file.start_pos_x[self.current_stage] * 32
        y = self.rom_file.start_pos_y[self.current_stage] * 32 - 64
        stage_draw = ImageDraw.Draw(self.stage_img)
        stage_draw.rectangle(((x, y), (x + 32, y + 64)), outline="green", width=2)

    def draw_stage(self):  # DRAW THE STAGE:
        level = self.rom_file.levels[self.current_stage]

        # use the decompressed tiles from the stage, the tile map, and the pattern table to create an image of the stage
        self.stage_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
        self.overlay_img = Image.new('RGBA', (level.width * 16 * 2, level.height * 16 * 2))
        overlay_draw = ImageDraw.Draw(self.overlay_img)

        for i in range(level.width * level.height):
            x = (i % level.width) * 16 * 2
            y = int(i / level.width) * 16 * 2
            p = rgba_to_rgb_palette(level.palette[level.attribute_lookup[level.tile_palette_map[level.tile_map[i]]]])
            level.get_tile_at(i, self.rom_file).draw(self.stage_img, x, y, p, level, int(level.tile_map[i] / 64), self.rom_file)

        if self.show_solids.get() == 1:
            self.__draw_solids(overlay_draw)
        if self.show_grid.get() == 1:
            self.__draw_grid(overlay_draw)
        if self.show_paths.get() == 1:
            self.__draw_paths(overlay_draw)

        self.draw_sprites()
        self.draw_kid()

        complete_img = Image.alpha_composite(self.stage_img, self.overlay_img)
        self.ti = ImageTk.PhotoImage(complete_img)

        self.editor_canvas.config(scrollregion=(0, 0, level.width * 16 * 2, level.height * 16 * 2))
        self.editor_canvas.create_image(0, 0, anchor=NW, image=self.ti, tags="img")
        self.editor_canvas.place(x=0, y=0, anchor=NW)
        self.editor_canvas.config(xscrollcommand=self.xscrollbar.set, yscrollcommand=self.yscrollbar.set)
        self.xscrollbar.config(command=self.editor_canvas.xview)
        self.yscrollbar.config(command=self.editor_canvas.yview)

    def update_info_label(self, event):
        if self.rom_file != None:
            level = self.rom_file.levels[self.current_stage]
            canvas = event.widget
            x = (int)(canvas.canvasx(event.x) / 32)
            y = (int)(canvas.canvasy(event.y) / 32)
            index = level.width * y + x
            if len(level.tile_map) > index:
                type = level.get_tile_at(index, self.rom_file).tile_type
                tile_set_index = level.tile_map[index]
                self.info_var.set(f'Tile type: 0x{format(type, "02x")}, ' +
                             f' Tile set index: 0x{format(tile_set_index, "02x")},' +
                             f' Data index: 0x{format(index, "04x")}, ' +
                             f' X: {x}, Y: {y}')
            else:
                self.info_var.set(f'Out of range: {index}')

    def save_level_button_clicked(self):
        self.rom_file.save_level(self.current_stage)

    def save_rom_button_clicked(self):
        filename = filedialog.asksaveasfilename(defaultextension=".nes", initialfile=".nes", filetypes=[("Nintendo Entertainment System ROM", "*.nes"), ("All Files", "*")])
        if len(filename) > 0:
            if self.rom_file.write_rom(filename) == RomFile.ERROR_COULD_NOT_FIT_ALL_STAGES:
                messagebox.showerror("Error", "Could not fit all stages!")

    def set_next_click_callback(self, callback):
        self.next_click_callback = callback

    def canvas_clicked(self, event):
        canvas = event.widget
        x = int(canvas.canvasx(event.x) / 32)
        y = int(canvas.canvasy(event.y) / 32)
        if self.next_click_callback is None:
            self.paint_tile(canvas, x, y)
        else:
            self.next_click_callback(x, y)

    def paint_tile(self, canvas, x, y):
        # paint_with_index = 0x5B  # throwable block in stage 1-1
        if self.tile_tools.selected_tile != None:
            paint_with_index = self.tile_tools.selected_tile
            level = self.rom_file.levels[self.current_stage]
            index = level.width * y + x
            if level.tile_map[index] != paint_with_index:
                level.tile_map[index] = paint_with_index
                self.draw_tile(x, y)
                self.draw_sprites()
                self.redraw((x * 32, y * 32, x * 32 + 32, y * 32 + 32))
                # self.draw_stage()
