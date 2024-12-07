import tkinter as tk
import ttkbootstrap as tb
from scipy.io import loadmat
from PIL import Image, ImageTk
import cv2
from tkinter import font, filedialog
from ttkbootstrap.constants import *

class MainApplication(tb.Frame):
    def __init__(self, parent, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('The Reviewy GUI')
        icon = tb.PhotoImage(file='favicon.png')
        self.parent.iconphoto(True, icon)

        self.parent.bind("<space>", lambda event: self.play_pause_callback())
        self.parent.bind("<Left>", lambda event: self.jumpBack())
        self.parent.bind("<Right>", lambda event: self.jumpForward())

        # Objects that update
        self.videoStr = tk.StringVar(self.parent)
        self.videoStr.trace_add("write", lambda *args: self.video_path_updated(*args))
        self.trxStr = tk.StringVar(self.parent)
        self.videoCapture = None
        self.videoDisplay = None
        self.frameNumberStr = tk.StringVar(self.parent)
        self.timeStr = tb.StringVar(self.parent)
        self.playing = False
        self.lastFrame = None
        self.frameJump = 1
        self.frameNumber = None
        self.after_id = None

        # Configure grid columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Find Files Frame
        fileLblFrame = tb.LabelFrame(self, text='File Navigation', padding=10, name='fileLblFrame')
        fileLblFrame.grid(row=0, column=0, columnspan=2, sticky='nw', padx=(15,0), pady=(15,0))  

        self.vidPathLabel = tb.Label(fileLblFrame, text='Video', width=6)
        self.vidPathLabel.grid(row=0, column=0, sticky='w', pady=10, padx=(4,0)) 
        self.videoEntry = tb.Entry(fileLblFrame, width=60, textvariable=self.videoStr)
        self.videoEntry.grid(row=0, column=1, sticky='w')
        videoBrowseBtn = tb.Button(fileLblFrame, text='Browse', command=self.vid_callback, name='videoBrowseBtn')
        videoBrowseBtn.grid(row=0, column=2, stick='w', padx=(6,0))

        trxPathLabel = tb.Label(fileLblFrame, text="Tracks", width=6)
        trxPathLabel.grid(row=1, column=0, sticky='w', padx=(4,0))  
        self.trxEntry = tb.Entry(fileLblFrame, width=60, textvariable=self.trxStr)
        self.trxEntry.grid(row=1, column=1, sticky='w')
        trxBrowsebBtn = tb.Button(fileLblFrame, text='Browse', command=self.trx_callback)
        trxBrowsebBtn.grid(row=1, column=2, sticky='w', padx=(6,0))

        # Video Player Frame
        videoLblFrame = tb.LabelFrame(self, text='Video Player', name='videoLblFrame')
        videoLblFrame.grid(row=1, column=0, sticky='nw', padx=(15,10), pady=15) 
        videoLblFrame.columnconfigure(0, weight=1)

        videoRow0 = tb.Frame(videoLblFrame, width=450, height=30)
        videoRow0.grid(row=0, column=0, sticky="nsew", padx=10, pady=(10,0))

        timeLabel = tb.Label(videoRow0, text='Time:', width=5, name='timeLabel')
        timeLabel.grid(row=0,column=0, sticky='nsew', padx=(4,0))
        timeVarLabel = tb.Label(videoRow0, textvariable=self.timeStr, width=19, anchor='w', name='timeVarLabel')
        timeVarLabel.grid(row=0, column=1, sticky='nsew')

        frameLabel = tb.Label(videoRow0, text='Frame:', width=6, name='frameLabel')
        frameLabel.grid(row=0, column=2)
        frameVarLabel = tb.Label(videoRow0, textvariable=self.frameNumberStr, width=9, anchor='w')
        frameVarLabel.grid(row=0, column=3)
        
        self.playPauseBtn = tb.Button(videoRow0, text='Play \u25B6', bootstyle='success', width=6, command=self.play_pause_callback)
        self.playPauseBtn.grid(row=0, column=4, sticky='nsew')

        videoRow1 = tb.Frame(videoLblFrame, width=450, height=450)
        videoRow1.grid(row=1, column=0, sticky='nsew')
        videoRow0.grid_propagate(False)
        self.videoFrame = tb.Frame(videoRow1, height=450, width=450)
        self.videoFrame.grid_propagate(False)
        self.videoFrame.grid(row=0, column=0, padx=10, pady=10)

        # Column 2
        col2 = tb.Frame(self)
        col2.grid(row=1, column=1, sticky='nw', padx=(5, 15), pady=10)

        # Frame Navigation Frame
        frameNavLblFrame = tb.LabelFrame(col2, text='Frame Navigation')
        frameNavLblFrame.grid(row=0, column=0, sticky='nw', pady=5)

        frameRow0 = tb.Frame(frameNavLblFrame)
        frameRow0.grid(row=0, column=0, pady=(10,5))
        findFrameLabel = tb.Label(frameRow0, text='Find Frame: ')
        findFrameLabel.grid(row=0, column=0, padx=(10,0))
        self.frameNumEntry = tb.Entry(frameRow0, width=7)
        self.frameNumEntry.grid(row=0, column=1)
        self.frameNumEntry.bind("<Return>", self.seekTo)
        findFrameBtn = tb.Button(frameRow0, text='Go!', command=self.seekTo)
        findFrameBtn.grid(row=0, column=2, padx=(2,10))

        frameRow1 = tb.Frame(frameNavLblFrame)
        frameRow1.grid(row=1, column=0, pady=5)
        prevFrameBtn = tb.Button(frameRow1, text='Prev Frame', width=8, bootstyle="secondary", command=self.jumpBack)
        prevFrameBtn.grid(row=0, column=0, padx=(10,5))
        nextFrameBtn = tb.Button(frameRow1, text='Next Frame', width=8, bootstyle="secondary", command=self.jumpForward)
        nextFrameBtn.grid(row=0, column=1, padx=(5,10))

        frameNavSep = tb.Separator(frameNavLblFrame)
        frameNavSep.grid(row=2, column=0, pady=5)

        frameRow2 = tb.Frame(frameNavLblFrame)
        frameRow2.grid(row=3, column=0, pady=5, sticky='nw')
        skipLabel = tb.Label(frameRow2, text='Skip By: ')
        skipLabel.grid(row=0, column=0, sticky='w', padx=(10,0))
        self.skipValueStr = tk.StringVar()  # StringVar to track changes
        self.skipValueStr.trace_add("write", self.update_skip_value_from_trace)
        self.skipEntry = tb.Entry(frameRow2, width=7, textvariable=self.skipValueStr)
        self.skipEntry.grid(row=0, column=1, sticky='nw')

        frameRow3 = tb.Frame(frameNavLblFrame)
        frameRow3.grid(row=4, column=0, pady=(5,10))
        skipBackBtn = tb.Button(frameRow3, text='Skip Back', width=8, name='skipBackBtn', bootstyle="secondary", command=self.jumpBack)
        skipBackBtn.grid(row=0, column=0, padx=(0,5))
        skipForwardBtn = tb.Button(frameRow3, text='Skip Ahead', width=8, name='skipForwardBtn', bootstyle="secondary", command=self.jumpForward)
        skipForwardBtn.grid(row=0, column=1, padx=(5,0))

        # Playback Speed Frame
        playSpeedLblFrame = tb.LabelFrame(col2, text='Playback Speed', padding=10)
        playSpeedLblFrame.grid(row=1, column=0, sticky='nsew', pady=5)
        playSpeedScale = tb.Scale(playSpeedLblFrame, length=200)
        playSpeedScale.grid(row=0, column=0)

    def frame_to_time(self, frame):
        hr = int(frame // 108000)
        frame -= hr * 108000
        min = int(frame // 1800)
        frame -= min * 1800
        sec = int(frame // 30)
        frame -= sec * 30
        return hr, min, sec
    
    def update_frame_num(self):
        if not self.videoCapture:
            self.timeStr.set('')
            self.frameNumberStr.set('')
            return
        frameNumber = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
        self.frameNumber = frameNumber
        hr, min, sec = self.frame_to_time(frameNumber)
        self.frameNumberStr.set(frameNumber)
        self.timeStr.set(f'{hr:02} hr {min:02} min {sec:02} sec')

    def trx_callback(self):
        name = tk.filedialog.askopenfilename(filetypes=[("MATLAB Files", "*.mat")])
        if name.endswith("tracks.mat"):
            self.trxStr.set(name)
            self.trxEntry.configure(bootstyle="default")
        elif name == '':
            return
        else:
            self.trxStr.set('')
            self.trxEntry.configure(bootstyle='danger')
            tk.messagebox.showerror("Validation Error", "Invalid tracks file type")

    def vid_callback(self):
        name = tk.filedialog.askopenfilename(filetypes=[("Video Files", "*.mp4 *.avi")])
        self.videoStr.set(name)
        if name:
            self.load_video(name)

    def play_pause_callback(self):
        if not self.playing:
            self.playing = True
            self.playPauseBtn.configure(text='Pause \u23F8', bootstyle='danger')
            self.update_video_frame() 
        else:
            self.playing = False
            self.playPauseBtn.configure(text='Play \u25B6', bootstyle='success')
            # Cancel any scheduled updates
            if self.after_id:
                self.videoFrame.after_cancel(self.after_id)
                self.after_id = None

    def load_video(self, videoPath):
        self.videoCapture = cv2.VideoCapture(videoPath)
        if not self.videoCapture.isOpened():
            tk.messagebox.showerror('Error', 'Cannot open video file.')
            return  
        
        ret, frame = self.videoCapture.read()
        if not ret or frame is None:
            tk.messagebox.showerror("Error", "Unable to read the first frame of the video.")
            self.videoCapture.release()
            return

        frame = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        # Resize frame dynamically to fit the videoFrame widget
        vidWidth = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
        frameWidth = self.videoFrame.winfo_width()
        scale = frameWidth / vidWidth
        width = int(vidWidth * scale)
        height = int(frame.shape[0] * scale)

        frame = cv2.resize(frame, (width, height))
        img = ImageTk.PhotoImage(Image.fromarray(frame))

        # Display the image
        self.videoDisplay = tb.Label(self.videoFrame, image=img)
        self.videoDisplay.image = img
        self.videoDisplay.grid(row=0, column=0)


        # Update the frame number display
        self.update_frame_num()
        self.parent.focus_set()
        self.lastFrame = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))

    def update_video_frame(self):
        if not self.playing or not self.videoCapture:
            return

        # Read the next frame
        ret, frame = self.videoCapture.read()
        if not ret:  # Stop playback if no more frames are available
            self.playing = False
            self.playPauseBtn.configure(text='Replay \u21BB', bootstyle='warning', command=self.replay_video)
            return

        # Resize the frame dynamically to fit the videoFrame widget
        vidWidth = self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
        frameWidth = self.videoFrame.winfo_width()
        scale = frameWidth / vidWidth
        width = int(vidWidth * scale)
        height = int(frame.shape[0] * scale)
        resized_frame = cv2.resize(frame, (width, height))

        # Convert the frame to ImageTk format and display it
        frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

        if hasattr(self, 'videoDisplay'):
            self.videoDisplay.configure(image=img)
            self.videoDisplay.image = img
        else:
            self.videoDisplay = tk.Label(self.videoFrame, image=img)
            self.videoDisplay.image = img
            self.videoDisplay.grid(row=0, column=0)

        # Update the frame number and schedule the next update
        self.update_frame_num()
        fps = self.videoCapture.get(cv2.CAP_PROP_FPS)
        delay = int(1000 / fps)
        self.after_id = self.videoFrame.after(delay, self.update_video_frame)


    def replay_video(self):
        if self.videoCapture:
            self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, 0)
        self.playing = True
        self.playPauseBtn.configure(text="Pause \u23F8", bootstyle="danger", command=self.play_pause_callback)
        if self.after_id:
            self.videoFrame.after_cancel(self.after_id)
        self.update_video_frame()

    def video_path_updated(self, *args):
        if not self.videoStr.get():  # If the path is cleared
            if self.videoCapture:
                self.videoCapture.release()
            if self.videoDisplay:
                self.videoDisplay.destroy()
            self.videoCapture = None
            self.videoDisplay = None
            self.playPauseBtn.configure(text='Play \u25B6', bootstyle='success')
            self.update_frame_num()

    def seekTo(self, event=None):
        if not self.videoCapture or not self.videoCapture.isOpened():
            return

        if self.playing:
            self.playing = False
            if self.after_id:
                self.videoFrame.after_cancel(self.after_id)
                self.after_id = None

        try:
            seekFrame = int(self.frameNumEntry.get())
        except ValueError:
            print("Invalid frame input.")
            return

        seekFrame = max(1, min(seekFrame, int(self.lastFrame)))
        if self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, seekFrame - 1):
            ret, frame = self.videoCapture.read()
            if ret and frame is not None:
                # Resize the frame dynamically to fit the videoFrame widget
                vidWidth = self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
                frameWidth = self.videoFrame.winfo_width()
                scale = frameWidth / vidWidth
                width = int(vidWidth * scale)
                height = int(frame.shape[0] * scale)
                resized_frame = cv2.resize(frame, (width, height))

                # Convert the frame to ImageTk format and display it
                frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
                img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

                if hasattr(self, 'videoDisplay'):
                    self.videoDisplay.configure(image=img)
                    self.videoDisplay.image = img
                else:
                    self.videoDisplay = tk.Label(self.videoFrame, image=img)
                    self.videoDisplay.image = img
                    self.videoDisplay.grid(row=0, column=0)

            # Update frame number and time display
            self.update_frame_num()

    def jumpForward(self):
        if not self.videoCapture or not self.videoCapture.isOpened():
            return
        
        if self.skipEntry.get() == '0' or self.skipEntry.get() == '':
            self.frameJump = 1

        try:
            currFrame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
            targetFrame = min(currFrame + self.frameJump, int(self.lastFrame) - 1)
            print(f'Current: {currFrame}, Target: {targetFrame}')
        except ValueError:
            print("Invalid frame jump size.")
            return

        # Ensure correct frame position
        self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, targetFrame - 1)
        ret, frame = self.videoCapture.read()  # Read only the correct target frame
        if ret and frame is not None:
            self.display_frame(frame)
            self.update_frame_num()

    def jumpBack(self):
        if not self.videoCapture or not self.videoCapture.isOpened():
            return
        
        if self.skipEntry.get() == '0' or self.skipEntry.get() == '':
            self.frameJump = 1

        try:
            currFrame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
            targetFrame = max(currFrame - self.frameJump, 1)  # Avoid setting to frame 0
            print(f'Current: {currFrame}, Target: {targetFrame}')
        except ValueError:
            print("Invalid frame jump size.")
            return

        # Ensure correct frame position
        self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, targetFrame - 1)
        ret, frame = self.videoCapture.read()  # Read only the correct target frame
        if ret and frame is not None:
            self.display_frame(frame)
            self.update_frame_num()


    def display_frame(self, frame):
        # Resize the frame dynamically to fit the videoFrame widget
        vidWidth = self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
        frameWidth = self.videoFrame.winfo_width()
        scale = frameWidth / vidWidth
        width = int(vidWidth * scale)
        height = int(frame.shape[0] * scale)
        resized_frame = cv2.resize(frame, (width, height))

        # Convert the frame to ImageTk format and display it
        frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)
        img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))

        if hasattr(self, 'videoDisplay'):
            self.videoDisplay.configure(image=img)
            self.videoDisplay.image = img
        else:
            self.videoDisplay = tk.Label(self.videoFrame, image=img)
            self.videoDisplay.image = img
            self.videoDisplay.grid(row=0, column=0)

    def update_skip_value_from_trace(self, *args):
        try:
            # Get the value from the StringVar
            skip_value = int(self.skipValueStr.get())
            if skip_value <= 0:
                skip_value = 1
                print("Invalid skip value.")
            self.frameJump = skip_value  # Update the frame jump value
            print(f"Updated skip value to: {self.frameJump}")
        except ValueError:
            print("Invalid skip value. Please enter a positive integer.")
            self.frameJump = 1  # Set a default value if invalid