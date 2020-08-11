import tkinter as tk


class SpriteTools:

    def __init__(self, parent, redraw_callback):
        self.selected_spawn_x = tk.StringVar()
        self.selected_spawn_y = tk.StringVar()
        self.selected_spawn_id = tk.StringVar()
        self.level = None
        self.index = -1
        self.redraw = redraw_callback

        self.frame = tk.Frame(parent)
        tk.Label(self.frame, text="Sprites:").grid(row=0)
        self.sprite_list = tk.Listbox(self.frame, selectmode=tk.SINGLE)
        self.sprite_list.configure(exportselection=False)
        self.sprite_list.bind('<<ListboxSelect>>', self.edit_sprite)
        self.sprite_list.grid(row=1, pady=10, rowspan=5)

        tk.Label(self.frame, text="Spawn X:").grid(row=1, column=2)
        tk.Entry(self.frame, textvariable=self.selected_spawn_x).grid(row=1, column=3)

        tk.Label(self.frame, text="Spawn Y:").grid(row=2, column=2)
        tk.Entry(self.frame, textvariable=self.selected_spawn_y).grid(row=2, column=3)

        tk.Label(self.frame, text="Sprite ID:").grid(row=3, column=2)
        tk.Entry(self.frame, textvariable=self.selected_spawn_id).grid(row=3, column=3)

        tk.Button(self.frame, text="Save", command=self.save_button_clicked).grid(row=4, column=2, columnspan=2)

        self.frame.pack(fill=tk.BOTH)

    def load_from_level(self, level):
        self.level = level
        self.sprite_list.delete(0, tk.END)
        for i in range(len(level.spawn_points)):
            self.sprite_list.insert(i, f'Sprite {level.spawn_points[i].sprite_index} at {level.spawn_points[i].x}x{level.spawn_points[i].y}')

    def edit_sprite(self, event):
        tup = self.sprite_list.curselection()
        if len(tup) == 1:
            self.index = tup[0]
            self.selected_spawn_x.set(self.level.spawn_points[self.index].x)
            self.selected_spawn_y.set(self.level.spawn_points[self.index].y)
            self.selected_spawn_id.set(self.level.spawn_points[self.index].sprite_index)
        else:
            self.index = -1

    def save_button_clicked(self):
        if self.index >= 0:
            self.level.spawn_points[self.index].x = int(self.selected_spawn_x.get())
            self.level.spawn_points[self.index].y = int(self.selected_spawn_y.get())
            self.level.spawn_points[self.index].sprite_index = int(self.selected_spawn_id.get())
            self.load_from_level(self.level)
            self.redraw()

