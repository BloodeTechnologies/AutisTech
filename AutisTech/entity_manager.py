import entity
import torch
from torchvision import transforms as T
import cv2

class Entity_Manager():
    def __init__(self):
        super().__init__()
        self.entities = {}
        self.entity_glos = {}
        self.cos = torch.nn.CosineSimilarity(dim=1, eps=1e-6)
        self.totensor = T.ToTensor()
        self.total_entities = 0
    
    def get_entity_id(self, ent):
        print(hash(ent.type))
        
    def add_entity_dict(self, entities):
        for t in entities:
            for e in entities[t]:
                if not self.check_for_similar_entities(e.image, t, .6):
                    self.add_new_entity(e)
                
                
    def check_entities(self, base_image, padding =10, key=None):
        for cat in self.entities.keys():
            for i, ent in enumerate(self.entities[cat]):
                x, y, w, h = ent.xywh[0]-padding, ent.xywh[1]-padding, ent.xywh[2]+padding, ent.xywh[3]+padding
                img = base_image[y:y+h, x:x+w]
                pr = cv2.putText(ent.image, f"{cat}-{i}", (10, 10), cv2.FONT_HERSHEY_COMPLEX_SMALL, .5, (0, 0, 255), 1, cv2.LINE_AA)
                similarity = self.get_similarity(img, ent.image, 0.6)
                print(self.get_similarity(img, ent.image, 0.6))
                cv2.waitKey(0)
    
    def get_similarity(self, check_image, ent_image, threshold):
        check_gray = self.totensor(cv2.cvtColor(check_image, cv2.COLOR_RGB2GRAY))
        ent_gray = self.totensor(cv2.cvtColor(check_image, cv2.COLOR_BGR2GRAY))
        check_canny = cv2.Canny(cv2.cvtColor(check_image, cv2.COLOR_RGB2GRAY), 10, 150)
        # ent_canny = cv2.Canny(cv2.cvtColor(ent_image, cv2.COLOR_RGB2GRAY), 10, 150)
        try:
            sim = torch.cosine_similarity(check_gray, ent_gray, dim=1)
            print(sim.min().numpy())
            return sim.min().numpy()
        except Exception as e:
            print(e)
            return 0
    
    def check_for_similar_entities(self, check_image, label, tolerance):
        print("Checking for similar entities. tag:", label)
        assert label != "" and label is not None
    
        if label in self.entities.keys():
            for i in self.entities[label]:
                check_size = check_image.shape
                y_delta = abs(check_size[0] - i.image.shape[0])
                x_delta = abs(check_size[1] - i.image.shape[1])
                if x_delta > 30 or y_delta > 30:
                    continue
                return True
        return False
    
    def check_ents(self, image, tag, area_tolerance = 10):
        for ent in self.entities[tag]:
            y, x, w, h = ent.xywh[0]-area_tolerance, ent.xywh[1]-area_tolerance, ent.xywh[2]+area_tolerance, ent.xywh[3]+area_tolerance
            check_area = image[x:x+w, y:y+w]
            sim = self.get_similarity(check_area, ent.image, .7)
            print(sim)
        return False
    
    def get_list(self, entity_type:str):
        if entity_type in self.entities.keys():
            return self.entities[entity_type]
        else:
            return []
        
    def add_new_entity(self, ent:entity):
        t = ent.type
        if t not in self.entities.keys():
            self.entities[t] = []
        if self.check_for_similar_entities(ent.image, t, 10) == False:
            self.entities[t].append(ent)
            self.total_entities += 1
