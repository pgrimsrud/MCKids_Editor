import tkinter as tk
from spawnpoint import SpawnPoint
from sprite_names import sprite_names

class SpriteTools:

    def __init__(self, parent, editor):
        self.selected_spawn_x = tk.StringVar()
        self.selected_spawn_y = tk.StringVar()
        self.selected_spawn_id = tk.StringVar()
        self.level = None
        self.index = -1
        self.editor = editor

        self.frame = tk.Frame(parent)
        tk.Label(self.frame, text="Sprites:").grid(row=0)
        self.sprite_list = tk.Listbox(self.frame, selectmode=tk.SINGLE, width=30)
        self.sprite_list.configure(exportselection=False)
        self.sprite_list.bind('<<ListboxSelect>>', self.edit_sprite)
        self.sprite_list.grid(row=1, pady=5, rowspan=5)

        tk.Label(self.frame, text="Spawn X:").grid(row=1, column=2)
        tk.Entry(self.frame, textvariable=self.selected_spawn_x).grid(row=1, column=3)

        tk.Label(self.frame, text="Spawn Y:").grid(row=2, column=2)
        tk.Entry(self.frame, textvariable=self.selected_spawn_y).grid(row=2, column=3)

        tk.Label(self.frame, text="Sprite ID:").grid(row=3, column=2)
        sprite_options = self.__get_sprite_options()
        self.sprite_option = tk.OptionMenu(self.frame, self.selected_spawn_id, *sprite_options, command=self.sprite_option_selected).grid(row=3, column=3)

        sprite_buttons = tk.Frame(self.frame)
        tk.Button(sprite_buttons, text="Delete", command=self.delete_button_clicked).pack(side=tk.LEFT, padx=10)
        tk.Button(sprite_buttons, text="Add", command=self.add_button_clicked).pack(side=tk.LEFT, padx=10)
        sprite_buttons.grid(row=4, column=2, columnspan=2)

        self.frame.pack()

    def __get_sprite_options(self):
        self.sprite_lookup = []
        options = []
        for i in range(len(sprite_names)):
            if sprite_names[i] != '???':
                self.sprite_lookup.append(i)
                options.append(sprite_names[i])

        return options

    def __get_sprite_index(self, name):
        for i in range(len(sprite_names)):
            if sprite_names[i] == name:
                return i
        return 0

    def sprite_option_selected(self, event):
        self.save_sprite()
        self.editor.draw_stage()

    def load_from_level(self, level):
        self.level = level
        self.sprite_list.delete(0, tk.END)
        for i in range(len(level.spawn_points)):
            self.sprite_list.insert(i, f'{level.spawn_points[i].x:03d}x{level.spawn_points[i].y:03d}: {sprite_names[level.spawn_points[i].sprite_index]}')
        self.sprite_list.select_set(self.index)

    def edit_sprite(self, event):
        self.editor.deselect()
        tup = self.sprite_list.curselection()
        if len(tup) == 1:
            self.index = tup[0]
            self.editor.set_next_click_callback(self.place_sprite)
            self.selected_spawn_x.set(self.level.spawn_points[self.index].x)
            self.selected_spawn_y.set(self.level.spawn_points[self.index].y)
            self.selected_spawn_id.set(sprite_names[self.level.spawn_points[self.index].sprite_index])
            self.editor.draw_stage()
        else:
            self.index = -1

    def place_sprite(self, x, y):
        if self.index >= 0:
            self.level.spawn_points[self.index].x = x
            self.level.spawn_points[self.index].y = y
            self.sprite_list.select_set(self.index)
            self.save_sprite()
            self.editor.draw_stage()

    def save_sprite(self):
        if self.index >= 0:
            self.level.spawn_points[self.index].sprite_index = self.__get_sprite_index(self.selected_spawn_id.get())
            self.load_from_level(self.level)

    def delete_button_clicked(self):
        if self.index >= 0:
            self.level.spawn_points.remove(self.level.spawn_points[self.index])
            self.load_from_level(self.level)
            self.editor.draw_stage()

    def add_button_clicked(self):
        self.level.spawn_points.append(SpawnPoint(5, 5, 32, 0))
        for i in range(len(self.level.spawn_points)):
            self.level.spawn_points[i].index = i
        self.load_from_level(self.level)
        self.sprite_list.select_set(len(self.level.spawn_points) - 1)
        self.edit_sprite(None)

