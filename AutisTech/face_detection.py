import os, cv2, torch
from facenet_pytorch import InceptionResnetV1, MTCNN
from tqdm import tqdm
from types import MethodType

def encode(img):
    print("Image type is:", type(img))
    res = resnet(torch.Tensor(img))
    return res

def detect_box(self, img, save_path=None):
    #detect faces
    batch_boxes, batch_probs, batch_points = self.detect(img, landmarks=True)
    if not self.keep_all:
        batch_boxes, batch_probs, batch_points = self.select_boxes(
            batch_boxes, batch_probs, batch_points, img, method=self.selection_method
        )
    faces = self.extract(img, batch_boxes, save_path)
    return batch_boxes, faces

def load_known_faces():
    print(os.listdir(os.curdir))
    print(f'Current directory = "{os.curdir}"')
    
def detect(cam=0, thresh=0.7):
    vdo = cv2.VideoCapture(cam)
    while vdo.grab():
        _, img0 = vdo.retrieve()
        batch_boxes, cropped_images = mtcnn.detect_box(img0)
        if cropped_images is not None:
            for box, cropped in zip(batch_boxes, cropped_images):
                x, y, x2, y2 = [int(x) for x in box]
                print(x, y, x2, y2)
                face = img0[x:x2, y:y2]
                if face is not None:
                    cv2.imshow("face", face)
                detect_dict = {}
                for k, v in all_people_faces.items():
                    detect_dict = (v - img_embedding).norm().item()
                min_key = min(detect_dict, key=detect_dict.get)
                
                if detect_dict[min_key] >= thresh:
                    min_key = 'Undetected'
                cv2.rectangle(img0, (x, y), (x2, y2), (0, 0, 255), 2)
                cv2.putText(
                    img0, min_key, (x+5, y+10),
                    cv2.FONT_HRESHEY_DUPLEX, 0.5, (255, 255, 255), 1)
                
        # cv2.imshow("output", img0)
        if cv2.waitKey(1) == ord('q'):
            cv2.destroyAllWindows()
            break
       
resnet = InceptionResnetV1(pretrained='vggface2').eval()
mtcnn = MTCNN(image_size=244, keep_all=True, thresholds=[0.4, 0.5, 0.5], min_face_size=60)
mtcnn.detect_box = MethodType(detect_box, mtcnn)
people_directory = "/AutisTech/saved_faces"
all_people_faces = {}

 
if __name__ == "__main__":
    load_known_faces()
    detect(0)

