import tensorflow as tf
print(tf.__version__)

import cv2
import numpy as np
import pickle
import time
from PyQt5.QtCore import QTimer
from mtcnn.mtcnn import MTCNN
from keras.models import load_model
from sklearn.preprocessing import LabelEncoder
from sklearn.preprocessing import Normalizer
from sklearn.svm import SVC
from PIL import Image
import os

class image_processor():
    def __init__(self):
        # call QWidget constructor
        # super().__init__()

        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        self.Flag_showResult=False
        self.timer = QTimer()

        self.OperatorName = ''
        self.ProjectName = ''

        # load face cascade classifier
        self.face_cascade = cv2.CascadeClassifier(self.upFolder + '/SourceCode/SourceFiles/ImPr/haarcascade_frontalface_default.xml')
        # if self.face_cascade.empty():
        #     QMessageBox.information(self, "Error Loading cascade classifier", "Unable to load the face	cascade classifier xml file")
        #     sys.exit()

        self.face_recognizer = cv2.face.LBPHFaceRecognizer_create()
        self.face_recognizer.read(self.upFolder + "/SourceCode/SourceFiles/ImPr/trainner.yml")

        self.embeding = np.load(self.upFolder + '/SourceCode/SourceFiles/IDEK_ImPr_Source/results/IDEK_faces-embeddings.npz')
        self.model_emb = load_model(self.upFolder + '/SourceCode/SourceFiles/IDEK_ImPr_Source/facenet_keras.h5')
        self.trainX, self.trainy, self.testX, self.testy = self.embeding['arr_0'], self.embeding['arr_1'], self.embeding['arr_2'], self.embeding['arr_3']

        # in_encoder = Normalizer(norm='l2')
        # self.trainX = in_encoder.transform(self.trainX)
        self.out_encoder = LabelEncoder()
        self.out_encoder.fit(self.trainy)
        self.trainy = self.out_encoder.transform(self.trainy)

        self.model_svc = SVC(kernel='rbf', probability=True)
        self.model_svc.fit(self.trainX, self.trainy)

        # self.fourcc = cv2.VideoWriter_fourcc(*'XVID')

        self.font = cv2.FONT_HERSHEY_SIMPLEX
        self.color = (255, 255, 255)
        self.stroke = 3

        self.labels = {}
        with open(self.upFolder + "/SourceCode/SourceFiles/ImPr/labels.pickle", "rb") as f:
            org_labels = pickle.load(f)
            self.labels = {v: k for k, v in org_labels.items()}

        self.ct = 1
        self.NumfacePic = 0
        self.NummotionPic = 0
        self.NumcapturedPic = 0
        self.NumThermalcapturedPic = 0

        self.NumcapturedVid1 = 0
        self.NumcapturedVid2 = 0
        
        self.ret1 = False
        self.ret2 = False


        self.timer.timeout.connect(self.getFrame1)
        time.sleep(0.2)
        self.timer.timeout.connect(self.getFrame2)
        # self.timer.timeout.connect(self.checkOption())

    def capture_frame(self):
        self.cap = cv2.VideoCapture(0,cv2.CAP_DSHOW)
        self.timer.start(20)

    def getFrame1(self):
        # self.ret, self.frame1 = self.cap.read()
        self.ct += 1

        self.ret = self.cap.grab()

        if self.ct % 1 == 0: # skip some frames
            self.ret1, self.frame1 = self.cap.retrieve()


    def getFrame2(self):
        # self.ret, self.frame2 = self.cap.read()

        # self.ct += 1
        self.ret = self.cap.grab()
        self.ret2 = False
        if self.ct % 1 == 0: # skip some frames
            self.ret2, self.frame2 = self.cap.retrieve()


    def capturedPic(self):
        self.NumcapturedPic +=1
        name = self.upFolder + '/Users/' + self.OperatorName +'/'+ self.ProjectName +'/Pictures/Normal_Camera/' +'frame_' +str(self.NumcapturedPic)+ '.jpg'
        cv2.imwrite(name,self.frame1)

    def capturedVid_Start(self):
        if self.NumcapturedVid2 == 0:
            self.NumcapturedVid1 +=1
            nameVid = self.upFolder + '/Users/' + self.OperatorName + '/' + self.ProjectName + '/Videos/Normal_Camera/' + 'vid_' + str(
                self.NumcapturedVid1) + '.avi'
            height, width, channel = self.frame1.shape
            print(height, width, channel)
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.out = cv2.VideoWriter(nameVid, self.fourcc, 5, (width,height))
            self.NumcapturedVid2 = 1
        self.out.write(self.frame1)

    def capturedVid_End(self):
        self.NumcapturedVid2 = 0
        self.out.release()

    # def ThermalcapturedPic(self):
    #     self.NumThermalcapturedPic +=1
    #     name = 'Users/' + self.OperatorName +'/'+ self.ProjectName + '/Pictures/Thermal_Camera/' + 'frame_' + str(self.ThermalcapturedPic) + '.jpg'
    #     # name = './Thermal_Captured_Pic/frame_' +str(self.ThermalcapturedPic)+ '.jpg'
    #     cv2.imwrite(name,self.frameT1)

    def get_embedding(self, model, face_pixels):
        # scale pixel values
        face_pixels = face_pixels.astype('float32')
        # standardize pixel values across channels (global)
        mean, std = face_pixels.mean(), face_pixels.std()
        face_pixels = (face_pixels - mean) / std
        # transform face into one sample
        samples = np.expand_dims(face_pixels, axis=0)
        # make prediction to get embedding
        yhat = model.predict(samples)
        return yhat[0]

    # detect face
    def detectFaces(self):

        # self.frame1 = self.frame1
        # convert frame to GRAY format
        gray = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2GRAY)

        # # detect rect faces
        # face_rects = self.face_cascade.detectMultiScale(gray, 1.3, 5)

        # create the detector, using default weights
        detector = MTCNN()
        # detect faces in the image
        results = detector.detect_faces(self.frame1)
        # print(results)
        # print( type(results))
        # print(len(results))
        # extract the bounding box from the first face
        face_rects = []
        for iface in range(len(results)):
            face_rects.append(results[iface]['box'])
            # bug fix
            face_rects[iface][0],face_rects[iface][1] = abs(face_rects[iface][0]),abs(face_rects[iface][1])
        # print(face_rects)
        # print(len(face_rects))

        # for all detected faces
        for (x, y, w, h) in face_rects:

            face = self.frame1[y:y+h, x:x+w]
            image = Image.fromarray(face)
            image = image.resize((160, 160))
            face = np.asarray(image)

            self.embeding = self.get_embedding(self.model_emb, face)

            # prediction for the face
            samples = np.expand_dims(self.embeding, axis=0)
            yhat_class = self.model_svc.predict(samples)
            yhat_prob = self.model_svc.predict_proba(samples)
            class_probability = yhat_prob[0, yhat_class[0]] * 100
            predicted_name = self.out_encoder.inverse_transform(yhat_class)

            if class_probability < 40:
                title = 'Unknown'
            else:
                title = predicted_name[0]

            print(yhat_prob * 100)
            print('Predicted: %s (%.3f) %s' % (predicted_name[0], class_probability,title))
            cv2.putText(self.frame1, title, (x, y - 6), self.font, 2, self.color, self.stroke, cv2.LINE_AA)

            # draw green rect on face
            cv2.rectangle(self.frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)



            # roi_gray = gray[y:y + h, x:x + w]
            # id_, conf = self.face_recognizer.predict(roi_gray)
            # if conf >= 45 and conf <= 85:
            #     # print(id_)
            #     # print(labels[id_])
            #     # print(conf)
            #     name = self.labels[id_]
            #     # else:
            #     #     name = "Unknown"
            #
            #     # name = labels[id_]
            #     cv2.putText(self.frame1, name, (x, y - 6), self.font, 2, self.color, self.stroke, cv2.LINE_AA)


            self.NumfacePic += 1
            name = self.upFolder +'/Users/' + self.OperatorName +'/'+ self.ProjectName + '/Pictures/Face/' + 'frame_' + str(self.NumfacePic) + '.jpg'

            # name = './Face_Detected/frame_' + str(self.NumfacePic) + '.jpg'
            cv2.imwrite(name, self.frame1)
            
        # # convert frame to RGB format
        # self.frame1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
        #
        # # get frame infos
        # # self.frame1.resize(300,200,3)
        # height, width, channel = self.frame1.shape
        # step = channel * width
        # # create QImage from RGB frame
        # qImg = QImage(self.frame1.data, width, height, step, QImage.Format_RGB888)
        # qImg =qImg.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        # # show frame in img_label
        # self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))


    def detectMotion(self):

        # self.frame1 = self.frame1
        diff = cv2.absdiff(self.frame1, self.frame2)
        gray = cv2.cvtColor(diff, cv2.COLOR_BGR2GRAY)

        # blur = cv2.GaussianBlur(gray, (51, 51), 0)
        blur = cv2.GaussianBlur(gray, (5, 5), 0)
        # blur = gray

        _, thresh = cv2.threshold(blur, 50, 255, cv2.THRESH_BINARY)

        dilated = cv2.dilate(thresh, None, iterations=3)
        contours, _ = cv2.findContours(dilated, cv2.RETR_TREE, cv2.CHAIN_APPROX_SIMPLE)

        for contour in contours:
            (x, y, w, h) = cv2.boundingRect(contour)

            if cv2.contourArea(contour) < 700:
                continue
            else:
                cv2.rectangle(self.frame1, (x, y), (x + w, y + h), (0, 255, 0), 2)
                self.NummotionPic +=1
                name = self.upFolder + '/Users/' + self.OperatorName +'/'+ self.ProjectName + '/Pictures/Motion/' + 'frame_' +str(self.NummotionPic) + '.jpg'
                # name = './Motion_Detected/frame_' +str(self.NummotionPic)+ '.jpg'
                cv2.imwrite(name,self.frame1)
                
            # cv2.putText(frame1,"Status: {}".format('Movement'),(0,0),cv2.FONT_HERSHEY_SIMPLEX,1,(0,0,255),2)
        #     cv2.putText(frame1, "Warning: {}".format('Water Drop'), (100, 100), cv2.FONT_HERSHEY_SIMPLEX, 2,
        #                 (0, 0, 255), 6)

        # self.showResult()

        # # convert frame to RGB format
        # self.frame1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
        #
        # # get frame infos
        # # self.frame1.resize(300, 200,3)
        # height, width, channel = self.frame1.shape
        # step = channel * width
        # # create QImage from RGB frame
        # qImg = QImage(self.frame1.data, width, height, step, QImage.Format_RGB888)
        # qImg = qImg.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        # # show frame in img_label
        # self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))


    def checkOption(self,motionCheck,faceCheck):

        self.Flag_showResult = False

        if self.ret1 and self.ret2:
            if motionCheck & faceCheck:
                self.detectFaces()
                self.detectMotion()
                self.Result()
                self.Flag_showResult = True
            elif motionCheck:
                self.detectMotion()
                self.Result()
                self.Flag_showResult = True
            elif faceCheck:
                self.detectFaces()
                self.Result()
                self.Flag_showResult = True
            else:
                self.Result()
                self.Flag_showResult = True

        return self.Flag_showResult

    def Result(self):
        # self.Flag_showResult = True
        return self.frame1



