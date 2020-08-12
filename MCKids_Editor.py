from tkinter import *
from editor import Editor

# the main window
window = Tk()
window.title("M.C. Kids Level Editor")
window.geometry("1549x1068")

editor = Editor(window)

window.mainloop()