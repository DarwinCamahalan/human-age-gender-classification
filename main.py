import tkinter as tk
from PIL import Image, ImageTk
from logs import LogsTab
from graphs import GraphsTab
from captured_images import CapturedImagesTab
from realtime_video import RealtimeVideoTab

class GUIApp:
    def __init__(self, master):
        self.master = master
        self.master.title("Human Age & Gender Classification")

        # Set the window icon
        icon_path = "icon.ico"
        icon_image = ImageTk.PhotoImage(Image.open(icon_path))
        self.master.iconphoto(True, icon_image)

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
        self.label_realtime_video = tk.Label(sidebar_text_container, text="Realtime Video", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        self.label_realtime_video.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        self.label_realtime_video.bind("<Button-1>", lambda event: self.show_realtime_video())

        self.label_captured_images = tk.Label(sidebar_text_container, text="Captured Images", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        self.label_captured_images.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        self.label_captured_images.bind("<Button-1>", lambda event: self.show_captured_images())

        self.label_graphs = tk.Label(sidebar_text_container, text="Graphs", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        self.label_graphs.pack(pady=(40, 0), anchor='w', padx=40, fill='x')
        self.label_graphs.bind("<Button-1>", lambda event: self.show_graphs())

        self.label_logs = tk.Label(sidebar_text_container, text="Logs", fg="white", bg="black", cursor="hand2", font=("Arial", 12))
        self.label_logs.pack(pady=(50, 0), anchor='w', padx=40, fill='x')
        self.label_logs.bind("<Button-1>", lambda event: self.show_logs())

        # Create a frame for the main content area
        self.content_frame = tk.Frame(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Default tab is "Realtime Video"
        self.show_realtime_video()

    def switch_tab_colors(self, selected_label):
        # Reset colors for all labels
        for label in [self.label_realtime_video, self.label_captured_images, self.label_graphs, self.label_logs]:
            label.configure(bg="black", fg="white")

        # Set colors for the selected label
        selected_label.configure(bg="white", fg="black")

    def show_logs(self):
        self.content_frame.destroy()
        self.content_frame = LogsTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.switch_tab_colors(self.label_logs)

    def show_graphs(self):
        self.content_frame.destroy()
        self.content_frame = GraphsTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.switch_tab_colors(self.label_graphs)

    def show_captured_images(self):
        self.content_frame.destroy()
        self.content_frame = CapturedImagesTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.switch_tab_colors(self.label_captured_images)

    def show_realtime_video(self):
        self.content_frame.destroy()
        self.content_frame = RealtimeVideoTab(self.master, bg="white")
        self.content_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        self.switch_tab_colors(self.label_realtime_video)

if __name__ == "__main__":
    root = tk.Tk()
    app = GUIApp(root)
    root.resizable(False, False)
    root.mainloop()
