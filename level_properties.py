import tkinter as tk
from colors import colors

class LevelProperties:
    def __init__(self, parent, editor):
        self.parent = parent
        self.editor = editor
        self.level = None
        self.level_num = 0
        self.level_name = tk.StringVar()
        self.level_index = tk.StringVar()
        self.level_start_x = tk.StringVar()
        self.level_start_y = tk.StringVar()
        self.card1_world = tk.IntVar()
        self.card1_number = tk.IntVar()
        self.card2_world = tk.IntVar()
        self.card2_number = tk.IntVar()
        self.bg_color = tk.IntVar()
        self.sprite_set = tk.IntVar()

        self.flags = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]
        self.flags2 = [tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar(), tk.IntVar()]

        frame = tk.Frame(parent)

        tk.Label(frame, text="Level index:").grid(row=0)
        tk.Label(frame, textvariable=self.level_index).grid(row=0, column=1)
        tk.Label(frame, text="Level name:").grid(row=1)
        tk.Entry(frame, textvariable=self.level_name).grid(row=1, column=1, columnspan=3)

        tk.Label(frame, text="Start position:").grid(row=2)
        tk.Entry(frame, textvariable=self.level_start_x, width=5).grid(row=2, column=1)
        tk.Entry(frame, textvariable=self.level_start_y, width=5).grid(row=2, column=2)
        tk.Button(frame, text="Place", command=self.place_start_clicked).grid(row=2, column=3)

        self.flag_frame = tk.Frame(frame)
        for i in range(8):
            tk.Checkbutton(self.flag_frame, variable=self.flags[i], command=self.save_flags).pack(side=tk.LEFT)
        self.flag_frame.grid(row=3, columnspan=4)

        self.flag_frame2 = tk.Frame(frame)
        for i in range(8):
            tk.Checkbutton(self.flag_frame2, variable=self.flags2[i], command=self.save_flags).pack(side=tk.LEFT)
        self.flag_frame2.grid(row=4, columnspan=4)

        card_options = ['No card', 1, 2, 3, 4, 5, 6]
        tk.Label(frame, text="Card 1:").grid(row=5)
        tk.OptionMenu(frame, self.card1_world, *card_options).grid(row=5, column=1)
        tk.OptionMenu(frame, self.card1_number, *card_options).grid(row=5, column=2)
        tk.Label(frame, text="Card 2:").grid(row=6)
        tk.OptionMenu(frame, self.card2_world, *card_options).grid(row=6, column=1)
        tk.OptionMenu(frame, self.card2_number, *card_options).grid(row=6, column=2)

        tk.Label(frame, text="BG color:").grid(row=7)
        color_options = []
        for i in range(len(colors)):
            color_options.append(i)
        self.bg_color_picker = tk.OptionMenu(frame, self.bg_color, *color_options, command=self.update_color)
        self.bg_color_picker.grid(row=7, column=1)

        tk.Label(frame, text="Sprite set:").grid(row=8)
        sprite_set_options = [3, 4, 5, 6, 7, 8, 9, 11, 12, 15, 16, 19]
        self.sprite_set_picker = tk.OptionMenu(frame, self.sprite_set, *sprite_set_options,
                                               command=self.update_sprite_set).grid(row=8, column=1)

        frame.pack()

    def update_sprite_set(self, event):
        self.level.stage_sprite_index = self.sprite_set.get()
        self.editor.draw_stage()

    def update_color(self, event):
        color = colors[self.bg_color.get()]
        hexcolor = '#%02x%02x%02x' % (color[0], color[1], color[2])
        self.bg_color_picker.config(bg=hexcolor)
        self.level.set_background_color(self.bg_color.get())
        self.editor.draw_stage()

    def change_level(self, num):
        self.level_num = num
        self.load_data()

    def load_data(self):
        self.level = self.editor.rom_file.levels[self.level_num]
        level_index = self.editor.rom_file.level_index_lookup[self.level_num]
        self.level_index.set(self.level_num)
        if level_index == -1:
            self.level_name.set("")
        else:
            self.level_name.set(self.editor.rom_file.level_names[level_index])

        self.level_start_x.set(self.level.start_x)
        self.level_start_y.set(self.level.start_y)

        self.sprite_set.set(self.level.stage_sprite_index)

        self.load_flags()

    def load_flags(self):
        for i in range(8):
            self.flags[i].set((self.level.flags1 >> (7 - i)) & 0x01)
            self.flags2[i].set((self.level.flags2 >> (7 - i)) & 0x01)

    def save_flags(self):
        value1 = 0
        value2 = 0
        for i in range(8):
            value1 += self.flags[i].get() << 7 - i
            value2 += self.flags2[i].get() << 7 - i
        self.level.flags1 = value1
        self.level.flags2 = value2

    def place_start_clicked(self):
        self.editor.set_next_click_callback(self.place_start_pos)

    def place_start_pos(self, x, y):
        self.level_start_x.set(x)
        self.level_start_y.set(y + 1)
        self.level.start_x = x
        self.level.start_y = y + 1
        self.editor.draw_stage()
