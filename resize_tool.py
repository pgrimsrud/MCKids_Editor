import tkinter as tk
from tkinter import messagebox

class ResizeTool:
    def __init__(self, root, level, render_callback):
        self.level = level
        self.render = render_callback

        self.width = tk.StringVar()
        self.height = tk.StringVar()
        self.width.set(f'{level.width}')
        self.height.set(f'{level.height}')

        self.dialog = tk.Toplevel(root)
        self.dialog.geometry("250x200")
        self.dialog.resizable(False, False)

        tk.Label(self.dialog, text="Width:").grid(row=0, padx=10, pady=5)
        tk.Label(self.dialog, text="Height:").grid(row=1, padx=10, pady=5)

        in_width = tk.Entry(self.dialog, textvariable=self.width)
        in_height = tk.Entry(self.dialog, textvariable=self.height)

        in_width.grid(row=0, column=1)
        in_height.grid(row=1, column=1)

        self.anchor_frame = tk.Frame(self.dialog)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(0)).grid(row=0, column=0)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(1)).grid(row=0, column=1)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(2)).grid(row=0, column=2)

        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(3)).grid(row=1, column=0)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(4)).grid(row=1, column=1)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(5)).grid(row=1, column=2)

        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(6)).grid(row=2, column=0)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(7)).grid(row=2, column=1)
        tk.Button(self.anchor_frame, text="", width=2, height=1, borderwidth=4, command=lambda: self.set_anchor_point(8)).grid(row=2, column=2)
        self.anchor_frame.grid(row=2, column=0, columnspan=2, pady=5)
        self.anchor = 6
        self.update_anchor_buttons()

        button_frame = tk.Frame(self.dialog)
        tk.Button(button_frame, text="Resize", command=self.resize_clicked).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        button_frame.grid(row=3, columnspan=2)

    def set_anchor_point(self, point):
        self.anchor = point
        self.update_anchor_buttons()

    def update_anchor_buttons(self):
        buttons = self.anchor_frame.winfo_children()
        for i in range(9):
            if self.anchor == i:
                buttons[i].config(bg="gray")
            else:
                buttons[i].config(bg="white")

    def resize_clicked(self):
        width = int(self.width.get())
        height = int(self.height.get())
        if width > 255 or height > 255:
            messagebox.showerror("Error", "Max width/height is 255!")
        if width * height > 5120:
            messagebox.showerror("Error", "The total number of tiles can not exceed 5120!")
            self.dialog.focus()
            return
        new_tile_map = [0] * width * height

        if self.anchor in [0, 3, 6]:
            delta_x = 0
        elif self.anchor in [1, 4, 7]:
            delta_x = int((width - self.level.width) / 2)
        else:
            delta_x = width - self.level.width

        if self.anchor < 3:
            delta_y = 0
        elif self.anchor < 6:
            delta_y = int((height - self.level.height) / 2)
        else:
            delta_y = height - self.level.height

        for x in range(width):
            for y in range(height):
                old_x = x - delta_x
                old_y = y - delta_y
                if 0 <= old_x < self.level.width and 0 <= old_y < self.level.height:
                    new_tile_map[x + y * width] = self.level.tile_map[old_x + old_y * self.level.width]

        for spawn in self.level.spawn_points:
            spawn.x += delta_x
            spawn.y += delta_y

        self.level.width = width
        self.level.height = height
        self.level.tile_map = new_tile_map
        self.render()
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()

