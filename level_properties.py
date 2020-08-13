import tkinter as tk


class LevelProperties:
    def __init__(self, parent, editor):
        self.editor = editor
        self.level_num = 0
        self.level_name = tk.StringVar()
        self.level_start_x = tk.StringVar()
        self.level_start_y = tk.StringVar()

        frame = tk.Frame(parent)

        tk.Label(frame, text="Level name:").grid(row=0)
        tk.Entry(frame, textvariable=self.level_name).grid(row=0, column=1, columnspan=2)

        tk.Label(frame, text="Start position:").grid(row=1)
        tk.Entry(frame, textvariable=self.level_start_x, width=5).grid(row=1, column=2)
        tk.Entry(frame, textvariable=self.level_start_y, width=5).grid(row=1, column=3)
        tk.Button(frame, text="Place", command=self.place_start_clicked).grid(row=1, column=4)

        frame.pack()

    def change_level(self, num):
        self.level_num = num
        self.load_data()

    def load_data(self):
        # level = self.editor.rom_file.levels[self.level_num]
        level_index = self.editor.rom_file.level_index_lookup[self.level_num]
        if level_index == -1:
            self.level_name.set("")
        else:
            self.level_name.set(self.editor.rom_file.level_names[level_index])

        self.level_start_x.set(self.editor.rom_file.start_pos_x[self.level_num])
        self.level_start_y.set(self.editor.rom_file.start_pos_y[self.level_num])

    def place_start_clicked(self):
        self.editor.set_next_click_callback(self.place_start_pos)

    def place_start_pos(self, x, y):
        self.level_start_x.set(x)
        self.level_start_y.set(y + 1)
        self.editor.rom_file.start_pos_x[self.level_num] = x
        self.editor.rom_file.start_pos_y[self.level_num] = y + 1
        self.editor.draw_stage()
