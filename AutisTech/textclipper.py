import easyocr, os
import cv2
from PIL import Image
class texter():
    def __init__(self):
        super().__init__()
        self.reader = easyocr.Reader(['en'])
        
    def ReadText(self, image, detail=0):
        print(type(image))
        try:
            
            result = self.reader.readtext(image=image)
            print(result)
        except Exception as e:
            print(e)



if __name__ == "__main__":
    t = texter()
    reader = easyocr.Reader(['en'])
    path = "AutisTech/s1.jpeg"
    t.ReadText(reader, path)