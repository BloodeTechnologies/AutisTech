import cv2
from PIL import ImageTk, Image
import numpy as np
import tkinter as tk


class AutisTech_VideoProcessor:
    def __init__(self, canvas):
        self.current_video_path = None
        self.current_frame = None
        self.vidcap = None
        self.canvas = canvas
        self.is_playing = False
        self.show_canny = False
        self.current_image = None
        self.class_legend = self.setup_classes_legend()
        
    def goto_frame(self, current_frame:int=None):
        if current_frame is not None:    
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame-1)
            
        _, img = self.vidcap.read()
        self.current_frame = int(self.vidcap.get(cv2.CAP_PROP_POS_FRAMES))
        self.current_image = img
        self.display_image()
        
    def numpy_to_pil(self, img:np.ndarray):
        return Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
    
    def get_image(self):        
        return self.current_image
    
    def next_frame(self):
        if self.current_frame is not None:
            pass
    
    def get_frame_counter(self):
        return self.vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        
    def import_video(self, path:str):
        print("Importing the video", path)
        self.vidcap = cv2.VideoCapture(path)
        _, i = self.vidcap.read()
        self.is_playing = True
        self.goto_frame(0)
        
    def draw_entity_box(self, entity):
        x, y, w, h = entity.xywh[0], entity.xywh[1], entity.xywh[2], entity.xywh[3],
        print(f"x:{x}, y:{y}, h:{h}, w:{w}")
        self.current_image = cv2.rectangle(self.current_image, (x, y), (x+w, y+h), self.class_legend[entity.label], 1, cv2.LINE_AA)
        self.display_image(self.current_image)
                
    def display_image(self, img:np.ndarray = None):
        if img is None:
            img = cv2.resize(self.current_image, (640, 360))
        else:
            img = cv2.resize(img, (640, 360))
        if self.show_canny:
            img = cv2.Canny(img, 10, 250)    
            
            
        mid = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
        final = ImageTk.PhotoImage(image=mid)
        self.canvas.create_image(0, 0, image=final, anchor=tk.NW)
        self.canvas.image = final
                    
    def play_video(self, current_frame:int = None):
        self.is_playing = True
        
    def move_forward(self):
        self.current_frame += 1
        self.goto_frame(self.current_frame)
        
    def back_one(self):
        self.current_frame -= 1
        self.goto_frame(self.current_frame)
        
    def back_10(self):
        self.current_frame -= 10
        self.goto_frame(self.current_frame)
        
    def back_50(self):
        self.current_frame -= 50
        self.goto_frame(self.current_frame)
    
    def restart(self):
        self.current_frame = 0
        self.goto_frame(self.current_frame)
        
    def move_10(self):
        self.current_frame += 10
        self.goto_frame(self.current_frame)
        
    def move_50(self):
        self.current_frame += 50
        self.goto_frame(self.current_frame)
        
    def change_canny(self):
        if self.show_canny:
            self.show_canny = False
        else:
            self.show_canny = True
        self.display_image()
        
    def setup_classes_legend(self):
        class_legend = {
            'person':(0, 0, 255),
            'bicycle':(100, 0, 255),
            'car':(100, 100, 255),
            'motorcycle':(0, 100, 255),
            'airplane':(0, 200, 255),
            'bus':(140, 202, 14),
            'train':(27, 115, 89),
            'truck':(115, 12, 115),
            'boat':(18, 205, 78),
            'traffic light':(37, 119, 200),
            'fire hydrant':(0, 15, 255),
            'street sign':(0, 115, 255),
            'stop sign':(115, 105, 255),
            'parking meter':(105, 114, 185),
            'bench':(255, 125, 0),
            'bird':(255, 125, 0),
            'cat':(255, 125, 0),
            'dog':(255, 125, 0),
            'horse':(255, 125, 0),
            'sheep':(255, 125, 0),
            'umbrella':(200, 125, 255),
            'potted plant':(125, 255, 125),
            'suitcase':(75, 168, 200)
        }
        return class_legend
