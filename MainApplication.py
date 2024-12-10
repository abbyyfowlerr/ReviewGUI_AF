import tkinter as tk
import ttkbootstrap as tb
from scipy.io import loadmat
from PIL import Image, ImageTk
import cv2
from tkinter import font, filedialog, messagebox
from ttkbootstrap.constants import *
import numpy as np
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

class MainApplication(tb.Frame):
    def __init__(self, parent, theme, *args, **kwargs):
        super().__init__(parent, *args, **kwargs)
        self.parent = parent
        self.parent.title('The Reviewy GUI')
        icon = tb.PhotoImage(file='favicon.png')
        self.parent.iconphoto(True, icon)

        self.parent.bind("<space>", lambda event: self.play_pause_callback())
        self.parent.bind("<Left>", lambda event: self.jumpBack())
        self.parent.bind("<Right>", lambda event: self.jumpForward())
        self.parent.bind("<Button-1>", self.focus_out)

        # Objects that update
        self.videoStr = tk.StringVar(self.parent)
        self.videoStr.trace_add("write", lambda *args: self.video_path_updated(*args))
        self.trxStr = tk.StringVar(self.parent)
        self.trx = None
        self.videoCapture = None
        self.videoDisplay = None
        self.frameNumberStr = tk.StringVar(self.parent)
        self.timeStr = tb.StringVar(self.parent)
        self.playing = False
        self.lastFrame = None
        self.frameJump = 1
        self.frameNumber = None
        self.after_id = None
        self.playbackSpeed = 1
        self.speedValues = [0.25, 0.5, 1, 2, 5, 10, 30]
        self.colors = [(66,228,240),(178,114,0),(0,159,230),(167,121,204)]
        self.spine_data = []
        self.fps = None
        self.theme = theme

        self.initialize_shared_widgets()
        self.load_default_layout()
    
    def update_playback_speed(self, event=None):
        # Get the selected speed from the combobox
        selected_speed = self.speedCombobox.get().replace("x", "")  # Remove the "x" suffix
        try:
            # Update the playback speed
            self.playbackSpeed = float(selected_speed)
            print(f"Playback speed updated to: {self.playbackSpeed}x")
        except ValueError:
            print("Invalid speed selected.")

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
            self.trx = loadmat(name)['astrctTrackers']
            self.spine_data = self.trx[0, 0]['m_afA'][0]*4
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

    def exp_callback(self):
        name = filedialog.askdirectory()
        if name:
            self.expPathVar.set(name)

    def focus_out(self, event):
        widget = self.parent.winfo_containing(event.x_root, event.y_root)  # Find the widget under the cursor
        if not isinstance(widget, tb.Entry):  # Check if the widget is not an entry widget
            self.parent.focus_set()

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
        self.fps = self.videoCapture.get(cv2.CAP_PROP_FPS)
        self.update_frame_num()
        self.parent.focus_set()
        self.lastFrame = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_COUNT))

        if self.showChangepoints.get():
            self.update_plot_window(1)
            self.update_marker(1)

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

        # Convert the frame to RGB format for display
        frame_rgb = cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)

        # Add tracking data (ellipses and lines)
        frame_rgb = self.add_tracks(frame_rgb)

        # Convert the frame to ImageTk format and display it
        img = ImageTk.PhotoImage(Image.fromarray(frame_rgb))
        if hasattr(self, 'videoDisplay'):
            self.videoDisplay.configure(image=img)
            self.videoDisplay.image = img
        else:
            self.videoDisplay = tk.Label(self.videoFrame, image=img)
            self.videoDisplay.image = img
            self.videoDisplay.grid(row=0, column=0)

        self.fps = self.videoCapture.get(cv2.CAP_PROP_FPS)
        current_frame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
        if self.showChangepoints.get():
            if current_frame == 1:
                self.update_plot_window(current_frame)
            elif current_frame % (self.fps * 5) == 0:
                self.update_plot_window(current_frame)
            self.update_marker(current_frame)
        self.update_frame_num()
        delay = int((1 / (self.fps * self.playbackSpeed)) * 1000)
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
        
        try:
            currFrame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
            targetFrame = min(currFrame + self.frameJump, int(self.lastFrame) - 1)
            if self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, targetFrame - 1):
                ret, frame = self.videoCapture.read()  # Read only the correct target frame
                if ret and frame is not None:
                    # Resize and display the updated frame
                    frame = self.process_frame(frame)
                    frame = self.add_tracks(frame)  # Add tracks to the current frame
                    self.display_frame(frame)
                    self.update_frame_num()
                    if self.showChangepoints.get():
                        self.update_marker(targetFrame)
                        self.update_plot_window(targetFrame)
        except ValueError:
            print("Invalid frame jump size.")

    def jumpBack(self):
        if not self.videoCapture or not self.videoCapture.isOpened():
            return

        try:
            currFrame = int(self.videoCapture.get(cv2.CAP_PROP_POS_FRAMES))
            targetFrame = max(currFrame - self.frameJump, 1)  # Avoid setting to frame 0

            if self.videoCapture.set(cv2.CAP_PROP_POS_FRAMES, targetFrame - 1):
                ret, frame = self.videoCapture.read()  # Read only the correct target frame
                if ret and frame is not None:
                    # Resize and display the updated frame
                    frame = self.process_frame(frame)
                    frame = self.add_tracks(frame)  # Add tracks to the current frame
                    self.display_frame(frame)
                    self.update_frame_num()
                    if self.showChangepoints.get():
                        self.update_marker(targetFrame)
                        self.update_plot_window(targetFrame)
        except ValueError:
            print("Invalid frame jump size.")

    def process_frame(self, frame):
        # Resize the frame dynamically to fit the videoFrame widget
        vidWidth = self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH)
        frameWidth = self.videoFrame.winfo_width()
        scale = frameWidth / vidWidth
        width = int(vidWidth * scale)
        height = int(frame.shape[0] * scale)
        resized_frame = cv2.resize(frame, (width, height))

        # Convert the frame to RGB format
        return cv2.cvtColor(resized_frame, cv2.COLOR_BGR2RGB)


    def display_frame(self, frame):
        img = ImageTk.PhotoImage(Image.fromarray(frame))
        if hasattr(self, 'videoDisplay'):
            self.videoDisplay.configure(image=img)
            self.videoDisplay.image = img
        else:
            self.videoDisplay = tk.Label(self.videoFrame, image=img)
            self.videoDisplay.image = img
            self.videoDisplay.grid(row=0, column=0)

    def update_skip(self, *args):
        try:
            skip_value = int(self.skipValueStr.get())
            if skip_value <= 0:
                skip_value = 1
            self.frameJump = skip_value 
        except ValueError:
            self.frameJump = 1  # Set a default value if invalid

    def add_tracks(self, frameR):
        if self.trx is not None and self.videoCapture is not None:
            try:
                if not self.ellipsesOn.get():  
                    return frameR  

                frame_idx = int(self.frameNumberStr.get()) - 1  # Current frame index

                # Get original video dimensions
                vid_width = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_WIDTH))
                vid_height = int(self.videoCapture.get(cv2.CAP_PROP_FRAME_HEIGHT))

                # Get displayed video frame dimensions
                disp_width = self.videoFrame.winfo_width()
                disp_height = self.videoFrame.winfo_height()

                # Calculate scaling factors
                scale_x = disp_width / vid_width
                scale_y = disp_height / vid_height

                thickness = self.ellipseThickness.get()  # Get ellipse thickness from options

                for mouse in range(len(self.trx[0])):  # Iterate over mice
                    # Extract track data for the current mouse
                    x = self.trx[0, mouse]['m_afX'][0][frame_idx]
                    y = self.trx[0, mouse]['m_afY'][0][frame_idx]
                    a = self.trx[0, mouse]['m_afA'][0][frame_idx]
                    b = self.trx[0, mouse]['m_afB'][0][frame_idx]
                    theta = self.trx[0, mouse]['m_afTheta'][0][frame_idx]

                    # Check for valid data (no NaNs)
                    if not np.any(np.isnan([x, y, a, b, theta])):
                        # Scale coordinates and dimensions
                        x = int(x * scale_x)
                        y = int(y * scale_y)
                        a = int(a * scale_x)
                        b = int(b * scale_y)

                        # Draw ellipse
                        frameR = cv2.ellipse(
                            frameR,
                            (x, y), 
                            (a, b), 
                            -theta * 180 / np.pi, 
                            0, 360,  
                            self.colors[mouse],  
                            thickness  
                        )
        
                        nosex = x + np.cos(-theta) * a
                        nosey = y + np.sin(-theta) * a
                        frameR = cv2.line(
                            frameR,
                            (x, y),  
                            (int(nosex), int(nosey)), 
                            self.colors[mouse],  
                            thickness  
                        )
            except Exception as e:
                print(f"Error adding tracks: {e}")
        return frameR
    
    def initialize_shared_widgets(self):
        self.parent.geometry("745x650")
        # Configure grid columns
        self.rowconfigure(0, weight=1)
        self.columnconfigure(0, weight=1)
        self.columnconfigure(1, weight=1)

        # Find Files Frame
        self.fileNavFrame = tb.Frame(self, name="fileNavFrame")
        self.fileNavFrame.grid(row=0, column=0, columnspan=2, sticky="nw", padx=(15, 0), pady=(15, 0)) 

        self.standardFileNavFrame = self.create_standard_file_nav(self.fileNavFrame)
        self.experimentFileNavFrame = self.create_experiment_file_nav(self.fileNavFrame)
        self.experimentFileNavFrame.grid(row=0, column=0, sticky="nsew")
        self.standardFileNavFrame.grid_forget()

        # Video Player Frame
        self.videoLblFrame = tb.LabelFrame(self, text='Video Player', name='videoLblFrame')
        self.videoLblFrame.grid(row=1, column=0, sticky='nw', padx=(15,10), pady=15) 
        self.videoLblFrame.columnconfigure(0, weight=1)

        videoRow0 = tb.Frame(self.videoLblFrame, width=450, height=30)
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

        videoRow1 = tb.Frame(self.videoLblFrame, width=450, height=450)
        videoRow1.grid(row=1, column=0, sticky='nsew')
        self.videoFrame = tb.Frame(videoRow1, height=450, width=450)
        self.videoFrame.grid_propagate(False)
        self.videoFrame.grid(row=0, column=0, padx=10, pady=(10,0))

        self.plotFrame = tb.Frame(self.videoLblFrame, height=70, width=450, name="plotFrame")
        self.plotFrame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        self.plotFrame.grid_remove()

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
        self.skipValueStr.trace_add("write", self.update_skip)
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
        playSpeedLblFrame.grid(row=1, column=0, sticky='nsew', pady=(0,5))

        speedLabel = tb.Label(playSpeedLblFrame, text="Select Speed:")
        speedLabel.grid(row=0, column=0)

        self.speedCombobox = tb.Combobox(
            playSpeedLblFrame,
            values=[f"{speed}x" for speed in self.speedValues],  # Display speeds as "0.5x", "1.0x", etc.
            state="readonly",  # Prevent typing custom values
            width=5
        )
        self.speedCombobox.set(f"{self.playbackSpeed}x")  # Default selected speed
        self.speedCombobox.grid(row=0, column=1)

        # Bind the selection event to update playback speed
        self.speedCombobox.bind("<<ComboboxSelected>>", self.update_playback_speed)

        # Menubar
        self.menubar = tk.Menu(self.parent)
        self.optionsmenu = tk.Menu(self.menubar, tearoff=0)
        self.ellipseThickness = tk.IntVar(self.parent, value=2)
        self.optionsmenu.add_checkbutton(
            label="Thick Ellipses",
            variable=self.ellipseThickness,
            onvalue=4,
            offvalue=2
        )
        self.ellipsesOn = tk.BooleanVar(self.parent, value=True)
        self.optionsmenu.add_checkbutton(
            label="Ellipses On",
            variable=self.ellipsesOn,
            onvalue=True,
            offvalue=False
        )

        self.rigidV = tk.BooleanVar(self.parent, value=True)
        self.optionsmenu.add_checkbutton(
            label="Rigid Directory Structure", 
            variable=self.rigidV, 
            onvalue=True, 
            offvalue=False, 
            command=self.toggle_file_nav_layout
        )

        self.menubar.add_cascade(label="Options", menu=self.optionsmenu)

        self.layoutmenu = tk.Menu(self.menubar, tearoff=0)
        self.showChangepoints = tk.BooleanVar(self.parent, value=False)
        self.layoutmenu.add_checkbutton(
            label="Changepoints Layout",
            variable=self.showChangepoints,
            onvalue=True,
            offvalue=False,
            command=self.toggle_layout
        )
        self.menubar.add_cascade(label="Layouts", menu=self.layoutmenu)
        self.parent.config(menu=self.menubar)

    def load_default_layout(self):
        self.plotFrame.grid_remove()
        if self.rigidV.get():
            self.parent.geometry("745x650")
        else:
            self.parent.geometry("745x680")

    def load_changepoints_layout(self):
        self.plotFrame.grid()
        if self.rigidV.get():
            self.parent.geometry("745x735")
        else:
            self.parent.geometry("745x765")
        self.after(100, self.initialize_plot) 

    def toggle_layout(self):
        if self.showChangepoints.get():
            if not hasattr(self, 'spine_data') or len(self.spine_data)==0:
                messagebox.showinfo(
                    "Info", "Please load a valid tracks file before switching to the Changepoints layout."
                )
                self.showChangepoints.set(False)
                return
            self.load_changepoints_layout()
        else:
            self.load_default_layout()

    def initialize_plot(self):
        plot_width = self.plotFrame.winfo_width() or 1  # Use a minimum width of 1
        plot_height = self.plotFrame.winfo_height() or 1  # Use a minimum height of 1 
        figsize = (plot_width / 100, plot_height / 100)  # Scale to your DPI (100 here)

        # Create the Matplotlib figure and axis with the calculated figsize
        self.fig = Figure(figsize=figsize, dpi=100)
        self.ax = self.fig.add_subplot(111)
        self.ax.set_xticks([])
        self.ax.set_ylim(50, 250)
        self.fig.subplots_adjust(left=0.098, right=0.98, top=0.95, bottom=0.05)

        if self.theme == 'darkly':
            marker_color = 'white' 
        else:
            marker_color = 'black'
        # Initialize an empty plot line and marker
        self.line, = self.ax.plot([], [], lw=1, label="Spine Length")
        self.marker_line = self.ax.axvline(x=0, color=marker_color, linestyle="-", label="Current Position")

        # Add the Matplotlib figure to the plotFrame
        self.canvas = FigureCanvasTkAgg(self.fig, master=self.plotFrame)
        self.canvas.draw()
        self.canvas.get_tk_widget().pack(fill="both", expand=True)

        self.update_plot_window(current_frame=1)

    def update_plot_window(self, current_frame):
        if self.spine_data is None or self.fps is None:
            return 

        window_size = self.fps * 5  # Multiply my number of seconds you want to see
        self.current_window_start = (current_frame // window_size) * window_size
        start_idx = int(self.current_window_start)
        end_idx = int(start_idx + window_size)

        x_data = [i / self.fps for i in range(start_idx, min(end_idx, len(self.spine_data)))]
        y_data = self.spine_data[start_idx:end_idx]

        selected_color = "#{:02x}{:02x}{:02x}".format(*self.colors[0])
        self.line.set_color(selected_color)
        self.line.set_data(x_data, y_data)

        if self.theme == 'darkly':
            self.ax.set_facecolor('#222222')
            self.fig.patch.set_facecolor('#222222')
            self.ax.tick_params(color='white', labelcolor='white')
            for spine in self.ax.spines.values():
                spine.set_color('white')
        else:
            self.ax.set_facecolor('white')
            self.fig.patch.set_facecolor('white')
            self.ax.tick_params(color='#7f8080', labelcolor='#7f8080')
            for spine in self.ax.spines.values():
                spine.set_color('#7f8080')

        self.ax.set_xlim(max(0, x_data[0]), x_data[-1])  
        self.ax.set_ylim(50,250)

        current_time = current_frame / self.fps
        self.marker_line.set_xdata([current_time])


        self.fig.canvas.draw_idle()

    def update_marker(self, current_frame):
        if self.spine_data is None or self.fps is None:
            return 
        
        current_time = current_frame / self.fps
        self.marker_line.set_xdata([current_time]) 
        self.fig.canvas.draw_idle()

    def toggle_file_nav_layout(self):
        if self.rigidV.get():
            if self.showChangepoints.get():
                self.parent.geometry("745x735")
            else:
                self.parent.geometry("745x650")
            self.standardFileNavFrame.grid_forget()
            self.experimentFileNavFrame.grid(row=0, column=0, sticky="nsew")
        else:
            if self.showChangepoints.get():
                self.parent.geometry("745x765")
            else:
                self.parent.geometry("745x680")
            self.experimentFileNavFrame.grid_forget()
            self.standardFileNavFrame.grid(row=0, column=0, sticky="nsew")

    def create_standard_file_nav(self, parent):
        fileLblFrame = tb.LabelFrame(parent, text="File Navigation", padding=10)
        tb.Label(fileLblFrame, text="Video", width=6).grid(row=0, column=0, sticky="w", pady=10, padx=(4, 0))
        tb.Entry(fileLblFrame, width=60, textvariable=self.videoStr).grid(row=0, column=1, sticky="w")
        tb.Button(fileLblFrame, text="Browse", command=self.vid_callback).grid(row=0, column=2, stick="w", padx=(6, 0))

        tb.Label(fileLblFrame, text="Tracks", width=6).grid(row=1, column=0, sticky="w", padx=(4, 0))
        tb.Entry(fileLblFrame, width=60, textvariable=self.trxStr).grid(row=1, column=1, sticky="w")
        tb.Button(fileLblFrame, text="Browse", command=self.trx_callback).grid(row=1, column=2, sticky="w", padx=(6, 0))
        return fileLblFrame
    
    def create_experiment_file_nav(self, parent):
        # path
        frame = tb.LabelFrame(parent, text="File Navigation", padding=5)
        tb.Label(frame, text="Path", width=4).grid(row=0, column=0, sticky="w", pady=5, padx=(4, 0))
        self.expPathVar = tk.StringVar()
        tb.Entry(frame, width=45, textvariable=self.expPathVar).grid(row=0, column=1, sticky="w")
        tb.Button(frame, text="Browse", command=self.exp_callback).grid(row=0, column=2, stick="w", padx=(6))

        # experiment letter
        tb.Label(frame, text="Letter", width=5).grid(row=0, column=3, sticky="w", padx=(10, 0))
        self.expLetterVar = tk.StringVar()
        tb.Entry(frame, width=2, textvariable=self.expLetterVar).grid(row=0, column=4, sticky="w", padx=(0,10))
        tb.Button(frame, text="Load", command=self.load_experiment_files).grid(row=0, column=5, sticky="w", pady=10, padx=(0,5))
        return frame
    
    def load_experiment_files(self):
        experiment_path = self.expPathVar.get().strip()
        test_letter = self.expLetterVar.get().strip().upper()
        if not experiment_path or not test_letter:
            messagebox.showerror("Error", "Please specify both the experiment path and experiment letter.")
            return
        video_path = f"{experiment_path}/Video/Test_{test_letter}_1.avi"
        trx_path = f"{experiment_path}/Output/Video/Motr/MotrTest_{test_letter}_1/Results/Tracks/Test_{test_letter}_1_tracks.mat"
        self.videoStr.set(video_path)
        self.trxStr.set(trx_path)
        self.load_video(video_path)
        self.trx = loadmat(trx_path)['astrctTrackers']
        self.spine_data = self.trx[0, 0]['m_afA'][0]*4