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
        self.dialog.geometry("250x100")
        self.dialog.resizable(False, False)

        tk.Label(self.dialog, text="Width:").grid(row=0, padx=10, pady=5)
        tk.Label(self.dialog, text="Height:").grid(row=1, padx=10, pady=5)

        in_width = tk.Entry(self.dialog, textvariable=self.width)
        in_height = tk.Entry(self.dialog, textvariable=self.height)

        in_width.grid(row=0, column=1)
        in_height.grid(row=1, column=1)

        button_frame = tk.Frame(self.dialog)
        tk.Button(button_frame, text="Resize", command=self.resize_clicked).pack(side=tk.LEFT)
        tk.Button(button_frame, text="Cancel", command=self.cancel_clicked).pack(side=tk.LEFT)
        button_frame.grid(row=2, columnspan=2)

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
        for x in range(width):
            for y in range(height):
                if x < self.level.width and y < self.level.height:
                    new_tile_map[x + y * width] = self.level.tile_map[x + y * self.level.width]
        self.level.width = width
        self.level.height = height
        self.level.tile_map = new_tile_map
        self.render()
        self.dialog.destroy()

    def cancel_clicked(self):
        self.dialog.destroy()

