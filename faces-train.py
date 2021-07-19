import os
import cv2
from PIL import Image
import numpy as np
import pickle

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
image_dir = os.path.join(BASE_DIR,"images")
print(image_dir)

face_cascade = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
print(dir (cv2.face))
face_recognizer = cv2.face.LBPHFaceRecognizer_create()

x_train=[]
y_labels=[]
label_ids={}
current_id=0

for root,dirs,files in os.walk(image_dir):
    for file in files:
        if file.endswith("png") or file.endswith("jpg"):
            path = os.path.join(root,file)
            label = os.path.basename(root).replace(" ", "-").lower()
            # label.append("unknown")
            # label = os.path.basename(os.path.dirname(path)).replace(" ","-").lower()
            # print(label,"\n",path)

            # give each known person folder a number ID
            if not label in label_ids:
                label_ids[label] = current_id
                current_id += 1
            id_ = label_ids[label]
            # print(label_ids)

            pil_image = Image.open(path).convert("L")   # GrayScale
            size=(550,550)
            final_image = pil_image.resize(size,Image.ANTIALIAS )
            image_array = np.array(final_image,"uint8")

            face_rects = face_cascade.detectMultiScale(image_array,scaleFactor=1.2,minNeighbors=6)

            for (x, y, w, h) in face_rects:
                # cv2.rectangle(face_img, (x, y), (x + w, y + h), (255, 255, 255), 10)
                rect = image_array[y:y+h,x:x+w]
                x_train.append(rect)
                y_labels.append(id_)

print(label_ids)
# print(x_train)
# print(y_labels)


# x_train.append(rect)
# y_labels.append(id_)

with open("labels.pickle","wb") as f:
    pickle.dump(label_ids,f)

face_recognizer.train(x_train,np.array(y_labels))
face_recognizer.save("trainner.yml")