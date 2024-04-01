import cv2
import torch, torchvision
from torchvision import transforms as T
import os
import numpy as np
import traceback
from entity import Entity
from facenet_pytorch import MTCNN
import torch.nn.functional

class Basic_Detector():
    
    def __init__(self):
        super().__init__()
        self.device = "cuda" if torch.cuda.is_available() else "cpu"
        self.model = None
        while self.model == None:
            try:
                self.model = torchvision.models.detection.fasterrcnn_mobilenet_v3_large_320_fpn(pretrained=True)
            except:
                pass
            
        self.model.eval()
        self.classnames = self.get_classnames()
    
        
    def get_classnames(self):
        
        class_path = "AutisTech/classes.txt"
        path = os.path.join(os.curdir, class_path)
        with open(path,'r') as f:
            classnames = f.read().splitlines()
        return classnames
    
    def scan_for_face(self, image):
        mtcnn = MTCNN(keep_all=True)
        
        boxes, _ = mtcnn.detect(image)
        if boxes is not None:
            x, y, w, h = round(abs(boxes[0][0])), round(abs(boxes[0][1])), round(abs(boxes[0][2])), round(abs(boxes[0][3]))
            f = image[y-30:h+30, x-30:w+30]
            # transformer = T.ToTensor()
            # face_tensor = transformer(f)
            # h, w, c = face_tensor.shape
            # f_up = torch.nn.functional.interpolate(face_tensor, [h*2, w*2], mode='bilinear', align_corners=True)
            # # f_up = m(face_tensor)
            # f_up_img = torchvision.transforms.ToPILImage()(f_up)
            # f_up_image = np.array(f_up_img)
            # print(f_up_image.shape, f.shape, "|", image.shape)
            
            # cv2.imshow("f_up", f_up_image)
            # cv2.waitKey()
            return boxes[0]
        
        
    def scan_for_new_entities(self, image, threshold, entity_dict:dict = None):
        if image is None:
            return False
        return_dict = {}
        transformer = T.ToTensor()
        image = cv2.cvtColor(image, cv2.COLOR_RGBA2RGB)
        if entity_dict is not None:
            for k in entity_dict.keys():
                for e in entity_dict[k]:
                    entity_image = e.image
                    x, y, w, h = e.xywh[1], e.xywh[0], e.xywh[3], e.xywh[2]
                    image[x:x+w, y:y+h] = [0, 0, 0]
        image_tensor = transformer(image)
        with torch.no_grad():
            y_pred = self.model([image_tensor])
            
            bbox, scores, labels = y_pred[0]['boxes'], y_pred[0]['scores'], y_pred[0]['labels']
            indices = torch.nonzero(scores > threshold).squeeze(1)
            
            filtered_bbox = bbox[indices]
            filtered_scores = scores[indices]
            filtered_labels = labels[indices]
            # image = cv2.cvtColor(image, cv2.COLOR_RGB2BGRA)
            for label, box in zip(filtered_labels, filtered_bbox):
                box = box.numpy()
                x, y, w, h = round(box[0]), round(box[1]), round(box[2]) - round(box[0]), round(box[3]) - round(box[1])
                
                label = self.classnames[label-1]
                ent = Entity("",(x, y, w, h), 0, label, label)
                w2, h2 = x+w, y+h
                img = image[y:h2, x:w2]
                ent.image = image[y-10:h+y+10, x-10:w+x+10]
                faces = None
                if label == 'person':
                    try:
                        # pass
                        faces = self.scan_for_face(ent.image)
                    except Exception as e:
                        # cv2.imshow("error image", ent.image)
                        traceback.print_exception(e)
                        print(e)
                        print()
                    if faces is not None:
                        x, y, w, h = round(abs(faces[0])), round(abs(faces[1])), round(abs(faces[2])), round(abs(faces[3]))
                        ent.face = ent.image[y-10 if y > 10 else 0:h+10, x-10 if x > 10 else 0:w+10]
                if label not in return_dict.keys():
                    return_dict[label] = []
                    return_dict[label].append(ent)
                else:
                    return_dict[label].append(ent)
        return return_dict