import cv2
import numpy as np
import os, xml, time
import textclipper

class BloodeTechUI():
    
    def create_new_overlay(self, height, width):
        return np.zeros((height, width, 4), dtype=np.uint8)
    
    def __init__(self, img_height = 300, img_width = 300):
        super().__init__()
        self.process = {}
        self.process["name"] = False
        self.process["frame_rate"] = False
        self.img_height = img_height
        self.img_width = img_width
        self.reader = textclipper.texter()
        ## First, we need to create a blank image. Ultimately, we will draw all our UI onto this blank image
        ## and add it to the camera image later.
        
        self.ui_overlay_img = self.create_new_overlay(self.img_width, self.img_height)
        
        if self.ui_overlay_img is None:
            raise Exception ("Unknown error prevented creation of UI overlay. (Init BloodeTechUI)")
    
    def change_height_and_width(self, new_height, new_width):
           self.img_height = new_height
           self.img_width = new_width
    
    def get_processes(self):
        return list(p for p in self.process.keys() if self.process[p] == True)
    
    def alter_process(self, process):
        self.process[process] = not self.process[process]
    
    def add_user_name(self, line, xpos=0):
        self.ui_overlay_img = cv2.putText(self.ui_overlay_img, "Alastor Bloode", (0, 20 + (20*line)), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0, 1), 1, cv2.LINE_AA)
    
    def add_frame_rate(self, line):
        try:
            fr = fr = round(1.0/(time.time() - self.start_time))
        except:
            fr = "ERR"
        self.ui_overlay_img = cv2.putText(self.ui_overlay_img, f"Frame Rate: {fr}", (0, 20 + (20*line)), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0, 1), 1, cv2.LINE_AA)   
        
    def display_text(self, text, position:tuple, color=(255, 255, 255)):
        self.ui_overlay_img = cv2.putText(self.ui_overlay_img, text, (position[0], position[1]), cv2.FONT_HERSHEY_COMPLEX, .4, color, 1, cv2.LINE_AA)

    
    def draw_box_label(self, topLeftPos, label, color = (0, 255, 0)):
        self.ui_overlay_img = cv2.rectangle(self.ui_overlay_img, (topLeftPos[0]+10, topLeftPos[1]-2), (len(label)*8+topLeftPos[0]+15, topLeftPos[1]-18), color, 1, cv2.LINE_AA)
        self.ui_overlay_img = cv2.putText(self.ui_overlay_img, label, (topLeftPos[0]+12, topLeftPos[1]-4), cv2.FONT_HERSHEY_COMPLEX, .4, (255, 255, 255), 1, cv2.LINE_AA)
        
    def draw_box_xywh(self, xywh, label = None):
        x, y, w, h = int(xywh[0]), int(xywh[1]), int(xywh[2]), int(xywh[3])
        self.ui_overlay_img = cv2.rectangle(self.ui_overlay_img, (x, y), (x+w, y+h), (0, 255, 0, .2), 1, cv2.LINE_AA)
        if label is not None:
            self.draw_box_label((x, y), label)
            
    def draw_box_xyxy(self, xyxy, label=None):
        x1, y1, x2, y2 = xyxy[0], xyxy[1], xyxy[2], xyxy[3]
        self.ui_overlay_img = cv2.rectangle(self.ui_overlay_img, (x1, y1), (x2, y2), (0, 255, 0), 1, cv2.LINE_AA)
        if label is not None:
            self.draw_box_label((x1, y1), label)
            
    def timed_text_overlay(self, xywh, text, duration):
        start_time = time.time()
        endTime = 0
        x, y, w, h = xywh[0], xywh[1], xywh[2], xywh[3]
        time_delta = 0
        while time_delta < duration:
            time_delta = endTime - start_time
            self.ui_overlay_img = cv2.putText(self.ui_overlay_img, text, (25, 75), cv2.FONT_HERSHEY_SIMPLEX, .5, (0, 255, 0), 1, cv2.LINE_AA)            
            endTime = time.time()
            yield
            
    def display_image_box(self, image, pos):
        x, y = pos[0], pos[1]
        w, h = image.shape[0], image.shape[1]
        self.ui_overlay_img = cv2.rectangle(self.ui_overlay_img, (x, y), (x+w, y+h), (0, 255, 0), 1, cv2.LINE_AA)
        self.ui_overlay_img = cv2.addWeighted(image, 1, self.ui_overlay_img, .5,0)
        return self.ui_overlay_img
    
    def skew_correction(self, entity):
        
        lowpart = int(entity.image.shape[0]*.8)
        toppart = int(entity.image.shape[0]*.15)
        top_img = entity.image[lowpart:-1, 0:-1]
        btm_img = entity.image[0:toppart, 0:-1]
        
        
        gray = cv2.cvtColor(top_img, cv2.COLOR_BGR2GRAY)
        gray = cv2.bitwise_not(gray)
        
        thresh = cv2.threshold(gray, 0, 255,
                               cv2.THRESH_BINARY | cv2.THRESH_OTSU) [1]
        
        
        cv2.imshow("threshold", thresh)
        coords = np.column_stack(np.where(thresh > 0))
        angle = cv2.minAreaRect(coords)[0][0]/2.2
        
        if angle < -45:
            angle = -(90+angle)
        (h, w) = entity.image.shape[:2]
        center = (w // 2, h // 2)
        M = cv2.getRotationMatrix2D(center, angle, 1.0)
        rotated = cv2.warpAffine(entity.image, M, (w, h),
                                 flags = cv2.INTER_CUBIC, borderMode=cv2.BORDER_TRANSPARENT)
        return rotated
    
    def unsharp_mask(self, image, kernel_size=(5, 5), sigma=1.0, amount=1.0, threshold=0):
        """Return a sharpened version of the image, using an unsharp mask."""
        blurred = cv2.GaussianBlur(image, kernel_size, sigma)
        sharpened = float(amount + 1) * image - float(amount) * blurred
        sharpened = np.maximum(sharpened, np.zeros(sharpened.shape))
        sharpened = np.minimum(sharpened, 255 * np.ones(sharpened.shape))
        sharpened = sharpened.round().astype(np.uint8)
        if threshold > 0:
            low_contrast_mask = np.absolute(image - blurred) < threshold
            np.copyto(sharpened, image, where=low_contrast_mask)
        return sharpened
        
    def enhance_entity(self, entity, size, pos):
        for i, e in enumerate(entity):
            x, y = pos[0] + (i*size+10), pos[1]
            try:
                if e.image is not None:
                    e.image = self.unsharp_mask(e.image, amount=2)
                    e.image = self.skew_correction(e)
                    img = cv2.cvtColor(e.image, cv2.COLOR_RGB2RGBA)
                    sizeX = round(size* (e.image.shape[1]/e.image.shape[0]))
                    # self.display_image_box(img, pos)
                    entity_img = cv2.resize(img, (sizeX, size)) 
                    img2gray = cv2.cvtColor(entity_img, cv2.COLOR_BGR2GRAY)
                    ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)
                    mask = np.bitwise_not()
                    roi = self.ui_overlay_img[x:x+size, y:y+sizeX]   
                    self.ui_overlay_img = cv2.rectangle(self.ui_overlay_img, (y-1, x-1), (y+sizeX, x+size), (0, 255, 0), 1, cv2.LINE_AA)
                    self.ui_overlay_img = cv2.line(self.ui_overlay_img, (y+sizeX, x+size), (e.xywh[0], e.xywh[1]), (0, 255, 0), 1, cv2.LINE_AA)
                    # self.ui_overlay_img = cv2.addWeighted(img, 255, self.ui_overlay_img, 1, 1)
                    roi[np.where(mask)] = 0
                    roi += entity_img
            except Exception as ex:
                print(ex)
                print(e, e.image.shape)
           
            
    def get_ui_overlay(self):
        self.start_time = time.time()
        self.ui_overlay_img = self.create_new_overlay(self.img_width, self.img_height)
        active_processes = self.get_processes()
        for p in active_processes:
            if p == "name":
                self.add_user_name(1)
            if p == "frame_rate":
                self.add_frame_rate(3)
        return self.ui_overlay_img
    
    def combine_images(self, images:list):
        ## TODO:
        ## cv2.addWeighted adds the two images together straight up, which
        ## actually isn't what we want this to do. This needs to be
        ## altered to the correct protocol at some point.
        assert type(images) == list
        
        combination_image = self.get_ui_overlay()
        image_list = list(f for f in images if f is not None)
        for f in image_list:
            if type(f) == None:
                pass
            f = cv2.cvtColor(f, cv2.COLOR_RGB2RGBA)
            f = cv2.resize(f, (combination_image.shape[1], combination_image.shape[0]))
            if f is None:
                continue
            try:
                combination_image = cv2.addWeighted(f, 1, combination_image, .5, 0)
            except Exception as e:
                print(e)
                print(combination_image.shape, f.shape)
                print("STOP")     
            # w, h = combination_image.shape[0], combination_image.shape[1]
            # print(combination_image.shape[0])  
            # entity_img = cv2.resize(f, (w, h)) 
            # img2gray = cv2.cvtColor(entity_img, cv2.COLOR_BGR2GRAY)
            # ret, mask = cv2.threshold(img2gray, 1, 255, cv2.THRESH_BINARY)
            # roi = self.ui_overlay_img[0:w-1, 0:h-1]   
            # roi[np.where(mask)] = 0
            # roi += entity_img
                  
        return combination_image
    
    def draw_entity(self, entityList:dict):
        for e in entityList.keys():
            print("e", e)
            for i in entityList[e]:
                print(i.label)
                self.draw_box_xywh(i.xywh, i.label)
            
        return self.ui_overlay_img
    
        

if __name__ == "__main__":
    config_path = "./config files/"
    config = "config.xml"
    config_file = None
    if not os.path.exists(os.path.join(config_path, config)):
        with open (os.path.join(config_path, config), 'w') as file:
            config_file = file.write('"name":"True"')
    else:
        with open(os.path.join(config_path, config), 'w') as file:
            config_file = file
    
    BTUI = BloodeTechUI()
    
    while (True):
        ui = BTUI.get_ui_overlay()
        cv2.imshow("bloodetech ui", ui)
        
        if cv2.waitKey(1) & 0xFF == ord('q'): 

            break
        
        if cv2.waitKey(1) & 0xff == ord('w'):
            BTUI.alter_process("name")
    