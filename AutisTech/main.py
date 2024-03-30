import tkinter as tk
from tkinter import filedialog as fd
import VideoProcessing.video_main as video
import concurrent.futures
import AutisTech_OD as at


class Main:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("Everything is going to be ok.")
        self.basic = at.Basic_Detector()
        ### The Menu
        menubar = tk.Menu(self.root, tearoff=0)
        
        ### The File Menu
        file = tk.Menu(menubar, tearoff=0)
        file.add_command(label="import video", command=lambda: self.import_video())
        file.add_command(label="export current image")
        file.add_command(label="quit", command=lambda: self.window.quit())
        menubar.add_cascade(label = "File", menu=file)
        
        ### The main menu
        
        ###First and foremost, we need to load a video player. 
        ####### I am not a UI designer. This is functional, not pretty.
        
        player_frame = tk.Frame(self.root)
        video_frame = tk.Frame(player_frame)
        control_frame = tk.Frame(player_frame)
        
        # Place our frames
        video_frame.grid(column=0, row=0)
        control_frame.grid(column=0, row=1, sticky='', padx=5, pady=5)
        player_frame.grid(column=0, row=1)
        
        ### Create and place the video frame
        self.canvas = tk.Canvas(player_frame, width=640, height=360)
        self.video = video.AutisTech_VideoProcessor(self.canvas)
        self.canvas.grid(column=0, row=0)
        self.canvas.bind("<Motion>", self.motion)
        
        ### The video frame controller
        
        control_bar = tk.Frame(control_frame)
        options_bar = tk.Frame(control_frame)
        frames_bar = tk.Frame(control_frame)
        
        restart_button = tk.Button(control_bar, text="<|", command=self.video.restart)
        back_100_btn = tk.Button(control_bar, text="<<<", command=self.video.back_50)
        back_50_btn = tk.Button(control_bar, text="<<", command=self.video.back_10)
        back_one_btn = tk.Button(control_bar, text="<", command=self.video.back_one)
        play_btn = tk.Button(control_bar, text="|>")
        forward_one_btn = tk.Button(control_bar, text = ">", command=self.video.move_forward)
        forward_10_btn = tk.Button(control_bar, text=">>", command=self.video.move_10)
        forward_50_btn = tk.Button(control_bar, text=">>>", command=self.video.move_50)
        
        
        frame_entry = tk.Entry(frames_bar, width=5)
        
        quick_scan_btn = tk.Button(options_bar, text="kwik scan", command=self.quick_scan)
        show_canny_btn = tk.Button(options_bar, text="show canny" if self.video.show_canny == False else "show normal", command=self.video.change_canny)
        control_bar.grid(column=0, row=1)
        frames_bar.grid(column=0, row=2)
        options_bar.grid(column=0, row=0)
        
        ### Place the video frame controller
        frame_entry.grid(column=0, row=2, columnspan=7)
        restart_button.grid(column=0, row=1)
        back_100_btn.grid(column=1, row=1)
        back_50_btn.grid(column=2, row=1)
        back_one_btn.grid(column=3, row=1)
        play_btn.grid(column=4, row=1)
        forward_one_btn.grid(column = 5, row=1)
        forward_10_btn.grid(column=6, row=1)
        forward_50_btn.grid(column=7, row=1)
        quick_scan_btn.grid(column=0, row=0)
        show_canny_btn.grid(column=1, row=0)
        
        ### Place the menu and run the UI
        self.root.config(menu=menubar)
        self.root.mainloop()
        
        ### Entity information
        self.entities = [None]
        
        ### Important flag variables
        self.show_canny = False
        
    def import_video(self):
        id = fd.askopenfilename(title="Please choose a file",
        filetypes =(
        ("mp4", "*.mp4"),
        ("mp4", "*.mp4"),))
        self.video.import_video(id)
        
    def quick_scan(self):
        entities = {None}
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(self.basic.scan_for_new_entities, self.video.get_image(), .6)
            entities = future.result()
        self.entities = entities
        for cat in entities.values():
            for ent in cat:
                self.video.draw_entity_box(ent)
                
    def motion(self, args):
        x, y = args.x, args.y
        print(f"x:{x}, y:{y}")
        for cat in self.entities.values():
            for entity in cat:
                ex, ey, ew, eh = entity.xywh[0], entity.xywh[1], entity.xywh[2], entity.xywh[3]
                if x > ex and x < ex+ew and y > ey and y < ey+eh:
                    print(entity.label)
                else:
                    pass









if __name__ == "__main__":
    print("System starting")
    print("Everything is going to be fine.")
    main = Main()
    