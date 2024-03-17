import cv2
import numpy as np
import BloodeTechUI

class BloodeTechCameraController():
    def __init__(self, height:int, width:int):
        super().__init__()
        self.camera_active = False
        self.img_height = height
        self.img_width = width
    
    def Start_Camera(self):
        self.camera_active = True
        self.video = cv2.VideoCapture(0)
        self.video.set(cv2.CAP_PROP_FRAME_WIDTH, self.img_width)
        self.video.set(cv2.CAP_PROP_FRAME_HEIGHT, self.img_height)     
        
    def Close_Camera(self):
        print("Camera link closed")
        self.camera_active = False
    
    def Get_Camera_Image(self):
        while self.camera_active:
            ret, img = self.video.read()
            if img is not None:
                return img
        
if __name__ == "__main__":
    res_x = 320
    res_y = 240
    BT_C = BloodeTechCameraController(res_x, res_y)
    BT_UI = BloodeTechUI.BloodeTechUI(res_x, res_y)
    BT_C.Start_Camera()
    while BT_C.camera_active:
        img = BT_C.Get_Camera_Image()
        combined = BT_UI.combine_images([img])
        cv2.imshow("Combined_image", combined)
        
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        if cv2.waitKey(1) & 0xFF == ord('w'):
            BT_UI.alter_process("name")
        if cv2.waitKey(1) & 0xFF == ord('e'):
            BT_UI.process["frame_rate"] = not BT_UI.process["frame_rate"]
    
    
    