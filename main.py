from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from MainApplication import MainApplication
import darkdetect

def detect_os_theme():
    os_theme = darkdetect.theme()
    if os_theme == 'Light':
        theme = 'cosmo'
    elif os_theme == 'Dark':
        theme = 'darkly'
    else:
        raise ValueError("Error detecting OS theme")
    return theme

def main():
    # Have app match os theme
    theme = detect_os_theme()
    root = tb.Window(themename=theme)
    root.geometry("745x680") # "745x680" 
    app = MainApplication(root, theme=theme)
    app.pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()

