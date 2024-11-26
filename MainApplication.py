import tkinter as tk
import ttkbootstrap as tb
from scipy.io import loadmat
from tkinter import filedialog
from PIL import Image, ImageTk
import cv2

class MainApplication(tb.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('The Reviewy GUI')
        icon = tb.PhotoImage(file='favicon.png')
        self.parent.iconphoto(True, icon)

        # Configure grid columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        # COLUMN 1
        col1 = tb.Frame(self, padding=10)
        col1.grid(row=0, column=0, sticky='nsew', padx=(10,0))

        # Find Files Frame
        self.videoStr = tk.StringVar(self.parent)
        self.trxStr = tk.StringVar(self.parent)

        fileFrame = tb.LabelFrame(col1, text='File Navigation', padding=10)
        fileFrame.grid(row=0, column=0, sticky='nsew', pady=(5,0))  

        vidPathLabel = tb.Label(fileFrame, text='Video', width=6)
        vidPathLabel.grid(row=0, column=0, sticky='w', pady=10)  
        self.videoEntry = tb.Entry(fileFrame, width=50, textvariable=self.videoStr)
        self.videoEntry.grid(row=0, column=1, sticky='w', padx=(0,5))
        videoBrowseBtn = tb.Button(fileFrame, text='Browse', command=self.file_callback)
        videoBrowseBtn.grid(row=0, column=2, stick='w')

        trxPathLabel = tb.Label(fileFrame, text="Tracks", width=6)
        trxPathLabel.grid(row=1, column=0, sticky='w')  
        self.trxEntry = tb.Entry(fileFrame, width=50, textvariable=self.trxStr)
        self.trxEntry.grid(row=1, column=1, sticky='w', padx=(0,5))
        trxBrowsebBtn = tb.Button(fileFrame, text='Browse', command=self.trx_callback)
        trxBrowsebBtn.grid(row=1, column=2, sticky='w')

        # Video frame
        videoFrame = tb.LabelFrame(col1, text='Video Player', padding=10)
        videoFrame.grid(row=1, column=0, sticky='nsew', pady=(20,10))  # Place videoFrame in the grid
        frameLabel = tb.Label(videoFrame, text='Frame:')
        frameLabel.grid(row=0, column=0)

        frameNumStr = tb.StringVar(value='0')

        frameVarLabel = tb.Label(videoFrame, textvariable=frameNumStr, width=7)
        frameVarLabel.grid(row=0, column=1)

        timeLabel = tb.Label(videoFrame, text='Time: ', width=14)
        timeLabel.grid(row=0,column=2)


        timeStr = tb.StringVar(value='0')
        timeVarLabel = tb.Label(videoFrame, textvariable=timeStr)
        timeVarLabel.grid(row=0, column=3)

        playButton = tb.Button(videoFrame, text='Play \u25B6', bootstyle='success', width=6)
        playButton.grid(row=0, column=4)

        # COLUMN 2
        col2 = tb.Frame(self, padding=10)
        col2.grid(row=0, column=1, sticky='nsew', padx=10)

        # Layout Frame
        layoutFrame = tb.LabelFrame(col2, text='Layout', padding=10)
        layoutFrame.grid(row=0, column=0, sticky='nsew', pady=5)

        radio1 = tb.Radiobutton(layoutFrame, text='default')
        radio1.grid(row=0, column=0, padx=3)
        radio2 = tb.Radiobutton(layoutFrame, text='clips')
        radio2.grid(row=0, column=1, padx=3)
        radio3 = tb.Radiobutton(layoutFrame, text='neural')
        radio3.grid(row=0, column=2, padx=3)

        # Frame Navigation Frame
        frameNavFrame = tb.LabelFrame(col2, text='Frame Navigation', padding=10)
        frameNavFrame.grid(row=1, column=0, sticky='nsew', pady=5)

        frameRow0 = tb.Frame(frameNavFrame, width=20)
        frameRow0.grid(row=0, column=0, pady=5)
        findFrameLabel = tb.Label(frameRow0, text='Find Frame: ')
        findFrameLabel.grid(row=0, column=0)
        frameNumEntry = tb.Entry(frameRow0, width=7)
        frameNumEntry.grid(row=0, column=1)
        findFrameBtn = tb.Button(frameRow0, text='Go!')
        findFrameBtn.grid(row=0, column=2)

        frameRow1 = tb.Frame(frameNavFrame, width=20)
        frameRow1.grid(row=1, column=0, pady=5)
        prevFrameBtn = tb.Button(frameRow1, text='Prev Frame')
        prevFrameBtn.grid(row=0, column=0)
        nextFrameBtn = tb.Button(frameRow1, text='Next Frame')
        nextFrameBtn.grid(row=0, column=1)

        frameNavSep = tb.Separator(frameNavFrame)
        frameNavSep.grid(row=2, column=0)

        frameRow2 = tb.Frame(frameNavFrame, width=20)
        frameRow2.grid(row=3, column=0, pady=5)
        skipLabel = tb.Label(frameRow2, text='Skip By')
        skipLabel.grid(row=0, column=0)
        skipEntry = tb.Entry(frameRow2, width=7)
        skipEntry.grid(row=0, column=1)

        frameRow3 = tb.Frame(frameNavFrame, width=20)
        frameRow3.grid(row=4, column=0, pady=5)
        skipForwardBtn = tb.Button(frameRow3, text='Skip Forward')
        skipForwardBtn.grid(row=0, column=0)
        skipBackBtn = tb.Button(frameRow3, text='Skip Back')
        skipBackBtn.grid(row=0, column=1)

        # Playback Speed Frame
        playSpeedFrame = tb.LabelFrame(col2, text='Playback Speed', padding=10)
        playSpeedFrame.grid(row=2, column=0, sticky='nsew', pady=5)
        playSpeedLabel = tb.Label(playSpeedFrame, text='Playback Speed')
        playSpeedLabel.grid(row=0, column=0)
        playSpeedSpin = tb.Spinbox(playSpeedFrame, width=4)
        playSpeedSpin.grid(row=0, column=1)

    def trx_callback(self):
        name = tk.filedialog.askopenfilename()
        if 'tracks.mat' in name:
            self.trxStr.set(name)
            self.trxEntry.configure(bootstyle="default")
        else:
            self.trxStr.set('')
            self.trxEntry.configure(bootstyle='danger')
            tk.messagebox.showerror("Validation Error", "Invalid tracks file type")

    def file_callback(self):
        name = tk.filedialog.askopenfilename()
        self.videoStr.set(name)
        if '.avi' in name or '.mp4' in name:
            self.videoStr.set(name)
            self.videoEntry.configure(bootstyle="default")
        else:
            self.videoStr.set('')
            self.videoEntry.configure(bootstyle='danger')
            tk.messagebox.showerror("Validation Error", "Invalid video file type")
