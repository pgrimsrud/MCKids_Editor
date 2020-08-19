from colors import colors
import tkinter as tk


class ColorPicker:
    def __init__(self, parent, title, callback):
        self.window = tk.Toplevel(parent)
        self.window.geometry("305x360")
        self.window.resizable(False, False)
        self.callback = callback
        dark_colors = [0x00, 0x01, 0x02, 0x03, 0x04, 0x05, 0x06, 0x07, 0x08, 0x09, 0x0A, 0x0B, 0x0C, 0x0D,
                       0x0E, 0x0F, 0x1D, 0x1E, 0x1F, 0x2D, 0x2E, 0x2F, 0x3E, 0x3F]
        for c in range(0x40):
            color = (colors[c][0], colors[c][1], colors[c][2])
            color_str = "#%02x%02x%02x" %color
            if c in dark_colors:
                fg = '#ffffff'
            else:
                fg = '#000000'
            btn = tk.Button(self.window,
                            text="0x{:02x}".format(c),
                            bg=color_str,
                            fg=fg,
                            width=4, height=2,
                            command=lambda color=c: self.select_color(color))
            btn.grid(row=(int)(c / 8), column=c % 8)
        tk.Button(self.window, text="Cancel", width=20, command=self.close_window).grid(row=8, columnspan=8)

    def close_window(self):
        self.window.destroy()

    def select_color(self, colorId):
        self.callback(colorId)
        self.close_window()
