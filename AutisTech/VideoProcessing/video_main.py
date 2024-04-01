import cv2, copy
import os
from PIL import ImageTk, Image
import numpy as np
import tkinter as tk
import moviepy.editor as editor
# import AudioProcessing.audio_main as audio
class AutisTech_VideoProcessor:
    def __init__(self, canvas):
        self.current_video_path = None
        self.current_frame = 0
        self.vidcap = None
        self.canvas = canvas
        self.is_playing = False
        self.show_canny = False
        self.current_image = None
        self.class_legend = self.setup_classes_legend()
        self.audio = None
        
    def goto_frame(self, current_frame:int=None):
        if current_frame is not None:    
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame-1)
            
        _, img = self.vidcap.read()
        self.current_frame = int(self.vidcap.get(cv2.CAP_PROP_POS_FRAMES))
        self.current_image = cv2.resize(img, (640, 360))
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
        video = editor.VideoFileClip(path)
        audio_path = os.path.join(os.path.dirname(path), "audio.mp3")
        
        ## This stuff is for the transcription. It is not working yet, but I
        ## want to keep the reference for later.
        
        # if not os.path.exists(audio_path):
        #     self.audio = video.audio.write_audiofile(audio_path)
        # audio.transcribe_audio(audio_path)
        
        self.vidcap = cv2.VideoCapture(path)
        _, i = self.vidcap.read()
        self.is_playing = True
        self.goto_frame(0)
        
    def draw_entity_box(self, entity):
        x, y, w, h = entity.xywh[0], entity.xywh[1], entity.xywh[2], entity.xywh[3],
        self.current_image = cv2.rectangle(self.current_image, (x, y), (x+w, y+h), self.class_legend[entity.label], 1, cv2.LINE_AA)
        self.display_image(self.current_image)
        
    def pip(self, point:tuple, image, *args, **kwargs):
        for k in kwargs:
            print(k)
        try:
            pip_img = copy.copy(self.current_image)
            print(point, image.shape)
            pip_img[point[0]:point[0]+image.shape[0], point[1]:point[1]+image.shape[1]] = image
            self.display_image(pip_img)
        except Exception as e:
            print("There was an issue in there")
            print(e)
            print("Breakpoint")
        
                
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
            'car':(255,127,0),
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

class picture_window():
    def __init__(self):
        self.image_frame_pos = ()
        self.window_size = ()
        self.lines = []
        self.info_window_color = (150, 255, 150)
        
    def setupWindow(self, size:tuple, point:tuple, *args, **kwargs):
        self.window = np.zeros((size[0], size[1], 3), dtype=np.uint8)
        self.window[0:-1, 0:-1] = kwargs["color"]
        self.place_window_header(color=(250, 100, 0), padx=2, pady=2, text="Header window")
        self.place_image_frame((150, 150), (32, 15), color=(255, 0, 0), thickness=2)
        
    def place_window_header(self, **kwargs):
        self.window[kwargs["padx"] if "padx" in kwargs.keys() else 5:30, kwargs["pady"] if "pady" in kwargs.keys() else 5:80] = (0, 0, 0)
        self.window = cv2.putText(self.window, kwargs["text"], (3, 8), cv2.FONT_HERSHEY_COMPLEX_SMALL, .4, (255, 255, 255), 1, cv2.LINE_AA)
        print("Window header placed")
        
    def place_image_frame(self, size:tuple, point:tuple, **kwargs):
        color = kwargs["color"]
        thickness = kwargs["thickness"]
        self.image_frame_pos = point
        self.window_size = size
        # self.window[point:thickness, point[1]-thickness:point[1]] = color
        # self.window[0:-1, point[1]-thickness:point[1]] = color
        
    def get_window(self):
        return self.window
        
    def clean_lines(self, lines):
        ret_list = []
        for l in lines:
            if len(l) > 45:
                a = f"{l[0:44]}-"
                b = f"   {l[44:]}"
                ret_list.append(a)
                ret_list.append(b)
            else:
                ret_list.append(l)
        return ret_list
        
    def setup_info_window(self, point:tuple, width_percentage=.8):
        x = round(point[1])
        y = 200
        w = round(abs(((self.window.shape[1] - x)*width_percentage)))
        print(f"x: {x}, y: {y}, w: {w}")
        self.window[30:180, x:x+w] = self.info_window_color
        self.lines = self.clean_lines(self.lines)
        if len(self.lines) > 0:
            for i, l in enumerate(self.lines):
                self.window = cv2.putText(self.window, l, (205, 40 + (12*i)), cv2.FONT_HERSHEY_COMPLEX_SMALL, .45, (0, 0, 255), 1, cv2.LINE_AA)
        
    def display_image(self, image, size_to_fit=False, keep_proportions=True, offset:tuple=None):
        if size_to_fit:
            d = 0
            if image.shape[0] > image.shape[1]:
                d = 150/image.shape[0]
            else:
                d = 150/image.shape[1]
            print("D", d)
            if keep_proportions:
                print(round(image.shape[0]*d), round(image.shape[1]*d))
                w, h = round(image.shape[0]*d), round(image.shape[1]*d)
                image = cv2.resize(image, (round(image.shape[1]*d), round(image.shape[0]*d)))
            else:
                w, h = 150, 150
                image = cv2.resize(image, self.window_size)
            self.window[self.image_frame_pos[0]:self.image_frame_pos[0]+w, self.image_frame_pos[1]:self.image_frame_pos[1]+h] = image
        else:
            if offset is not None:
                y_offset = offset[0]
                x_offset = offset[1]
            else:
                x_offset = 0
                y_offset = 0
            
            self.window[self.image_frame_pos[0]:self.image_frame_pos[0]+self.window_size[0], self.image_frame_pos[1]:self.image_frame_pos[1]+self.window_size[1]] = image[x_offset:x_offset+self.window_size[0], y_offset:y_offset+self.window_size[1]]
        
    def display_window(self):
        cv2.imshow("window preview", self.window)
        cv2.waitKey(0)
        
## Testing the picture window real quick
if __name__ == "__main__":
    
    pw = picture_window()
    pw.setupWindow((200, 550), (10, 10), color=(100, 255, 0))
    pw.display_image(cv2.imread("C:/Users/Alast/Downloads/171010160355-img-2777-dxo-raw-v2.jpg"), offset=(300, 25), size_to_fit=True)
    pw.lines.append("This is the built in data window.")
    pw.lines.append("This is very customizable, and soon to be very cool")
    pw.lines.append("This window is for purely text data.")
    pw.lines.append("Like transcriptions, reading assistance, and special interest farming")
    pw.setup_info_window((200, 200))
    pw.display_window()