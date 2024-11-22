import ttkbootstrap as tb
import numpy as np
from scipy.io import loadmat
import h5py
import cv2
from VideoPlayer import VideoPlayer
from tkinter import filedialog

class MainApplication(tb.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('The Reviewy GUI')
        icon = tb.PhotoImage(file = 'favicon.png')
        self.parent.iconphoto(True, icon)

        label = tb.Label(self, text='Choose a Theme:', font=('Helvetica', 14))
        label.pack(pady=10)

        self.theme_selector = tb.Combobox(
            self,
            values = parent.style.theme_names(),
            bootstyle = 'info'
        )
        self.theme_selector.pack(pady=10)

        self.theme_selector.set(parent.style.theme_use())

        apply_button = tb.Button(self, text='Apply Theme', command=self.change_theme, bootstyle='success')
        apply_button.pack(pady=10)

    def change_theme(self):
        selected_theme = self.theme_selector.get()
        self.parent.style.theme_use(selected_theme)

    def openFile():
        filepath = filedialog.askopenfilename
