from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from pathlib import Path
from MainApplication import MainApplication

def main():
    root = tb.Window(themename='simplex')
    app = MainApplication(root)
    app.pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()