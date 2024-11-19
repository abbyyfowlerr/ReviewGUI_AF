import ttkbootstrap as tb
import numpy as np
from scipy.io import loadmat
import h5py
import cv2
from VideoPlayer import VideoPlayer

class MainApplication(tb.Frame):
    def __init__(self, parent, *args, **kwargs):
        tb.Frame.__init__(self, parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('The Reviewy GUI')
        icon = tb.PhotoImage(file = 'favicon.png')
        self.parent.iconphoto(True, icon)