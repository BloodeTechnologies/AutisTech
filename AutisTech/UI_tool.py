import tkinter as tk
from tkinter import filedialog as fd
import cv2
from PIL import ImageTk, Image
import numpy as np
from matplotlib import pyplot as PLT
import AutisTech_OD as AT
import pyaudio
import time, os
from facenet_pytorch import MTCNN, InceptionResnetV1
import csv
from entity_manager import Entity_Manager
from copy import copy
import traceback
class UI_Tool:
    
    def restart(self):
        self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, 0)

    def onselect(self, evt):
        self.shown_ents.clear()
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.shown_ents.append(str(value.split(" ")[0]))
        if not self.is_playing:
            self.update_boxes(cv2.cvtColor(np.array(self.current_image), cv2.COLOR_BGR2RGB))
        
    def entbox_Select(self, evt):
        w = evt.widget
        index = int(w.curselection()[0])
        value = w.get(index)
        self.shown_ents.append(str(value.split(" ")[0]))
        if not self.is_playing:
            self.update_boxes(cv2.cvtColor(np.array(self.current_image), cv2.COLOR_BGR2RGB))
        
            
    def update_boxes(self, img):
        self.update_current_ents()
        for e in self.shown_ents:
            if e in self.current_ents:
                img = self.draw_boxes(self.shown_ents, self.current_ents[e], img, (255, 0, 0))
                self.current_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                self.photo = ImageTk.PhotoImage(image=self.current_image)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
    
    def motion(self, evt):
        x, y = evt.x, evt.y
        try:
            selected = self.check_for_entity((x, y))
            if selected is not None:
                if selected.face is not None:
                    self.enhance_face(selected.face, 4)
                else:
                    self.enhanced_entity(selected.image,2)
        except:
            pass
        
    def check_for_entity(self, pos):
        x2, y2 = pos[0], pos[1]
        current_entity = None
        for e in self.current_ents:
            for i in self.current_ents[e]:
                x, y, w, h = i.xywh[0], i.xywh[1], i.xywh[2], i.xywh[3]
                if x2 > x and x2 < x+w and y2 > y and y2 < y+h:
                    return i
                    
    def Start_Screen(self, window, vidcap=None):
        self.window = window
        self.current_image = None
        self.cur_img = None
        self.vidcap = vidcap
        self.canvas = tk.Canvas(window, width=640, height=360)
        self.canvas.grid(column=1, row=0)
        
        self.canvas.bind('<Motion>', self.motion)
        
        self.annotation_canvas = tk.Canvas(window, width=640, height=360)
        
        self.detector = AT.Basic_Detector()
        self.catbox = tk.Listbox(window, height = 20, width=20)
        self.entbox = tk.Listbox(window, height = 20, width=20)
        
        for i, f in enumerate(self.detector.classnames):
            self.catbox.insert(i, f)
        self.catbox.bind('<<ListboxSelect>>', self.onselect)
        self.entbox.bind('<<ListboxSelect>>', self.entbox_Select)
        
        self.catbox.grid(column=0, row=0)
        self.entbox.grid(column=2, row=0)
        
        self.shown_ents = []
        self.is_playing = False
        self.control_frame = tk.Frame(window)
        self.control_frame.grid(row=1, column=1, columnspan=3)
        self.current_frame = 0
        self.restart_button = tk.Button(self.control_frame, text="|<", command=self.restart)
        self.back_5_button = tk.Button(self.control_frame, text="<<", command=lambda: self.back_frame(11))
        self.back_frame_button = tk.Button(self.control_frame, text="<", command=lambda: self.back_frame(2))
        self.play_button = tk.Button(self.control_frame, text="|>", command=self.play)
        self.current_ents = None
        self.restart_button.grid(column=0, row=1)
        self.back_5_button.grid(column=1, row=1)
        self.back_frame_button.grid(column=2, row=1)
        self.play_button.grid(column=3, row=1)
        self.cur_frame_entry = tk.Entry(self.control_frame, textvariable="0", width=5)
        self.cur_frame_entry.grid(column=2, row=0)
        
        
        self.entity_manager = Entity_Manager()
        
        
        menubar = tk.Menu(window)
        file = tk.Menu(menubar)
        annotation = tk.Menu(menubar)
        file.add_command(label="import video", command=lambda: self.import_video())
        file.add_command(label="quit", command=lambda: self.window.quit())
        
        annotation.add_command(label="Open Annotator", command=self.open_annotator)
        menubar.add_cascade(label = "File", menu=file)
        menubar.add_cascade(label="Tools", menu=annotation)
        root.config(menu=menubar)
        self.annotator = tk.PanedWindow(window)
        
        self.audio = pyaudio.PyAudio()
        self.framerate = 0
        
        self.refresh()
        
    def enhanced_entity(self, img, scale):
        shape = (round(img.shape[0]*scale), round(img.shape[1]*scale))
        if shape[0] > self.cur_img.shape[0]:
            scale = scale * 0.75
        img = cv2.resize(img, (shape[1], shape[0]))
        try:
            self.cur_img[10:10+img.shape[0], 10:10+img.shape[1]] = img
            # img = cv2.resize(img, (scaled_shape[1], scale))
            self.current_image = Image.fromarray(cv2.cvtColor(self.cur_img, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.canvas.image = self.photo
            return self.cur_img
        except Exception as e:
            traceback.print_exc()
            print(e)
            cv2.waitKey()
            
    def enhance_face(self, img, scale):
        img = cv2.resize(img, (img.shape[1]*scale, img.shape[0]*scale))
        try:
            self.cur_img[10:10+img.shape[0], 10:10+img.shape[1]] = img
            self.current_image = Image.fromarray(cv2.cvtColor(self.cur_img, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image = self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.canvas.image = self.photo
            return self.cur_img
        except Exception as e:
            traceback.print_exc()
            cv2.waitKey()
        
        
        
    def import_video(self):
        id = fd.askopenfilename(title="Please choose a file",
                                filetypes=(
                                ("mp4", "*.mp4"),
                                ("mp4 files", "*.mp4"),
                                ))
        self.vidcap = cv2.VideoCapture(id)
        _, i = self.vidcap.read()
        self.is_playing = True
        self.refresh(0)
        
    def back_frame(self, frames=2):
        if self.is_playing:
            self.is_playing = False
        cur_frame_number = self.vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        if cur_frame_number > frames-1:
            cur_frame_number -= frames
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, cur_frame_number)
            _, img = self.vidcap.read()
            if _:
                img = cv2.resize(img, (640, 360))
                self.cur_img = img
                self.current_ents = self.detector.scan_for_new_entities(img, .6) 
                img = self.draw_boxes(self.shown_ents, self.current_ents, img)
                self.current_image = Image.fromarray(cv2.cvtColor(img, cv2.COLOR_BGR2RGB))
                self.photo = ImageTk.PhotoImage(image=self.current_image)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.update_boxes(img)
            
    def get_next_frame(self, current_frame=None):
        if self.vidcap is None:
            return 
        if current_frame is not None:
            self.vidcap.set(cv2.CAP_PROP_POS_FRAMES, current_frame-1)
        _, img = self.vidcap.read()
        return img
    
    def remove_known_entities(self, img):
        for e in self.entity_manager.entities:
            for i in self.entity_manager.entities[e]:
                x, y, w, h = i.xywh[0], i.xywh[1], i.xywh[2], i.xywh[3]
                img[y:y+h, x:x+w] = 0
        return img
    
    def process_entity(self, original_image, entity, padding=10, return_boxed_image=False):
        x, y, w, h = entity.xywh[0]-padding if entity.xywh[0] > padding else 0, entity.xywh[1]-padding if entity.xywh[1] > padding else 0, entity.xywh[2]+padding, entity.xywh[3]+padding
        entity_space = original_image[y:y+h, x:x+w]
        entity.get_exp_1()
        volume = w*h
        frame = self.vidcap.get(cv2.CAP_PROP_POS_FRAMES)
        if entity.last_seen < (frame - 10):
            return
        d = self.detector.scan_for_new_entities(entity_space, .6)
        if entity.label in d.keys():
            if len(d[entity.label]) > 1:
                for e in d[entity.label]:
                    print("--!--!--")
                    found_entity_volume = e.xywh[2]* e.xywh[3]
                    percentage = found_entity_volume/volume
                    print(f"Entity: {entity.label}, volume: {volume}, entity volume: {found_entity_volume}, percentage: {percentage}")
                            
        if entity.label in d.keys():
            en = d[entity.label][0]
            x2, y2, w2, h2 = x+en.xywh[0], y+en.xywh[1], en.xywh[2], en.xywh[3]
            entity.xywh = (x2, y2, w2, h2)
            entity.last_seen = frame
            # print("Process image offset", (x, y, w, h), (entity.xywh))
            if return_boxed_image is True:
                boxed = original_image[(y2):(y2+h2), (x2):(x2+w2)]
                return boxed
            
    def process_entbox(self, ents, compact=True):
        self.entbox.delete(0, tk.END)
        for i, e in enumerate(ents.keys()):
            for i, p in enumerate(ents[e]):
                self.entbox.insert(i, f"{p.label}")
    
    def get_image_frame(self, current_frame=None):
        img = self.get_next_frame()
        frame = int(self.vidcap.get(cv2.CAP_PROP_POS_FRAMES))
        img = cv2.resize(img, (640, 360))
        self.cur_img = copy(img)
        print("FRAME", frame)
        print()
        if (frame % 5) != 1 and frame != 2:
            img = self.remove_known_entities(img)
        ents = self.detector.scan_for_new_entities(img, .6)
        self.current_ents = ents
        img = self.draw_boxes(ents, ["person"], self.cur_img, (0, 0, 255))
        return img
    
    def play(self):
        if self.is_playing == False:
            self.is_playing = True
            self.refresh(self.current_frame)
        else:
            self.current_frame = self.vidcap.get(cv2.CAP_PROP_POS_FRAMES)
            self.is_playing = False
            
    def open_annotator(self):
        top = tk.Toplevel()
        top.title("Annotator")
        self.anno_canvas = tk.Canvas(top, width=640, height=360)
        self.current_image = Image.fromarray(cv2.cvtColor(self.cur_img, cv2.COLOR_BGR2RGB))
        self.photo = ImageTk.PhotoImage(image=self.current_image)
        self.anno_canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
        self.anno_canvas.image = self.photo
        self.anno_canvas.grid(column=0, row=0)
        
        classListBox = tk.Listbox(top)
        for c in self.detector.classnames:
            classListBox.insert(-1, c)
    
    def draw_boxes(self, ent_list, cat_list, current_frame, color=(0, 0, 255)):
        for c in cat_list:
            if c in ent_list:
                for e in ent_list[c]:
                    x, y, w, h = e.xywh[0], e.xywh[1], e.xywh[2], e.xywh[3]
                    current_frame = cv2.rectangle(current_frame, (x, y), (x+w, y+h), color, 1, cv2.LINE_AA)
        return current_frame
    
    def refresh(self, current_frame=None, image=None):
        if image is None:
            frame = None
            if current_frame is None and self.vidcap is not None:
                frame = self.get_image_frame(current_frame)
            elif self.vidcap is not None and current_frame is not None:
                frame = self.get_image_frame()
            if self.is_playing:
                self.cur_frame_entry.configure(textvariable=self.vidcap.get(cv2.CAP_PROP_POS_FRAMES))
                self.current_image = Image.fromarray(cv2.cvtColor(frame, cv2.COLOR_BGR2RGB))
                self.photo = ImageTk.PhotoImage(image=self.current_image)
                self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
                self.window.after(15, self.refresh)
        else:
            self.current_image = Image.fromarray(cv2.cvtColor(image, cv2.COLOR_BGR2RGB))
            self.photo = ImageTk.PhotoImage(image=self.current_image)
            self.canvas.create_image(0, 0, image=self.photo, anchor=tk.NW)
            self.window.after(15, self.refresh)
            
    def update_current_ents(self):
        self.entbox.delete(0, tk.END)
        for i, e in enumerate(self.current_ents):
            for i, p in enumerate(e):
                self.entbox.insert(i, f"{p.label}")

if __name__ == "__main__":
    root = tk.Tk()
    
    tool = UI_Tool()
    vidcap = cv2.VideoCapture('./AutisTech/video/WF.mp4')
    
    tool.Start_Screen(root)
    
    root.mainloop()
        
        