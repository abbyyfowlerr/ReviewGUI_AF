from tkinter import *
from ttkbootstrap.constants import *
import ttkbootstrap as tb
from MainApplication import MainApplication
import darkdetect

def main():
    # Have app match os theme
    os_theme = darkdetect.theme()
    if os_theme == 'Light':
        theme = 'cosmo'
    elif os_theme == 'Dark':
        theme = 'darkly'
    else:
        print('Error detecting os theme')

    root = tb.Window(themename=theme)
    root.geometry("745x680")
    app = MainApplication(root)
    app.pack(side="top", fill="both", expand=True)
    root.mainloop()

if __name__ == "__main__":
    main()