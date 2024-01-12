import tkinter as tk
import json
from logs import LogsTab
from graphs import GraphsTab
from captured_images import CapturedImagesTab
from realtime_video import RealtimeVideoTab

class GUIApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Human Age & Gender Classification")

        # Set the width of the sidebar to 40% of the window size
        window_width = 1366
        window_height = 768
        sidebar_width = int(window_width * 0.20)

       # Calculate the x and y coordinates for the top-center position
        x_position = (self.master.winfo_screenwidth() - window_width) // 2
        y_position = 0  # Top of the screen

        self.master.geometry(f"{window_width}x{window_height}+{x_position}+{y_position}")

        # Create a frame for the sidebar with a black background
        self.sidebar_frame = tk.Frame(self.master, width=sidebar_width, bg="black")
        self.sidebar_frame.pack(side=tk.LEFT, fill=tk.Y)

        # Create a container frame for labels inside the sidebar with a black background
        sidebar_text_container = tk.Frame(self.sidebar_frame, bg="black")
        sidebar_text_container.pack(side=tk.TOP, fill=tk.X)

        # Create labels for navigation in the sidebar with white text and black background
        label_logs = tk.Label(sidebar_text_container, text="Logs", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        label_logs.pack(pady=(50, 0), anchor='w', padx=40, fill='x')
        label_logs.bind("<Button-1>", lambda event: self.show_logs())

        label_graphs = tk.Label(sidebar_text_container, text="Graphs", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        label_graphs.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        label_graphs.bind("<Button-1>", lambda event: self.show_graphs())

        label_captured_images = tk.Label(sidebar_text_container, text="Captured Images", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        label_captured_images.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        label_captured_images.bind("<Button-1>", lambda event: self.show_captured_images())

        label_realtime_video = tk.Label(sidebar_text_container, text="Realtime Video", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        label_realtime_video.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        label_realtime_video.bind("<Button-1>", lambda event: self.show_realtime_video())

        # Create a frame for the main content area
        self.content_frame = tk.Frame(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Default tab is "Logs"
        self.show_logs()

    def show_logs(self):
        self.content_frame.destroy()
        self.content_frame = LogsTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_graphs(self):
        self.content_frame.destroy()
        self.content_frame = GraphsTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_captured_images(self):
        self.content_frame.destroy()
        self.content_frame = CapturedImagesTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

    def show_realtime_video(self):
        self.content_frame.destroy()
        self.content_frame = RealtimeVideoTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.mainloop()
