import sys
import cv2
from time import sleep
from matplotlib import pyplot as plt

#sys.path.append("/usr/local/lib/python3.7.3/site-packages")
#path =r'/home/pi/Desktop/stop_sign1.jpg'
#img = cv2.imread(path)

#FRAME_WIDTH = 320
#FRAME_HEIGHT = 240
vidCapture = cv2.VideoCapture(0)
#vidCapture.set(cv2.CAP_PROP_FRAME_WIDTH,FRAME_WIDTH)
#vidCapture.set(cv2.CAP_PROP_FRAME_HEIGHT,FRAME_HEIGHT)
#fps = vidCapture.get(5)

    
while True:
    suc, img=vidCapture.read()



    img_gray=cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
    img_rgb=cv2.cvtColor(img, cv2.COLOR_BGR2RGB)

    xml_path= r'/home/pi/Desktop/stop_data.xml'
    stop_data = cv2.CascadeClassifier('stop_data.xml')
    found = stop_data.detectMultiScale(img_gray, minSize =(100, 100))
    amount_found = len(found)



    if amount_found != 0:
        for (x, y, width, height) in found:
            cv2.rectangle(img_rgb, (x,y), (x + height, y + width), (0, 255, 0), 5)
        
        
    cv2.imshow('img_rgb',img_rgb)
    cv2.waitKey(1000)
    