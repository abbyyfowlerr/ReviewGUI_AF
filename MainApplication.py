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

        # Objects that update
        self.videoStr = tk.StringVar(self.parent)
        self.trxStr = tk.StringVar(self.parent)
        self.videoCapture = None
        self.videoDisplay = None
        self.frameNumber = None
        self.frameNumberStr = tk.StringVar(self.parent)

        # Configure grid columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=2)
        self.columnconfigure(1, weight=1)

        # COLUMN 1
        col1 = tb.Frame(self, padding=10)
        col1.grid(row=0, column=0, sticky='nsew', padx=(10,0))

        # Find Files Frame
        fileLblFrame = tb.LabelFrame(col1, text='File Navigation', padding=10)
        fileLblFrame.grid(row=0, column=0, sticky='nsew', pady=(5,0))  

        vidPathLabel = tb.Label(fileLblFrame, text='Video', width=6)
        vidPathLabel.grid(row=0, column=0, sticky='w', pady=10)  
        self.videoEntry = tb.Entry(fileLblFrame, width=40, textvariable=self.videoStr)
        self.videoEntry.grid(row=0, column=1, sticky='w', padx=(0,5))
        videoBrowseBtn = tb.Button(fileLblFrame, text='Browse', command=self.vid_callback)
        videoBrowseBtn.grid(row=0, column=2, stick='w')

        trxPathLabel = tb.Label(fileLblFrame, text="Tracks", width=6)
        trxPathLabel.grid(row=1, column=0, sticky='w')  
        self.trxEntry = tb.Entry(fileLblFrame, width=40, textvariable=self.trxStr)
        self.trxEntry.grid(row=1, column=1, sticky='w', padx=(0,5))
        trxBrowsebBtn = tb.Button(fileLblFrame, text='Browse', command=self.trx_callback)
        trxBrowsebBtn.grid(row=1, column=2, sticky='w')

        # Video frame
        videoLblFrame = tb.LabelFrame(col1, text='Video Player', padding=10)
        videoLblFrame.grid(row=1, column=0, sticky='nsew', pady=(20,10)) 
        videoLblFrame.columnconfigure(0, weight=1)

        videoRow0 = tb.Frame(videoLblFrame)
        videoRow0.grid(row=0, column=0)
        videoRow0.columnconfigure(0, weight=1)

        timeLabel = tb.Label(videoRow0, text='Time: ', width=14)
        timeLabel.grid(row=0,column=0)
        timeStr = tb.StringVar(value='0')
        timeVarLabel = tb.Label(videoRow0, textvariable=timeStr)
        timeVarLabel.grid(row=0, column=1)

        frameLabel = tb.Label(videoRow0, text='Frame:')
        frameLabel.grid(row=0, column=2)
        frameNumStr = tb.StringVar(value='0')
        frameVarLabel = tb.Label(videoRow0, textvariable=frameNumStr, width=7)
        frameVarLabel.grid(row=0, column=3)
        
        playButton = tb.Button(videoRow0, text='Play \u25B6', bootstyle='success', width=6)
        playButton.grid(row=0, column=4)

        videoRow1 = tb.Frame(videoLblFrame)
        videoRow1.grid(row=1, column=0)
        self.videoFrame = tb.Frame(videoRow1, height=450, width=450)
        self.videoFrame.grid_propagate(False)
        self.videoFrame.grid(row=0, column=1, pady=10)

        # COLUMN 2
        col2 = tb.Frame(self, padding=10)
        col2.grid(row=0, column=1, sticky='nsew', padx=10)

        # Layout Frame
        layoutLblFrame = tb.LabelFrame(col2, text='Layout', padding=10)
        layoutLblFrame.grid(row=0, column=0, sticky='nsew', pady=5)

        radio1 = tb.Radiobutton(layoutLblFrame, text='default')
        radio1.grid(row=0, column=0, padx=3)
        radio2 = tb.Radiobutton(layoutLblFrame, text='clips')
        radio2.grid(row=0, column=1, padx=3)
        radio3 = tb.Radiobutton(layoutLblFrame, text='neural')
        radio3.grid(row=0, column=2, padx=3)

        # Frame Navigation Frame
        frameNavLblFrame = tb.LabelFrame(col2, text='Frame Navigation', padding=10)
        frameNavLblFrame.grid(row=1, column=0, sticky='nsew', pady=5)

        frameRow0 = tb.Frame(frameNavLblFrame, width=20)
        frameRow0.grid(row=0, column=0, pady=5)
        findFrameLabel = tb.Label(frameRow0, text='Find Frame: ')
        findFrameLabel.grid(row=0, column=0)
        frameNumEntry = tb.Entry(frameRow0, width=7)
        frameNumEntry.grid(row=0, column=1)
        findFrameBtn = tb.Button(frameRow0, text='Go!')
        findFrameBtn.grid(row=0, column=2)

        frameRow1 = tb.Frame(frameNavLblFrame, width=20)
        frameRow1.grid(row=1, column=0, pady=5)
        prevFrameBtn = tb.Button(frameRow1, text='Prev Frame')
        prevFrameBtn.grid(row=0, column=0)
        nextFrameBtn = tb.Button(frameRow1, text='Next Frame')
        nextFrameBtn.grid(row=0, column=1)

        frameNavSep = tb.Separator(frameNavLblFrame)
        frameNavSep.grid(row=2, column=0)

        frameRow2 = tb.Frame(frameNavLblFrame, width=20)
        frameRow2.grid(row=3, column=0, pady=5)
        skipLabel = tb.Label(frameRow2, text='Skip By')
        skipLabel.grid(row=0, column=0)
        skipEntry = tb.Entry(frameRow2, width=7)
        skipEntry.grid(row=0, column=1)

        frameRow3 = tb.Frame(frameNavLblFrame, width=20)
        frameRow3.grid(row=4, column=0, pady=5)
        skipForwardBtn = tb.Button(frameRow3, text='Skip Forward')
        skipForwardBtn.grid(row=0, column=0)
        skipBackBtn = tb.Button(frameRow3, text='Skip Back')
        skipBackBtn.grid(row=0, column=1)

        # Playback Speed Frame
        playSpeedLblFrame = tb.LabelFrame(col2, text='Playback Speed', padding=10)
        playSpeedLblFrame.grid(row=2, column=0, sticky='nsew', pady=5)
        playSpeedLabel = tb.Label(playSpeedLblFrame, text='Playback Speed')
        playSpeedLabel.grid(row=0, column=0)
        playSpeedSpin = tb.Spinbox(playSpeedLblFrame, width=4)
        playSpeedSpin.grid(row=0, column=1)

    def frame_to_time(frame):
        hr = frame // 108000
        frame -= hr * 108000
        min = frame // 1800
        frame -= min * 1800
        sec = frame // 30
        frame -= sec * 30
        return hr, min, sec, frame
    
    def update_frame_num(self):
        frameNumber = self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES)
        hr, min, sec, time = frame_to_time(frameNumber)
        self.frameNumber = frameNumber

    def trx_callback(self):
        name = tk.filedialog.askopenfilename(filetypes=[("MATLAB Files", "*.mat")])
        if 'tracks.mat' in name:
            self.trxStr.set(name)
            self.trxEntry.configure(bootstyle="default")
        else:
            self.trxStr.set('')
            self.trxEntry.configure(bootstyle='danger')
            tk.messagebox.showerror("Validation Error", "Invalid tracks file type")

    def vid_callback(self):
        name = tk.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        self.videoStr.set(name)
        if '.avi' in name or '.mp4' in name:
            self.videoStr.set(name)
            self.videoEntry.configure(bootstyle="default")
            self.load_video(name)
        else:
            self.videoStr.set('')
            self.videoEntry.configure(bootstyle='danger')
            tk.messagebox.showerror("Validation Error", "Invalid video file type")

    def load_video(self, videoPath):
        self.videoCapture = cv2.VideoCapture(videoPath)
        if not self.videoCapture.isOpened():
            tk.messagebox.showerror('Error', 'Cannot open video file.')
            return  
        ret, frame = self.videoCapture.read()
        if not ret:
            tk.messagebox.showerror("Error", "Unable to read the first frame of the video.")
            self.videoCapture.release()
            return
        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        vidWidth = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frameWidth = self.videoFrame.winfo_width()
        scale = frameWidth/vidWidth
        height = width = int(vidWidth * scale)
        frame = cv2.resize(frame, (width, height)) # dynamically update this?
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        self.videoDisplay = tb.Label(self.videoFrame, image=img)
        self.videoDisplay.image = img
        self.videoDisplay.grid(row=0, column=0)

        self.update_frame_num()

