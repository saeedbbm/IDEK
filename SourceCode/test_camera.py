
# import system module
import sys
import os

# import some PyQt5 modules
from PyQt5.QtWidgets import QApplication
from PyQt5.QtWidgets import QMessageBox
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QImage
from PyQt5.QtGui import QPixmap
from PyQt5.QtCore import QTimer

# import Opencv module
import cv2
import numpy as np
import pickle
import time

class MainWindow(QWidget):
    # class constructor
    def __init__(self):
        # call QWidget constructor
        super().__init__()

        self.cap = cv2.VideoCapture(0)
        # self.cap = cv2.VideoCapture("192.168.43.148")
        # self.cap = cv2.VideoCapture('http://idek:idek1234@192.168.43.148:80/html/')
        # cap = cv2.VideoCapture('rtsp://admin:idek1234@192.168.1.108:554/cam/realmonitor?channel=1&subtype=0')
        # self.cap = cv2.VideoCapture('http://192.168.43.148/')

        # # check ip
        # hostname = "192.168.43.148"  # example
        # response = os.system("ping -c 1 " + hostname)
        #
        # # and then check the response...
        # if response == 0:
        #     print(hostname, 'is up!')
        # else:
        #     print(hostname, 'is down!')

        # create a timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.getFrame1)
        self.timer.timeout.connect(self.checkOption)

        # self.timer.timeout.connect(self.detectFaces)
        # self.timer.timeout.connect(self.detectMotion)

    def checkOption(self):
            self.showResult()

    def showResult(self):
        self.frame1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
        height, width, channel = self.frame1.shape
        step = channel * width
        # create QImage from RGB frame
        qImg = QImage(self.frame1.data, width, height, step, QImage.Format_RGB888)
        qImg = qImg.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
        # show frame in img_label
        self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))

    def getFrame1(self):
        self.ret, self.frame1 = self.cap.read()
        # self.frame1.resize(300, 200, 3)

    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            # create video capture
            self.cap = cv2.VideoCapture(0)
            # start timer
            self.timer.start(20)
            # update control_bt text
            self.ui.control_bt.setText("Stop")

            print(self.ui.motion_check.isChecked(),self.ui.face_check.isChecked())
        # if timer is started
        else:
            # stop timer
            self.timer.stop()
            # release video capture
            self.cap.release()
            # update control_bt text
            self.ui.control_bt.setText("Start")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    # QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
    # create and show mainWindow
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())