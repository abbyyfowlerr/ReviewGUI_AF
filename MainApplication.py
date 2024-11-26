import ttkbootstrap as tb
from scipy.io import loadmat
from VideoPlayer import VideoPlayer
from tkinter import filedialog

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

        # Column 1
        col1 = tb.Frame(self, padding=10)
        col1.grid(row=0, column=0, sticky="nsew", padx=(10,0))

        # Find Files
        path_str = None
        tracks_str = None

        fileFrame = tb.LabelFrame(col1, text='File Navigation', padding=10)
        fileFrame.grid(row=0, column=0, sticky="nsew")  

        vidPathLabel = tb.Label(fileFrame, text="Video", padding=10)
        vidPathLabel.grid(row=0, column=0, sticky="w")  
        path_entry = tb.Entry(fileFrame, width=58, textvariable=path_str)
        path_entry.grid(row=0, column=1, sticky="w")

        tracksPathLabel = tb.Label(fileFrame, text="Tracks", padding=10)
        tracksPathLabel.grid(row=1, column=0, sticky="w")  
        tracks_entry = tb.Entry(fileFrame, width=58, textvariable=tracks_str)
        tracks_entry.grid(row=1, column=1, sticky="w")

        # Column 2
        col2 = tb.Frame(self, padding=10)
        col2.grid(row=0, column=1, sticky="nsew", padx=10)

        # Layout 
        layoutFrame = tb.LabelFrame(col2, text='Layout', padding=10)
        layoutFrame.grid(row=1, column=0, sticky="nsew", pady=5)

        radio1 = tb.Radiobutton(layoutFrame, text='default')
        radio1.grid(row=0, column=0, padx=3)
        radio2 = tb.Radiobutton(layoutFrame, text='clips')
        radio2.grid(row=0, column=1, padx=3)
        radio3 = tb.Radiobutton(layoutFrame, text='neural')
        radio3.grid(row=0, column=2, padx=3)

        # Theme 
        themeFrame = tb.LabelFrame(col2, text='Theme', padding=10)
        themeFrame.grid(row=0, column=0, sticky="nsew")
        theme_label = tb.Label(themeFrame, text='Choose a Theme:')
        theme_label.grid(row=0, column=0, sticky="w") 

        self.theme_selector = tb.Combobox(
            themeFrame,
            values=parent.style.theme_names(),
            bootstyle='info',
            width=10
        )
        self.theme_selector.grid(row=1, column=0, pady=10, sticky="w") 

        apply_button = tb.Button(
            themeFrame, text='Apply', command=self.change_theme, bootstyle='success'
        )
        apply_button.grid(row=1, column=1, pady=5, padx=5, sticky="w")  


        # Video
        videoFrame = tb.LabelFrame(col1, text="Video Player", padding=10)
        videoFrame.grid(row=1, column=0, sticky="nsew", pady=(20,10))  # Place videoFrame in the grid
        frame_label = tb.Label(videoFrame, text="Frame:")
        frame_label.grid(row=0, column=0)

        frame_num_str = tb.StringVar(value="0")

        frame_num_label = tb.Label(videoFrame, textvariable=frame_num_str)
        frame_num_label.grid(row=0, column=1)

        time_label = tb.Label(videoFrame, text="Time:")
        time_label.grid(row=0,column=2)


        time_str = tb.StringVar(value="0")
        time_num_label = tb.Label(videoFrame, textvariable=time_str)
        time_num_label.grid(row=0, column=1)


    def change_theme(self):
        selected_theme = self.theme_selector.get()
        self.parent.style.theme_use(selected_theme)

    def openFile():
        filepath = filedialog.askopenfilename
