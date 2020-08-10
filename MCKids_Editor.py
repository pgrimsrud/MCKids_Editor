from tkinter import *
from rom import RomFile
from editor import Editor

RomFile.load_rom("mckids.nes")

# the main window
window = Tk()
window.title("M.C. Kids level editor")
window.geometry("1045x1064")# + str(stage_height*16*2 + 16))

editor = Editor(window)

window.mainloop()
