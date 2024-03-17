import BloodeTechUI
import Camera_Control
import entity_manager
import AutisTech_OD
from entity import Entity
import cv2, time
import numpy as np
from cv2 import VideoWriter
import torch
from torchvision import transforms as T
import random

def check_for_new_entities(image, threshold = 0.8):
    entities = basic_detect0r.scan_for_new_entities(image, threshold, manager.entities)
    
    manager.add_entity_dict(entities)
      
def check_for_known_entity(current_frame, entity, threshold = 0.72, offset = 10):
    x1, y1, w, h = entity.xywh[1], entity.xywh[0], entity.xywh[3], entity.xywh[2]
    w = w+x1
    h = h+y1
    entity_area_image = current_frame[x1:w, y1:h]
    check = basic_detect0r.scan_for_new_entities(entity_area_image, threshold)
    if entity.type in check.keys():
        e = check[entity.type][0]
        
        x, y, w, h = y1+e.xywh[0], x1+e.xywh[1], e.xywh[2], e.xywh[3]
        entity.xywh = (x, y, w, h)
        entity.image = current_frame[x:h+x, y:w+y]
        entity.image = cv2.cvtColor(entity.image, cv2.COLOR_RGB2RGBA)
    else:
        pass    
    
if __name__ == "__main__":
    ui = BloodeTechUI.BloodeTechUI(640, 360)
    camera = Camera_Control.BloodeTechCameraController(640, 360)
    manager = entity_manager.Entity_Manager()
    basic_detect0r = AutisTech_OD.Basic_Detector()
    entity_layer = None
    frame_id = 0
    seconds = 0
    entities = None
    vidcap = cv2.VideoCapture('./AutisTech/video/WF.mp4')
    
    
    out = cv2.VideoWriter( 
        "output2.avi", 
        cv2.VideoWriter_fourcc(*'mp4v'), 
        10,
        (360,640)
        )
    
    success,image = vidcap.read()
    count = 0
    name = "output_walk.mp4"
    known_entities = {}
    cos = torch.nn.CosineSimilarity(dim=0)
    transformer = T.ToTensor()
    sizer = T.Resize((100, 100)) 
    ents = None
    
    while count < 200:
        # We need the alpha channel. Right now, it's only so we can match
        # the tensor of the UI images. Later, this could be used for additional
        # masking, as a big part of the point is to create a less
        # intense environment for users.
        
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        
        # Now, we are going to check for any new entities.
        for k in manager.entities.keys():
            manager.check_ents(k)
        entities = basic_detect0r.scan_for_new_entities(image, .8)
        # print(entities)
        if "car" in entities.keys():
            for c in entities['car']:
                m = manager.get_similarity(c.image, "car", 0.6)
                print("m", m)
                if m < .6:
                    manager.add_new_entity(c)
                # cv2.rectangle(image,
                #               (c.xywh[0], c.xywh[1]),
                #               (c.xywh[0] + c.xywh[2], c.xywh[1] + c.xywh[3]),
                #               (0, 0, 255),
                #               1,
                #               cv2.LINE_AA
                #               )
                # car_canny = cv2.Canny(c.image, 10, 150)
                # cv2.imshow("Car canny", car_canny)
                # ui.draw_box_xywh(c.xywh, 'car')
        ents = ui.draw_entity(manager.entities)
            
        final = ui.combine_images([image, ents])
        cv2.imshow("ui", final)
        code = cv2.waitKey(1)
        if code == ord('q'):
            break
        
        success,image = vidcap.read()
        
        
        
        
        
        # image = cv2.cvtColor(image, cv2.COLOR_RGB2RGBA)
        # st = time.time()
        # entities = basic_detect0r.scan_for_new_entities(image, .8)
        # et = time.time()
        # enhanced_layer = None
        # entity_layer = ui.draw_entity(entities)
        # if 'tv' in entities.keys():
        #     enhanced_layer = ui.enhance_entity(entities['tv'], 75, (10, 10))       
        # c = cv2.waitKey(1)
        # if c == ord('q'):
        #     break
        # if c == ord('w'):
        #     image = ui.combine_images([image, entity_layer, enhanced_layer])
        #     cv2.imwrite(f"output_image_{count}.jpg", image)
        # image = ui.combine_images([image, entity_layer, enhanced_layer])
        # # out.write(image)
        # cv2.imshow("Bloode Tech Display", image)
        # success,image = vidcap.read()
        # count += 1
    out.release()
    vidcap.release()
    # while True:
    #     start_time = time.time()
    #     cam = camera.Get_Camera_Image()
    #     if frame_id == 5:
    #         if camera.camera_active:
    #             entities = basic_detect0r.scan_for_new_entities(cam, .8)
    #             print(len(entities))
    #             if len(entities) > 0:
    #                 entity_layer=ui.draw_entity(entities)
    #                 ui.enhance_entity(entities[0], 50, (10, 10))
        
    #     if cv2.waitKey(1) == ord('q'):
    #         break
        
    #     elif cv2.waitKey(1) == ord('c'):
    #         print("Starting camera")
    #         ui.timed_text_overlay((10, 50, 100, 50), "Starting Camera", 2)
    #         ui.display_text("Starting Camera",(100, 100))
    #         if camera.camera_active == False:
    #             camera.Start_Camera()
    #         else:
    #             camera.Close_Camera()
    #     frame_id += 1
    #     if frame_id == 10:
    #         frame_id=0
        
    #     full = ui.combine_images([cam, entity_layer])
    #     cv2.imshow("Bloode Tech Display", full)
            
    #     end_time = time.time()
    #     seconds += end_time - start_time
    # print("Time in use:", round(seconds, 2))
        