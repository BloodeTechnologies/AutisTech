import cv2
import numpy as np
import torch
from torchvision import transforms as T

class Entity():
    def __init__(self, id, xywh, confidence, label="", type="", urgency=1):
        super().__init__()
        self.id, self.xywh, self.label, self.confidence, self.type, self.urgency = f"{id}_{label}", xywh, label, confidence, type, urgency
        self.tags = []
        self.image = None
        self.last_seen = 0
        self.tensor_transformer = T.ToTensor()
        
    def change_urgency(self, new_urgency, msg=""):
        if self.urgency != new_urgency:
            self.urgency = new_urgency
            
            
    def change_position(self, new_position:tuple, msg=""):
        assert len(new_position) == 4
    
        if self.xywh != new_position:
            self.xywh = new_position
        
            
    def compare_position(self, position_b, tolerance=32):
        for i in range(0, 4):
            n = abs(self.xywh[i] - position_b[i])
            if n > 32:
                return False
        return True
    
    def get_canny_image(self, threshold1=10, threshold2=150):
        canny = cv2.Canny(self.image, threshold1, threshold2)
        return canny
    
    def get_exp_1(self):
        exp = cv2.bitwise_not(self.image)
        exp2 = torch.sin(self.tensor_transformer(self.image))
        cv2.imshow("Exp", exp)
        cv2.imshow("exp2", exp2)
        cv2.imshow("og", self.image)
        cv2.waitKey(0)
    
    def __str__(self):
        return str(f"ID: {self.id}, {self.xywh}, {self.label}")