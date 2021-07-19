#
import sys
import os
import cv2
import numpy as np
import time
from PyQt5.QtWidgets import QApplication, QMessageBox, QWidget
from PyQt5.QtGui import QImage, QPixmap
from PyQt5.QtCore import QTimer, QObject

from fpdf import FPDF
from random import randint , seed
import random

from ui_window import *
from Image_Processing_old import image_processor
from Report_Creation import PDF

#controller
from controller_old import my_controller

class MainWindow(QWidget):
    def __init__(self):
        super().__init__()

        self.upFolder = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
        print(self.upFolder)
        
        self.ui = Ui_Form()

        self.ui.inputdialog()

        self.ui.setupUi(self)

        self.ImPr = image_processor()
        self.ImPr.OperatorName = self.ui.OperatorName_text.text()
        self.ImPr.ProjectName = self.ui.ProjectName_text.text()

        # controller
        self.control = my_controller()
        self.control.Motor_Position_stop()

        self.ReportNum = 0
        
        self.PositionCounterRatio = 2825 # Zarib counter to meter
        self.HeightCounterRatio = -42400
        self.AngleCounterRatio = 300
        
        self.PositionAccuracy = 0.1  # Deghat Tavaghof
        self.HeightAccuracy = 0.01
        self.AngleAccuracy = 10
        
        self.PositionAccuracy2 = 0.1*self.PositionCounterRatio #0.1m
        self.HeightAccuracy2 = 0.009*self.HeightCounterRatio 
        self.AngleAccuracy2 = 9*self.AngleCounterRatio
        
        self.AutoStart = 0
        self.AutoFlag=0
        self.NumThermalcapturedPic = 0
        self.NumcapturedVidT1 =0
        self.NumcapturedVidT2 = 0
        self.Flag_Vid_Recorder = 0
        self.Flag_VidT_Recorder = 0
        self.my_row = 0
        self.a1_if = 0
        self.a2_if = 0
        self.b1_if = 0
        self.b2_if = 0
        self.c1_if = 0
        self.c2_if = 0
        
        self.FirstTimeChange_H=0
        self.valueChange_H=0
        self.FirstTimeChange_A=0
        self.valueChange_A=0
        
        # Camera Home Sensor
#         self.flagDir_22 = 0
        
        #Click
            #UI_Report
        self.ui.btn_createReport.clicked.connect(self.createPDF)
            #UI_Camera
        self.ui.control_bt.clicked.connect(self.controlTimer)
        self.ui.start_thermal_btn.clicked.connect(self.start_thermal_func)
        # self.ui.camera_pic_btn.clicked.connect(self.ImPr.capturedPic)
        self.ui.camera_pic_btn.clicked.connect(lambda: self.ImPr.capturedPic(self.ui.InputPosition.text()))
        self.ui.thermal_pic_btn.clicked.connect(lambda: self.ThermalcapturedPic(self.ui.InputPosition.text()))
        self.ui.camera_vid_btn.clicked.connect(self.Vid_Recorder)
        self.ui.thermal_vid_btn.clicked.connect(self.VidT_Recorder)
            #UI_Table
        self.ui.btn_add.clicked.connect(self.ui.addRow)
        self.ui.btn_copy.clicked.connect(self.ui.copyRow)
        self.ui.btn_copy2.clicked.connect(self.ui.copyFunc)
        self.ui.btn_delete.clicked.connect(self.ui.deleteRow)
        self.ui.table.itemChanged.connect(self.ui.editActivated)    # could be used for alarm pic
            #UI_Setting
        self.ui.SETsave.clicked.connect(self.ui.SETfunc)
            #Save
        self.ui.btn_save.clicked.connect(self.ui.Save_Auto)
            #Go
        self.ui.btn_go.clicked.connect(self.GoFunc)
            #Controller_Auto
        self.ui.btn_Automatic.clicked.connect(self.AutoFunc)
            #Dialog
        self.ui.submit_btn.clicked.connect(self.ui.submit_func)

        #Timer
            #UI_Camera
        self.Timer_Vid_recorder = QTimer()
        self.Timer_Vid_recorder.timeout.connect(self.ImPr.capturedVid_Start)
        self.Timer_VidT_recorder = QTimer()
        self.Timer_VidT_recorder.timeout.connect(self.capturedVidT_Start)
        self.timerT = QTimer()
        self.timerT.timeout.connect(self.show_thermal_func)
            #UI_Automatic
        self.Autotimer = QTimer()
        self.Autotimer.timeout.connect(self.AutoMove)
            #UI_Alarm
        self.Alarmtimer = QTimer()
        self.Alarmtimer.start(20)
        self.Alarmtimer.timeout.connect(self.Alarm_Signal)


        # Position
        self.ui.PositionStart = 0
        self.ui.PositionCurrent = 0
        self.Position_encoder_counter_Value = 0
        self.enc_start = 0
        self.HoleNumber = 0
        self.HoleStatus = 0
        self.HPoEnd = 0
        self.HPoStart = 0
        self.HHeStatus = 0
        self.GHeStatus = 0
        
        self.HAnRight = 0
        self.HAnLeft = 0
        self.PreHAnRight = self.control.SensorArray[11]
        self.PreHAnLeft = self.control.SensorArray[11]
        
        self.flagDir_1 = 0
        self.Position_counter_Destination = 0
        self.timer_Position_counter = QTimer()
        self.timer_Position_counter.timeout.connect(self.Position_encoder_counter)
        self.timer_Position_counter.start(20)  # start the process of reading counter_encoder
        self.ui.upbutton1.clicked.connect(self.Position_JoyStick_up)
        self.ui.downbutton1.clicked.connect(self.Position_JoyStick_down)
        self.ui.stopbutton1.clicked.connect(self.Position_JoyStick_stop)

        self.ui.LED_up_btn.clicked.connect(self.LED_up)
        self.ui.LED_down_btn.clicked.connect(self.LED_down)
        self.LED_up_flag = 0
        self.LED_down_flag = 0
        

        self.ready = 0
#         self.PositionSpeed = 0
#         self.HeightSpeed = 0
#         self.AngleSpeed = 0
        self.ui.changeSpeedbutton.clicked.connect(self.SpeedisChanged)


        # Height
        self.TopPoint = 1.20 #0.65
        self.ui.HeightStart = self.TopPoint 
        self.ui.HeightCurrent = self.TopPoint
        self.Height_encoder_counter_Value = self.ui.HeightStart * self.HeightCounterRatio
        self.flagDir_2 = 0
        self.flag_Dir20=0
        self.Height_counter_Destination = 0
        self.timer_Height_counter = QTimer()
        self.timer_Height_counter.timeout.connect(self.Height_encoder_counter)
        self.timer_Height_counter.start(20)  # start the process of reading counter_encoder
        self.ui.upbutton2.clicked.connect(self.Height_JoyStick_up)
        self.ui.downbutton2.clicked.connect(self.Height_JoyStick_down)
        self.ui.stopbutton2.clicked.connect(self.Height_JoyStick_stop)

        # Angle
        self.ui.AngleStart = 0
        self.ui.AngleCurrent = 0
        self.Angle_encoder_counter_Value = self.ui.AngleStart * self.AngleCounterRatio
        self.flagDir_3 = 0
        self.flag_Dir30=0
        self.Angle_counter_Destination = 0
        self.timer_Angle_counter = QTimer()
        self.timer_Angle_counter.timeout.connect(self.Angle_encoder_counter)
        self.timer_Angle_counter.start(20)  # start the process of reading counter_encoder
        self.ui.rightbutton2.clicked.connect(self.Angle_JoyStick_up)
        self.ui.leftbutton2.clicked.connect(self.Angle_JoyStick_down)
        self.ui.stopbutton2.clicked.connect(self.Angle_JoyStick_stop)


        # Motors Timer
        self.timer_Motors_counter = QTimer()
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_1_up)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_1_down)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_1_stop)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_2_up)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_2_down)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_2_stop)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_3_right)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_3_left)
        self.timer_Motors_counter.timeout.connect(self.UI_Motor_3_stop)
        self.timer_Motors_counter.start(20)  # start the process of reading counter_encoder
        #CameraRoller
        self.CamRollerTimer0 = QTimer()
        self.CamRollerTimer0.timeout.connect(self.CamRoller0)
        self.CamRollerTimer0.start(10)
        
        self.CamRollerTimer = QTimer()
        self.CamRollerTimer.timeout.connect(self.CamRoller)
        self.CamRoller_Hflag = 0
        self.CamRoller_Pflag = 0
        self.CamRoller_Aflag = 0
        self.CamRoller_Hcnt = 0
        self.CamRoller_Acnt = 0
#         self.CamRollerTimer.start(20)
        self.cama1=0
        self.cama2=0
        self.cama3=0
        self.cama4=0
        
        # Other
        self.timer = QTimer()
        self.timer.timeout.connect(self.showResult)
        
        self.timer2 = QTimer()
        self.timer2.start(100)
        self.timer2.timeout.connect(self.updateFlags)

        #controller
        # self.timer2.timeout.connect(self.control.read_sensors)
        self.timer2.timeout.connect(self.control.SensorDataFunc)
        # self.timer2.timeout.connect(self.control.SensorDataFunc_old)

        self.ui.sensorValues = [randint(0, 100) for i in range(8)]
        self.timer2.timeout.connect(self.updateSensors)
        self.timer2.timeout.connect(self.ui.AlarmFunc)


        self.timer3 = QTimer()
        self.timer3.start(1)
        
        
        # PDF Creator Parameters
        # DATA
        self.df = np.array([[11, 100, 30, 14, 6], [15, 500, 40, 18, 6], [10, 900, 50, 5, 6], [10, 1200, 60, 5, 6],
                       [10, 1500, 45, 5, 6], [10, 1800, 40, 5, 6], [10, 2500, 30, 5, 6]])


        self.IntroTable = np.array([["Project Name:", self.ui.ProjectName_text.text() ,"User Name:", self.ui.OperatorName_text.text()],
                            ["Start point:", self.ui.StartPoint_text.text(),"Finish point:", self.ui.FinishPoint_text.text()],
                            ["Start time:", self.ui.dialog_start_time, "Finish time:", "10:21"],
                            ["O2 Alarm level:", "8", "CO2 Alarm level:", "30"],
                            ["CH4 Alarm level:", '4', "Humidity Alarm Level:", "80"],
                            ["Temperature Alarm level:", "50", "Battery Alarm level:", "20"],
                            ["Normal ambient temperature:", "40", "Normal internal temperature:", "20"],
                            ])


        self.SensorData = np.array([["ID", "Alarm", "Time", "Program", "Position", "Height", "Angle", "O2", "CO2", "CH4",
                                "Humidity", "Temperature", "Battery", "Voltage", "Amperage"],
                               ["1001", "9", "24", "1", "1002", "1.4", "240", "10", "20", "30", "40", "50", "60", "70",
                                "80"]])
    
    def CamRoller(self):
#         print("Sens1",self.control.SensorArray[9],self.control.SensorArray[11])
        if self.cama1 ==0:
#             print("\n\nGGG\n\n")
            
            self.control.Pre_tic_H = time.perf_counter()
            self.control.Motor_Height_stop()
#             print("Stop-121")
            self.control.Motor_Angle_stop()
            self.cama1 +=1

        # roll Height
        if self.control.SensorArray[9]==0:
            self.control.Motor_Height_up()
            self.flagDir_2 = 1
#             print("self.CamRoller_Acnt",self.CamRoller_Aflag)
        else:
            self.flagDir_2 = 0
#             print("Here101")
            self.control.Motor_Height_stop()
#             self.CamRoller_Hflag = 1
            self.ui.HeightStart =  self.TopPoint 
            self.ui.HeightCurrent =  self.TopPoint 
            self.Height_encoder_counter_Value = self.ui.HeightStart * self.HeightCounterRatio
            self.ui.InputHeight.setText(str(self.ui.HeightCurrent))
            self.control.Pre_tic_A = time.perf_counter()
#             print("FF",self.control.Pre_tic_A,self.control.tic_A)
            
        # roll Angle
        if self.control.SensorArray[9] == 1 :
            if self.control.SensorArray[11] == 0 :
                self.control.Motor_Angle_left()
                self.flagDir_3 = -1
#                 print("K1",self.flagDir_3)
#                 print("self.CamRoller_Hcnt",self.CamRoller_Hcnt)
            else:
                self.flagDir_3 = 0
#                 print("Stop-122")
                self.control.Motor_Angle_stop()
                self.CamRoller_Aflag = 1
                
                self.ui.AngleStart = 0
                self.ui.AngleCurrent = 0
                self.Angle_encoder_counter_Value = self.ui.AngleStart * self.AngleCounterRatio
                
                self.ui.InputAngle.setText(str(self.ui.AngleCurrent))
                
                self.CamRollerTimer.stop()

                self.control.Pre_tic_A = self.control.tic_A
                self.control.Pre_tic_H = self.control.tic_H
#                 print("TIK1",self.control.Pre_tic_A,self.control.tic_A)
                if self.cama2 == 0:
#                     time.sleep(6)
                    self.cama2 += 1
                 
                self.flagDir_1 = 1
                self.flagDir_2 = 0
                self.flagDir_3 = 0
                
                self.CamRoller_Pflag = 1
                self.CamRoller_Hflag = 0
                self.CamRoller_Aflag = 0
                
                
    def CamRoller0(self):
        if self.cama1 ==0:
            self.control.Motor_Height_stop()
            self.control.Motor_Angle_stop()
            self.cama1 +=1

        # roll Height
        if self.control.SensorArray[9]==0:
            self.control.Motor_Height_up()
            self.flagDir_2 = 1
#             print("self.CamRoller_Acnt",self.CamRoller_Aflag)
        else:
            self.flagDir_2 = 0
#             print("Here101")
            self.control.Motor_Height_stop()
#             self.CamRoller_Hflag = 1
            self.ui.HeightStart =  self.TopPoint 
            self.ui.HeightCurrent =  self.TopPoint 
            self.Height_encoder_counter_Value = self.ui.HeightStart * self.HeightCounterRatio
            
        # roll Angle
        if self.control.SensorArray[9] == 1 :
            if self.control.SensorArray[11] == 0 :
                self.control.Motor_Angle_left()
                self.flagDir_3 = -1
#                 print("K2",self.flagDir_3)
#                 print("self.CamRoller_Hcnt",self.CamRoller_Hcnt)
            else:
                self.flagDir_3 = 0
                self.control.Motor_Angle_stop()
                self.CamRoller_Pflag = 1
                self.CamRoller_Hflag = 1
                self.CamRoller_Aflag = 1
                self.ui.AngleStart = 0
                self.ui.AngleCurrent = 0
#                 print("*2")
                self.Angle_encoder_counter_Value = self.ui.AngleStart * self.AngleCounterRatio
                self.CamRollerTimer0.stop()
                if self.cama2 == 0:
#                     time.sleep(3)
                    self.cama2 += 1

    def Alarm_Signal(self):
#         if self.ImPr.PublicID2 != self.ui.ID2:
#             print("signal-",self.ui.ID2)
        
#         print("main1_ID2",self.ui.ID2)
        self.ImPr.PublicID2 = self.ui.ID2
        self.ImPr.PublicID3 = self.ui.ID3
        
        if self.ui.InputPosition.text() !='':
            self.ImPr.PublicPosition = float(self.ui.InputPosition.text())
        if self.ui.InputHeight.text() !='':
            self.ImPr.PublicHeight = float(self.ui.InputHeight.text())
        if self.ui.InputAngle.text() != '':
            self.ImPr.PublicAngle = float(self.ui.InputAngle.text())
            
        self.ImPr.AP_range = self.ui.AP_range
        self.ImPr.AH_range = self.ui.AH_range
        self.ImPr.AA_range = self.ui.AA_range
#         self.AlarmPosition = self.ui.AlarmPosition
        
        if self.ui.AlarmPicSignal == 1:
            self.ui.AlarmPicSignal = 0
            self.ImPr.capturedPicAlarm()
#             self.ImPr.capturedPicAlarm(self.ui.ID)
            
        if self.ImPr.FacePicSignal == 1:
            self.ImPr.FacePicSignal = 0
            print("main11_ID2",self.ui.ID2)
            self.ui.FaceMotionAddRow(333333)
            print("main12_ID2",self.ui.ID2)
            self.ImPr.PublicID2 = self.ui.ID2
            
        if self.ImPr.MotionPicSignal == 1:
            self.ImPr.MotionPicSignal = 0
            print("main21_ID2",self.ui.ID2)
            self.ui.FaceMotionAddRow(222222)
            print("main22_ID2",self.ui.ID2)
            self.ImPr.PublicID2 = self.ui.ID2
            
        if self.ImPr.OperatorPicSignal == 1:
            self.ImPr.OperatorPicSignal = 0
            self.ui.OperatorAddRow(444444)
            self.ImPr.PublicID3 = self.ui.ID3


    def SpeedisChanged(self):
        if self.ui.PositionSpeed_val.text() != '':
            pass
#             print("TT1",self.PositionCounterRatio , int(self.ui.PositionSpeed_val.text()), int(self.control.PositionSpeed))
#             self.PositionCounterRatio *= int(self.ui.PositionSpeed_val.text())/int(self.control.PositionSpeed) # Zarib counter to meter
#             print("TT2",self.PositionCounterRatio , int(self.ui.PositionSpeed_val.text()), int(self.control.PositionSpeed))
        if self.ui.HeightSpeed_val.text() != '':
            pass
#             self.HeightCounterRatio  *= int(self.ui.HeightSpeed_val.text())/int(self.control.HeightSpeed)
        if self.ui.AngleSpeed_val.text() != '':
            pass
#             self.AngleCounterRatio *= int(self.ui.AngleSpeed_val.text())/int(self.control.AngleSpeed)
        self.control.changeSpeed_func(self.ui.PositionSpeed_val.text(),self.ui.HeightSpeed_val.text(),self.ui.AngleSpeed_val.text())

    def createPDF(self):
        
        self.Position_JoyStick_stop()
        self.Height_JoyStick_stop()
        self.Angle_JoyStick_stop()
        
        self.pdf = PDF(orientation='P', unit='mm', format='A4')
        self.pdf.set_auto_page_break(0)
        # PDF Pages Creation
        self.AlarmArray = 50 * np.ones(self.ui.tableReport.rowCount())
        rows, cols = self.ui.tableReport.rowCount(), self.ui.tableReport.columnCount()

        self.chartArray = [[0] * cols for _ in range(rows)]
        table1 = self.ui.tableReport
#         print(table1)
#         print(table1.item(0, 0).text(),table1.item(0, 1).text(),table1.item(0, 2).text())

        count_Alarm = 0
        # Create Table for Charts
        for row in range(table1.rowCount()):

            # print("E ",table1.rowCount(), table1.item(row, 0))
            self.chartArray[row][0] = int(table1.item(row, 0).text())
            self.chartArray[row][1] = int(table1.item(row, 1).text())
            if self.chartArray[row][1] != 100:
                count_Alarm +=1
            self.chartArray[row][2] = (table1.item(row, 2).text())
            self.chartArray[row][3] = (table1.item(row, 3).text())
            self.chartArray[row][4] = (table1.item(row, 4).text())

            self.chartArray[row][5] = float(table1.item(row, 5).text()) # position
            self.chartArray[row][6] = float(table1.item(row, 6).text())
            self.chartArray[row][7] = float(table1.item(row, 7).text())

            self.chartArray[row][8] = (table1.item(row, 8).text())

            self.chartArray[row][9] = int(table1.item(row, 9).text())
            self.chartArray[row][10] = int(table1.item(row, 10).text())
            self.chartArray[row][11] = int(table1.item(row, 11).text())
            self.chartArray[row][12] = int(table1.item(row, 12).text())
            self.chartArray[row][13] = int(table1.item(row, 13).text())
            self.chartArray[row][14] = int(table1.item(row, 14).text())
        chartName = ['O2','Co2','CH4','Humidity','Temperature','Battery']
        chartTitle = ['Oxygen Gas','Carbon Dioxide Gas','Methane Gas','Humidity','Temperature','Battery']

        current_time = QtCore.QTime.currentTime()
        label_time = current_time.toString('hh:mm:ss')
        if self.ui.spring_radio.isChecked():
            season = 0
        elif self.ui.summer_radio.isChecked():
            season = 1
        elif self.ui.fall_radio.isChecked():
            season = 2
        elif self.ui.winter_radio.isChecked():
            season = 3
        else:
            self.ui.PDFseasonErrordialog()

        if self.ui.spring_radio.isChecked() or self.ui.summer_radio.isChecked() or self.ui.fall_radio.isChecked() or self.ui.winter_radio.isChecked():

            self.IntroTable = np.array(
                [["Project Name:", self.ui.ProjectName_text.text(), "User Name:", self.ui.OperatorName_text.text()],
                 ["Start point:", self.ui.StartPoint_text.text(), "Finish point:", self.ui.FinishPoint_text.text()],
                 ["Start time:", self.ui.dialog_start_time, "Finish time:", label_time],
                 ["O2 Alarm level:", self.ui.SettingArray[0][season], "CO2 Alarm level:", self.ui.SettingArray[1][season]],
                 ["CH4 Alarm level:", self.ui.SettingArray[2][season], "Humidity Alarm Level:", self.ui.SettingArray[3][season]],
                 ["Temperature Alarm level:", self.ui.SettingArray[4][season], "Battery Alarm level:", self.ui.SettingArray[5][season]]
                 ])

            for i in range(6):
                self.AlarmArray = int(self.ui.SettingArray[i][season]) * np.ones(self.ui.tableReport.rowCount())
                self.pdf.createChart(np.array([row[5] for row in self.chartArray]).reshape((table1.rowCount(), 1)),
                                     np.array([row[i + 9] for row in self.chartArray]).reshape((table1.rowCount(), 1)),
                                     chartTitle[i], self.AlarmArray, chartName[i], i+1,self.ui.OperatorName_text.text(),self.ui.ProjectName_text.text())

            table1Header = ['ID',"Alarm",'Program','Position','Height','Angle','Time','O2', 'Co2', 'CH4', 'Humidity', 'Temperature', 'Battery']

            SensorData_Header = ["ID", "Alarm", "Picture", "Video", "Program", "Position", "Height", "Angle", "Time", "O2", "Co2", "CH4", "Humidity", "Temperature", "Battery"]
            self.SensorData = [[0] * 15 for _ in range(count_Alarm)]

            SD_row= 0
            for row in range(table1.rowCount()):
                if self.chartArray[row][1] != 100:
                    self.SensorData[SD_row][:] = self.chartArray[row][:]
                    SD_row +=1

            self.pdf.pageOne(self.IntroTable,table1,table1Header)
            self.pdf.pageChart(self.IntroTable,chartName,self.ui.OperatorName_text.text(),self.ui.ProjectName_text.text())
            self.pdf.pageAlarm(self.SensorData,self.IntroTable,count_Alarm,self.ui.OperatorName_text.text(),self.ui.ProjectName_text.text())
            self.pdf.footer()
            self.ReportNum +=1

            self.pdf.output(self.upFolder + '/Users/' + self.ui.OperatorName_text.text() + '/' + self.ui.ProjectName_text.text() + '/Reports/report_' + str(self.ReportNum) + '.pdf', 'F')
            self.ui.outputdialog()

    def updateFlags(self):
        self.ui.deleteFlag = 0
        self.ui.cntAddFlag = 0
        self.ui.cntDeleteFlag = 0
        self.ui.addFlag = 0

    def AutoFunc(self):
 
        self.list = ['Program 1','Program 2','Program 3','Program 4','Program 5','Program 6','Program 7','Program 8','Program 9']
        if len(self.ui.combo.currentData()) > 0:
            self.list = self.ui.combo.currentData()

        print("LIST ", self.ui.table.rowCount())

        for i in range(self.ui.table.rowCount()):
            
            if float(self.ui.FinishPoint_text.text()) =='' or (float(self.ui.FinishPoint_text.text()) >= float(self.ui.table.item(self.ui.table.rowCount()-1,3).text())):
                self.AutoFinishPoint = float(self.ui.table.item(self.ui.table.rowCount()-1,3).text())
                self.AutoFinish = self.ui.table.rowCount()
                self.Auto_Finish_IP=1000
#                 print("Auto_Finisher",self.AutoFinish,self.Auto_Finish_IP,self.AutoFinishPoint)
                break
            elif float(self.ui.FinishPoint_text.text()) < float(self.ui.table.item(i,3).text()) :
                self.AutoFinishPoint = float(self.ui.FinishPoint_text.text())
                self.AutoFinish = i
                self.Auto_Finish_IP=1000+i #include
#                 print("Auto_Finisher",self.AutoFinish,self.Auto_Finish_IP,self.AutoFinishPoint)
                break
            
        for i in range(self.ui.table.rowCount()):
            if float(self.ui.StartPoint_text.text()) =='':
                self.AutoStartPoint = float(self.ui.table.item(0,3).text())
                self.AutoStart = 0
                self.Auto_Start_IP=1000+0+1
#                 print("Auto_Starter",self.AutoStart,self.Auto_Start_IP,self.AutoStartPoint)
#                 print("Going0 to: ",float(self.ui.table.item(0,3).text()))
                self.GoToStartFunc(float(self.ui.table.item(0,3).text()))
                break
            elif float(self.ui.StartPoint_text.text()) < float(self.ui.table.item(i,3).text()) :
                self.AutoStartPoint = float(self.ui.StartPoint_text.text())
                self.AutoStart = i
                self.Auto_Start_IP=1000+i+1
#                 print("Auto_Starter",self.AutoStart,self.Auto_Start_IP,self.AutoStartPoint)
#                 print("Going1 to: ",float(self.ui.StartPoint_text.text()))
                self.GoToStartFunc(float(self.ui.StartPoint_text.text()))
                break
        self.AutoFlag=1
#             print("FLAGS",(self.ui.PositionCurrent <= self.AutoStartPoint+self.PositionAccuracy) , (self.ui.PositionCurrent >= self.AutoStartPoint-self.PositionAccuracy))
#             if (self.ui.PositionCurrent <= self.AutoStartPoint+self.PositionAccuracy) and (self.ui.PositionCurrent >= self.AutoStartPoint-self.PositionAccuracy) :
#                 self.ready = 1

    def AutoFunc2(self):
#         time.sleep(3)
        self.AutoList = []
        self.AutoFlag=0
#         if self.ready == 1 :
        
        # find the current position IP
        for i in range(self.ui.table.rowCount()):
            if self.ui.PositionCurrent < float(self.ui.table.item(i,3).text()) :
#                 if self.ui.PositionCurrent+self.PositionAccuracy < float(self.ui.table.item(i,3).text()) :
                self.AutoStart = i
                self.Auto_Start_IP=1000+i+1
#                 print("11,Auto-Start-IP: ",self.Auto_Start_IP,self.ui.PositionCurrent)
#                 print("11,Start-Point: ",self.ui.StartPoint_text.text(),self.ui.FinishPoint_text.text() )
                break
            
#         print("AURO",self.AutoFinish,self.AutoStart)   
        for i in range(self.AutoFinish-self.AutoStart):
#         for i in range(self.ui.table.rowCount()-self.AutoStart):
            for j in range(len(self.list)):
#                 print("IF",self.ui.table.item(i+self.AutoStart,2).text() == self.list[j],self.ui.table.item(i+self.AutoStart,2).text() , self.list[j])
                if self.ui.table.item(i+self.AutoStart,2).text() == self.list[j]:
                    self.AutoList.append([float(self.ui.table.item(i+self.AutoStart,3).text()),float(self.ui.table.item(i+self.AutoStart,4).text()),float(self.ui.table.item(i+self.AutoStart,5).text()),self.ui.table.item(i+self.AutoStart,0).text(),self.ui.table.item(i+self.AutoStart,1).text(),self.ui.table.item(i+self.AutoStart,2).text(),1000+self.AutoStart+i+1])
                    break

        print("Auto List", self.AutoList)
        self.Autocnt = 0
        self.AutoDirection = 1
        self.Autotimer.start(20)
            

    def AutoMove(self):
        if self.AutoDirection == 1 :
            if (self.Autocnt) < (len(self.AutoList)):
                #  check to be stopped completely
#                 print("FLAGS",self.flagDir_1,self.flagDir_2,self.flagDir_3)
                if self.flagDir_1 == 0 and self.flagDir_2 ==0 and self.flagDir_3 == 0:
                    if self.Autocnt == 0:
                        self.my_row = self.Autocnt

                        self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
                        self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
                        self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
                        self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
                        self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
                        self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy

                    if self.Autocnt == 0:
                        self.my_row = self.Autocnt
                        self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
                        self.ui.PositionStart = self.ui.PositionCurrent
                        
#                         self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                         self.ui.HeightStart = self.ui.HeightCurrent
                        self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.TopPoint)
                        self.ui.HeightStart = self.TopPoint
#                         self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2]- self.ui.AngleCurrent)
#                         self.ui.AngleStart = self.ui.AngleCurrent
                        self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2]- 0)
                        self.ui.AngleStart = 0
                        
                        self.Autocnt += 1
                        
#                     print("\nAutcnt", self.Autocnt,self.CamRoller_Pflag,self.CamRoller_Hflag,self.CamRoller_Aflag)
#                     print("CCC",self.Height_counter_Destination,self.ui.HeightStart)
#                     print("BBB",self.Autocnt,self.ui.PositionCurrent,self.a1_if , self.a2_if , self.ui.HeightCurrent,self.b1_if ,self.b2_if , self.ui.AngleCurrent,self.c1_if ,self.c2_if)
#                     flagDir_22
                    # Check if Arrived
                    print("AARR", self.ui.PositionCurrent , self.a1_if , self.ui.PositionCurrent , self.a2_if , self.ui.HeightCurrent , self.b1_if , self.ui.HeightCurrent , self.b2_if , self.ui.AngleCurrent , self.c1_if , self.ui.AngleCurrent , self.c2_if)
                    if self.ui.PositionCurrent > self.a1_if and self.ui.PositionCurrent < self.a2_if and self.ui.HeightCurrent > self.b1_if and self.ui.HeightCurrent < self.b2_if and self.ui.AngleCurrent > self.c1_if and self.ui.AngleCurrent < self.c2_if:
#                     if self.ui.PositionCurrent >= self.a1_if and self.ui.PositionCurrent <= self.a2_if and self.ui.HeightCurrent >= self.b1_if and self.ui.HeightCurrent <= self.b2_if and self.ui.AngleCurrent >= self.c1_if and self.ui.AngleCurrent <= self.c2_if:
                        
#                         print("Here+1",self.AutoList[self.my_row],self.Autocnt)
#                         print("\n\nIF_Arrived+2",self.AutoList)
#                         print("\n\n")
                        self.Arrived(self.AutoList[self.my_row])
                        
                        self.my_row = self.Autocnt
                        self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
                        self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
                        self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
                        self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
                        self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
                        self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy
                        
                        self.b11_if = 0 - self.HeightAccuracy
                        self.b21_if = 0 + self.HeightAccuracy
                        self.c11_if = 0 - self.AngleAccuracy
                        self.c21_if = 0 + self.AngleAccuracy
                        
                        # Roll Camera
                        self.cama1=0
                        self.cama2 =0
                        self.CamRoller_Pflag = 0
                        self.CamRoller_Hflag = 0
                        self.CamRoller_Aflag = 0
                        self.flag_Dir20=1
                        self.flag_Dir30=1
                        self.CamRollerTimer.start(20)

                        
                        # Next Move
                        my_row = self.Autocnt
                        self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
                        self.ui.PositionStart = self.ui.PositionCurrent
                        
#                         self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                         self.ui.HeightStart = self.ui.HeightCurrent
                        self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.TopPoint)
                        self.ui.HeightStart = self.TopPoint
                        
#                         self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - self.ui.AngleCurrent)
#                         self.ui.AngleStart = self.ui.AngleCurrent
                        self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - 0)
                        self.ui.AngleStart = 0
                        
                        self.Autocnt += 1
                        
#                         print("GG",self.Height_counter_Destination ,-self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent),self.ui.HeightCurrent)
                        
#                         if self.ui.HeightCurrent > self.b11_if and self.ui.HeightCurrent < self.b21_if and self.ui.AngleCurrent > self.c11_if and self.ui.AngleCurrent < self.c21_if:
#                             my_row = self.Autocnt
#                             self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
#                             self.ui.PositionStart = self.ui.PositionCurrent
#                             self.Height_counter_Destination = self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                             self.ui.HeightStart = self.ui.HeightCurrent
#                             self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - self.ui.AngleCurrent)
#                             self.ui.AngleStart = self.ui.AngleCurrent
#                             self.Autocnt += 1
            else:
                self.AutoDirection = -1
                self.Autocnt -=1
#                 print("Auto+1",self.Autocnt,len(self.AutoList))
#                 self.AutoMove()
        elif self.AutoDirection == -1 :
            if (self.Autocnt) >= 0:
                #  check to be stopped completely
                if self.flagDir_1 == 0 and self.flagDir_2 ==0 and self.flagDir_3 == 0:
#                     print("Auto-11",self.Autocnt,len(self.AutoList)-1)
                    if self.Autocnt == (len(self.AutoList)-1):
                        self.my_row = self.Autocnt
                        
                        self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
                        self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
                        self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
                        self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
                        self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
                        self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy

                    if self.Autocnt == len(self.AutoList)-1:
                        self.my_row = self.Autocnt
                        self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
                        self.ui.PositionStart = self.ui.PositionCurrent
                        
#                         self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                         self.ui.HeightStart = self.ui.HeightCurrent
                        self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.TopPoint)
                        self.ui.HeightStart = self.TopPoint
                        
#                         self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2]- self.ui.AngleCurrent)
#                         self.ui.AngleStart = self.ui.AngleCurrent
                        self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2]- 0)
                        self.ui.AngleStart = 0
                        
                        self.Autocnt -= 1
                        
                    # Check if Arrived
#                     if self.ui.PositionCurrent >= self.a1_if and self.ui.PositionCurrent <= self.a2_if and self.ui.HeightCurrent >= self.b1_if and self.ui.HeightCurrent <= self.b2_if and self.ui.AngleCurrent >= self.c1_if and self.ui.AngleCurrent <= self.c2_if:
                    if self.ui.PositionCurrent > self.a1_if and self.ui.PositionCurrent < self.a2_if and self.ui.HeightCurrent > self.b1_if and self.ui.HeightCurrent < self.b2_if and self.ui.AngleCurrent > self.c1_if and self.ui.AngleCurrent < self.c2_if:
#                         print("AXE ", self.ui.PositionCurrent , self.a1_if , self.ui.PositionCurrent,self.a2_if , self.ui.HeightCurrent,self.b1_if , self.ui.HeightCurrent,self.b2_if , self.ui.AngleCurrent,self.c1_if , self.ui.AngleCurrent,self.c2_if)
                        
#                         print("Here-1",self.AutoList[self.my_row],self.Autocnt)
#                         print("IF_Arrived-2",self.AutoList)
    #                     self.Arrived(self.AutoList[self.my_row][3],self.AutoList[self.my_row][4],self.AutoList[self.my_row][5],self.AutoList[self.my_row][6])
                        self.Arrived(self.AutoList[self.my_row])
                        
                        self.my_row = self.Autocnt
                        self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
                        self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
                        self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
                        self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
                        self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
                        self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy
                        
                        self.b11_if = 0 - self.HeightAccuracy
                        self.b21_if = 0 + self.HeightAccuracy
                        self.c11_if = 0 - self.AngleAccuracy
                        self.c21_if = 0 + self.AngleAccuracy
                        
                        # Roll Camera
                        self.cama1=0
                        self.cama2 =0
                        self.CamRoller_Pflag = 0
                        self.CamRoller_Hflag = 0
                        self.CamRoller_Aflag = 0
                        self.flag_Dir20=1
                        self.flag_Dir30=1
                        self.CamRollerTimer.start(20)
                        
                        # Next Move
                        my_row = self.Autocnt
                        self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
                        self.ui.PositionStart = self.ui.PositionCurrent
            
#                         self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                         self.ui.HeightStart = self.ui.HeightCurrent
                        self.Height_counter_Destination = -self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.TopPoint)
                        self.ui.HeightStart = self.TopPoint
                        
#                         self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - self.ui.AngleCurrent)
#                         self.ui.AngleStart = self.ui.AngleCurrent
                        self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - 0)
                        self.ui.AngleStart = 0
                        self.Autocnt -= 1
                        
#                         if self.ui.HeightCurrent > self.b11_if and self.ui.HeightCurrent < self.b21_if and self.ui.AngleCurrent > self.c11_if and self.ui.AngleCurrent < self.c21_if:
#                         
#                             my_row = self.Autocnt
#                             self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
#                             self.ui.PositionStart = self.ui.PositionCurrent
#                             self.Height_counter_Destination = self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                             self.ui.HeightStart = self.ui.HeightCurrent
#                             self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - self.ui.AngleCurrent)
#                             self.ui.AngleStart = self.ui.AngleCurrent
#                             self.Autocnt -= 1
            else:
                self.AutoDirection = +1
                self.Autocnt +=1
#                 print("Auto-1",self.Autocnt,len(self.AutoList))
#                 self.AutoMove()

#         if (self.Autocnt) < (len(self.AutoList)):
#             #  check to be stopped completely
#             if self.flagDir_1 == 0 and self.flagDir_2 ==0 and self.flagDir_3 == 0:
#                 if self.Autocnt == 0:
#                     self.my_row = self.Autocnt
# 
#                     self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
#                     self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
#                     self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
#                     self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
#                     self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
#                     self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy
# 
#                 if self.Autocnt == 0:
#                     self.my_row = self.Autocnt
#                     self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
#                     self.ui.PositionStart = self.ui.PositionCurrent
#                     self.Height_counter_Destination = self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                     self.ui.HeightStart = self.ui.HeightCurrent
#                     self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2]- self.ui.AngleCurrent)
#                     self.ui.AngleStart = self.ui.AngleCurrent
#                     self.Autocnt += 1
#                     
#                 # Check if Arrived
#                 if self.ui.PositionCurrent > self.a1_if and self.ui.PositionCurrent < self.a2_if and self.ui.HeightCurrent > self.b1_if and self.ui.HeightCurrent < self.b2_if and self.ui.AngleCurrent > self.c1_if and self.ui.AngleCurrent < self.c2_if:
#                     self.my_row = self.Autocnt
#                     self.a1_if = self.AutoList[self.my_row][0] - self.PositionAccuracy
#                     self.a2_if = self.AutoList[self.my_row][0] + self.PositionAccuracy
#                     self.b1_if = self.AutoList[self.my_row][1] - self.HeightAccuracy
#                     self.b2_if = self.AutoList[self.my_row][1] + self.HeightAccuracy
#                     self.c1_if = self.AutoList[self.my_row][2] - self.AngleAccuracy
#                     self.c2_if = self.AutoList[self.my_row][2] + self.AngleAccuracy
# 
#                     print("IF_Arrived",self.AutoList[self.my_row])
# #                     self.Arrived(self.AutoList[self.my_row][3],self.AutoList[self.my_row][4],self.AutoList[self.my_row][5],self.AutoList[self.my_row][6])
#                     self.Arrived(self.AutoList)
#                     my_row = self.Autocnt
#                     self.Position_counter_Destination = self.PositionCounterRatio * (self.AutoList[self.my_row][0] - self.ui.PositionCurrent)
#                     self.ui.PositionStart = self.ui.PositionCurrent
#                     self.Height_counter_Destination = self.HeightCounterRatio * (self.AutoList[self.my_row][1] - self.ui.HeightCurrent)
#                     self.ui.HeightStart = self.ui.HeightCurrent
#                     self.Angle_counter_Destination = self.AngleCounterRatio * (self.AutoList[self.my_row][2] - self.ui.AngleCurrent)
#                     self.ui.AngleStart = self.ui.AngleCurrent
#                     self.Autocnt += 1
# 
#         else:
#             self.Autotimer.stop()


    def Arrived(self,ArrivedArray):
#         print("Arrived",self.ui.PositionStart,self.Position_counter_Destination,(self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio),(self.Position_counter_Destination-self.PositionAccuracy))
        print("@ destination: ",ArrivedArray)
        if int(ArrivedArray[3]) == 0 and int(ArrivedArray[4]) == 0: alarm = 100
        if int(ArrivedArray[3]) == 1 and int(ArrivedArray[4]) == 0: alarm = 110
        if int(ArrivedArray[3]) == 0 and int(ArrivedArray[4]) == 1: alarm = 101
        if int(ArrivedArray[3]) == 1 and int(ArrivedArray[4]) == 1: alarm = 111
        #
        # id-alarm-pic-vid-program-position-height-angle
        
        array=[ArrivedArray[6],alarm,ArrivedArray[3],ArrivedArray[4],ArrivedArray[5],ArrivedArray[0],ArrivedArray[1],ArrivedArray[2]]
        self.ui.Auto_Report(array)
        
        self.ImPr.PublicID1 = self.ui.ID1
        self.ImPr.capturedPicAuto()
        
#         time.sleep(1)
#         self.Height_counter_Destination = -self.HeightCounterRatio * (0 - self.ui.HeightCurrent)
        self.ui.HeightStart = self.ui.HeightCurrent
#         self.Angle_counter_Destination = self.AngleCounterRatio * (0- self.ui.AngleCurrent)
        self.ui.AngleStart = self.ui.AngleCurrent
#         time.sleep(3)
        

#         self.ImPr.PublicPosition = ArrivedArray[0]
#         self.ImPr.PublicHeight = ArrivedArray[1]
#         self.ImPr.PublicAngle = ArrivedArray[2]
#         self.ImPr.AP_range = self.ui.AP_range
#         self.ImPr.AH_range = self.ui.AH_range
#         self.ImPr.AA_range = self.ui.AA_range
# #         self.AlarmPosition = self.ui.AlarmPosition
#         
#         if self.ui.AlarmPicSignal == 1:
#             self.ui.AlarmPicSignal = 0
#             self.ImPr.capturedPicAlarm()

    def GoFunc(self):
        
        # Roll Camera
        self.cama1=0
        self.cama2 =0
        self.CamRoller_Pflag = 0
        self.CamRoller_Hflag = 0
        self.CamRoller_Aflag = 0
        self.flag_Dir20=1
        self.flag_Dir30=1
        self.CamRollerTimer.start(20)
        
#         print("TIK3",self.control.Pre_tic_A,self.control.tic_A)
#         self.flagDir_22 = 0

#         self.ui.HeightCurrent = 0
#         self.ui.AngleCurrent = 0
#         self.Height_encoder_counter_Value = 0
#         self.Angle_encoder_counter_Value = 0
        
        print( float(self.ui.enterPosition.text()) - self.ui.PositionCurrent, (float(self.ui.enterPosition.text()) - float(self.ui.PositionCurrent)), (float(self.ui.enterPosition.text()) , self.ui.PositionCurrent, float(self.ui.PositionCurrent)))
        if self.ui.enterPosition.text() == '':
            self.Position_counter_Destination = self.PositionCounterRatio * (0 - self.ui.PositionCurrent)
        else:
            self.Position_counter_Destination = self.PositionCounterRatio * (float(self.ui.enterPosition.text()) - self.ui.PositionCurrent)
        self.ui.PositionStart = self.ui.PositionCurrent
        
        print("EE", self.Position_counter_Destination)
        
        if self.ui.enterHeight.text() == '':
#             self.Height_counter_Destination = -self.HeightCounterRatio * (0 - self.ui.HeightCurrent)
            self.Height_counter_Destination = -self.HeightCounterRatio * (self.TopPoint - self.TopPoint)
        else:
#             self.Height_counter_Destination = -self.HeightCounterRatio * (float(self.ui.enterHeight.text()) - self.ui.HeightCurrent)
            self.Height_counter_Destination = -self.HeightCounterRatio * (float(self.ui.enterHeight.text()) - self.TopPoint)
#             print("GOFUNC",self.HeightCounterRatio , (float(self.ui.enterHeight.text())), (self.ui.HeightCurrent))
        self.ui.HeightStart = self.ui.HeightCurrent
        
        if self.ui.enterAngle.text() == '':
#             self.Angle_counter_Destination = self.AngleCounterRatio * (0 - self.ui.AngleCurrent)
            self.Angle_counter_Destination = self.AngleCounterRatio * (0 - 0)
        else:
#             self.Angle_counter_Destination = self.AngleCounterRatio * (float(self.ui.enterAngle.text()) - self.ui.AngleCurrent)
            self.Angle_counter_Destination = self.AngleCounterRatio * (float(self.ui.enterAngle.text()) - 0)
        self.ui.AngleStart = self.ui.AngleCurrent
        
#         print("GO_0",self.AngleCounterRatio , float(self.ui.enterAngle.text()) , self.ui.AngleCurrent)
#         print("GO_1 ",self.Position_counter_Destination,self.Height_counter_Destination,self.Angle_counter_Destination)
#         print("GO_2 ",self.CamRoller_Hflag,self.CamRoller_Aflag,self.CamRoller_Hcnt,self.CamRoller_Acnt )
#         print("FLAGS",self.flagDir_1,self.flagDir_2,self.flagDir_3)
        
#         if self.ui.enterHeight.text() == '':
#             self.Height_counter_Destination = self.HeightCounterRatio * (0 - self.ui.HeightCurrent)
#         else:
#             self.Height_counter_Destination = self.HeightCounterRatio * (float(self.ui.enterHeight.text()) - self.ui.HeightCurrent)
#         self.ui.HeightStart = self.ui.HeightCurrent
#         
#         if self.ui.enterAngle.text() == '':
#             self.Angle_counter_Destination = self.AngleCounterRatio * (0 - self.ui.AngleCurrent)
#         else:
#             self.Angle_counter_Destination = self.AngleCounterRatio * (float(self.ui.enterAngle.text()) - self.ui.AngleCurrent)
#         self.ui.AngleStart = self.ui.AngleCurrent

    def GoToStartFunc(self,position):
        
#         print("Sens2",self.control.SensorArray[9],self.control.SensorArray[11])
        # Roll Camera
        self.cama1=0
        self.cama2 =0
        self.CamRoller_Pflag = 0
        self.CamRoller_Hflag = 0
        self.CamRoller_Aflag = 0
        self.flag_Dir20=1
        self.flag_Dir30=1
        self.CamRollerTimer.start(20)
        
        self.ready = 0
        self.Position_counter_Destination = self.PositionCounterRatio * (position - self.ui.PositionCurrent)
        self.ui.PositionStart = self.ui.PositionCurrent
        print("Going2 to: ",float(self.ui.StartPoint_text.text()),position,self.ui.PositionStart,self.Position_counter_Destination)
#         print("Flag1",self.CamRoller_Pflag,self.CamRoller_Hflag,self.CamRoller_Aflag)
#         print("flag2",self.flagDir_1,self.flagDir_2,self.flagDir_3)
        
    def Position_JoyStick_up(self):
        self.ui.PositionStart = self.ui.PositionCurrent
        self.Position_counter_Destination = 1e10
        self.flagDir_1 = 1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         self.control.tic_P1 = time.perf_counter()

    def Position_JoyStick_down(self):
        self.ui.PositionStart = self.ui.PositionCurrent
        self.Position_counter_Destination = -1e10
        self.flagDir_1 = -1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         self.control.tic_P1 = time.perf_counter()
    
    def Position_JoyStick_stop(self):
#         self.ui.PositionStart = self.ui.PositionCurrent

        self.flagDir_1 = 0  # Counter Off
        self.control.Motor_Position_stop()
        self.Position_counter_Destination= 0 #-self.PositionAccuracy   # motor Off

#         self.flagDir_1 = 0              # Counter Off
#         self.CamRoller_Hflag = 0
#         self.CamRoller_Aflag = 0
#         self.control.toc_P1 = time.perf_counter()

    def Position_encoder_counter(self):
#         print("flag3",self.flagDir_1,self.flagDir_2,self.flagDir_3)
#         print("Flag4",self.CamRoller_Pflag,self.CamRoller_Hflag,self.CamRoller_Aflag)
        # Encoder + Counter
        # if self.control.SensorArray[7] == 0 and self.HoleStatus == 1:
        #     self.HoleStatus = 0
        #
        # if self.control.SensorArray[7] == 1 and self.HoleStatus == 0:
        #     self.HoleStatus = 1
        #     self.HoleNumber +=1
        #     self.enc_start = self.Position_encoder_counter_Value
        # self.Position_encoder_counter_Value = self.control.SensorArray[6]
        # self.ui.PositionCurrent = 10*self.HoleNumber + (self.Position_encoder_counter_Value - self.enc_start)/self.PositionCounterRatio
        # self.ui.InputPosition.setText(str(self.ui.PositionCurrent))
        # print("Hole: ",self.HoleNumber,self.ui.PositionCurrent)

        # Encoder Only
        if self.flagDir_1 ==1 or self.flagDir_1 ==-1:
            self.Position_encoder_counter_Value = self.control.SensorArray[6]
            self.ui.PositionCurrent = self.ui.PositionStart + float((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio)/self.PositionCounterRatio)
            self.ui.PositionCurrent = round(self.ui.PositionCurrent,3)
            # check = self.Position_encoder_counter_Value / self.PositionCounterRatio
            # check = round(check,3)
            # print("\nCheck 1: ", self.ui.PositionCurrent)
            # print("Check 2: ", check)
#             print("Encoder_P",self.Position_encoder_counter_Value,self.control.tic_P-self.control.toc_P)
#             print("TicToc",self.control.tic_P,self.control.toc_P)
#             print("TicToc1",self.control.tic_P1,self.control.toc_P1)
            
        self.ui.InputPosition.setText(str(self.ui.PositionCurrent))

        # if self.flagDir_1 ==1 or self.flagDir_1 ==-1:
        #     self.Position_encoder_counter_Value = self.control.SensorArray[6]
        #     self.ui.PositionCurrent = self.ui.PositionStart + float((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio)/self.PositionCounterRatio)
        #     self.ui.PositionCurrent = round(self.ui.PositionCurrent,3)
        # self.ui.InputPosition.setText(str(self.ui.PositionCurrent))

    def Height_JoyStick_up(self):
        self.ui.HeightStart = self.ui.HeightCurrent
        self.Height_counter_Destination = 1e10
        self.flagDir_2 = 1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         self.flagDir_1 = 0
#         self.flagDir_3 = 0

    def Height_JoyStick_down(self):
        self.ui.HeightStart = self.ui.HeightCurrent
        self.Height_counter_Destination = -1e10
        self.flagDir_2 = -1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         self.flagDir_1 = 0
#         self.flagDir_3 = 0

    def Height_JoyStick_stop(self):
#         self.ui.HeightStart = self.ui.HeightCurrent

        self.flagDir_2 = 0  # Counter Off
        self.control.Motor_Height_stop()
        self.Height_counter_Destination = 0#-self.HeightAccuracy #0  # motor Off
        
#         print("\n\nJoyStick\n\n")
#         print("LL ",self.CamRoller_Hflag,self.CamRoller_Aflag)

    def Height_encoder_counter(self):
        self.timerChange = 0
        
        
        if self.flagDir_2 == 1:
#             print("height1",self.ui.HeightCurrent,self.ui.HeightStart)
#             self.Height_encoder_counter_Value += 1
#             print("Encoder_H101",self.control.Pre_tic_H,self.control.tic_H)
            if self.control.Pre_tic_H == self.control.tic_H:
                self.FirstTimeChange_H = 0
            else:
                self.FirstTimeChange_H +=1
            self.valueChange_H = 0
#             print("Encoder_H102",self.FirstTimeChange,self.valueChange)
            if  self.control.Pre_tic_H != self.control.tic_H and self.FirstTimeChange_H >1:
                self.valueChange_H = self.control.tic_H-self.control.Pre_tic_H
#             print("SS", type(self.control.HeightSpeed))
            self.Height_encoder_counter_Value -= (self.valueChange_H *  int(self.control.HeightSpeed))
            self.control.Pre_tic_H = self.control.tic_H
            
            self.ui.HeightCurrent = self.ui.HeightStart + float((self.Height_encoder_counter_Value - self.ui.HeightStart * self.HeightCounterRatio) / self.HeightCounterRatio)
            self.ui.HeightCurrent = round(self.ui.HeightCurrent,3)
#             print("height2",self.ui.HeightCurrent,self.ui.HeightStart)
#             print("TIK4",self.control.Pre_tic_A,self.control.tic_A)
        
        if self.flagDir_2 == -1:
#             print("height1",self.ui.HeightCurrent,self.ui.HeightStart)
#             self.Height_encoder_counter_Value -= 1
#             print("Encoder_H201",self.control.Pre_tic_H,self.control.tic_H)
            if self.control.Pre_tic_H == self.control.tic_H:
                self.FirstTimeChange_H = 0
            else:
                self.FirstTimeChange_H +=1
            self.valueChange_H = 0
#             print("Encoder_H202",self.FirstTimeChange,self.valueChange)
            if  self.control.Pre_tic_H != self.control.tic_H and self.FirstTimeChange_H >1:
                self.valueChange_H = self.control.tic_H-self.control.Pre_tic_H    
            self.Height_encoder_counter_Value += (self.valueChange_H *  int(self.control.HeightSpeed))
            self.control.Pre_tic_H = self.control.tic_H
            
            self.ui.HeightCurrent = self.ui.HeightStart + float("{:.3f}".format(((self.Height_encoder_counter_Value - self.ui.HeightStart * self.HeightCounterRatio) / self.HeightCounterRatio)))
            self.ui.HeightCurrent = round(self.ui.HeightCurrent,3)

#             print("height2",self.ui.HeightCurrent,self.ui.HeightStart)
#             print("TIK5",self.control.Pre_tic_A,self.control.tic_A)
            
        
        self.ui.InputHeight.setText(str(self.ui.HeightCurrent))
#         print("Height",str(self.ui.HeightCurrent))
        
#         print("Encoder_H",self.Height_encoder_counter_Value,self.ui.HeightCurrent)
              
#         print("Encoder_H_10",self.FirstTimeChange,self.valueChange)
#         print("Encoder_H_11",self.Height_encoder_counter_Value,self.Height_encoder_counter_Value1)
#         print("Encoder_H_12",self.control.tic_H,self.control.Pre_tic_H)
#         print("22~",self.Height_encoder_counter_Value , self.ui.HeightStart*self.HeightCounterRatio,self.Height_counter_Destination+self.HeightAccuracy)


        # check = self.Height_encoder_counter_Value / self.HeightCounterRatio
        # check = round(check, 3)
        # print("\nCheck 3: ", self.ui.HeightCurrent)
        # print("Check 4: ", check)

    # Angle
    def Angle_JoyStick_up(self):
#         print("\n\nRight\n\n")
        # print("ZZ1",self.ui.AngleStart,self.ui.AngleCurrent)
        self.ui.AngleStart = self.ui.AngleCurrent
        # print("ZZ2", self.ui.AngleStart, self.ui.AngleCurrent)
        self.Angle_counter_Destination = 1e10
        self.flagDir_3 = 1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         print("K3",self.flagDir_3)
#         self.flagDir_2 = 0
#         self.flagDir_1 = 0
        # imagine camera is down
#         self.flagDir_22 = 0

    def Angle_JoyStick_down(self):
#         print("\n\nLeft\n\n")
        self.ui.AngleStart = self.ui.AngleCurrent
        self.Angle_counter_Destination = -1e10
        self.flagDir_3 = -1
        self.CamRoller_Pflag = 1
        self.CamRoller_Hflag = 1
        self.CamRoller_Aflag = 1
#         print("K4",self.flagDir_3)
#         self.flagDir_2 = 0
#         self.flagDir_1 = 0
        # imagine camera is down
#         self.flagDir_22 = 0

    def Angle_JoyStick_stop(self):
#         print("\n\nStop\n\n")
#         self.ui.AngleStart = self.ui.AngleCurrent

        self.flagDir_3 = 0  # Counter Off
        self.control.Motor_Angle_stop()
        self.Angle_counter_Destination = 0#-self.AngleAccuracy #0  # motor Off

        # Tell them camera is Up
#         self.flagDir_22 = 1

    def Angle_encoder_counter(self):

        if self.flagDir_3 == 1:
#             self.Angle_encoder_counter_Value += 100
            
            if self.control.Pre_tic_A == self.control.tic_A:
                self.FirstTimeChange_A = 0
            else:
                self.FirstTimeChange_A +=1
            self.valueChange_A = 0
#             print("Encoder_H102",self.FirstTimeChange,self.valueChange)
            if  self.control.Pre_tic_A != self.control.tic_A and self.FirstTimeChange_A >1:
                self.valueChange_A = self.control.tic_A-self.control.Pre_tic_A
#             print("\nKAKA",self.valueChange_A , self.control.AngleSpeed)
#             print("TIK6",self.control.Pre_tic_A,self.control.tic_A)
            self.Angle_encoder_counter_Value += (self.valueChange_A *  int(self.control.AngleSpeed))
            self.control.Pre_tic_A = self.control.tic_A
#             print("ZZZ",self.ui.AngleCurrent,self.Angle_encoder_counter_Value,self.ui.AngleStart * self.AngleCounterRatio)
            
#             print("Angle1",self.Angle_encoder_counter_Value1,self.Angle_encoder_counter_Value)
            
            self.ui.AngleCurrent = self.ui.AngleStart + float((self.Angle_encoder_counter_Value - self.ui.AngleStart * self.AngleCounterRatio) / self.AngleCounterRatio)
            self.ui.AngleCurrent = round(self.ui.AngleCurrent, 3)
        if self.flagDir_3 == -1:
#             self.Angle_encoder_counter_Value -= 100
            
            if self.control.Pre_tic_A == self.control.tic_A:
                self.FirstTimeChange_A = 0
            else:
                self.FirstTimeChange_A +=1
            self.valueChange_A = 0
#             print("Encoder_H102",self.FirstTimeChange,self.valueChange)
            if  self.control.Pre_tic_A != self.control.tic_A and self.FirstTimeChange_A >1:
                self.valueChange_A = self.control.tic_A-self.control.Pre_tic_A
#                 print("Totti",self.valueChange_A,self.control.tic_A,self.control.Pre_tic_A)
#             print("FF2",self.control.Pre_tic_A,self.control.tic_A)
#             print("KAKA2", self.valueChange_A*self.control.AngleSpeed,self.valueChange_A , self.control.AngleSpeed)
#             print("A12", self.Angle_encoder_counter_Value,- (self.ui.AngleStart * self.AngleCounterRatio),self.valueChange_A,self.control.tic_A,self.control.Pre_tic_A)
            
            self.Angle_encoder_counter_Value -= (self.valueChange_A *  int(self.control.AngleSpeed))
#             print("TIK7",self.control.Pre_tic_A,self.control.tic_A)
            self.control.Pre_tic_A = self.control.tic_A
#             print("A12", self.Angle_encoder_counter_Value,- (self.ui.AngleStart * self.AngleCounterRatio),self.valueChange_A,self.control.tic_A,self.control.Pre_tic_A)
            
#             print("XX",self.ui.AngleCurrent,self.Angle_encoder_counter_Value,self.ui.AngleStart * self.AngleCounterRatio)
            self.ui.AngleCurrent = self.ui.AngleStart + float((self.Angle_encoder_counter_Value - self.ui.AngleStart * self.AngleCounterRatio) / self.AngleCounterRatio)
            self.ui.AngleCurrent = round(self.ui.AngleCurrent, 3)
#             print("Angle2",self.ui.AngleStart , float((self.Angle_encoder_counter_Value - self.ui.AngleStart * self.AngleCounterRatio) / self.AngleCounterRatio),self.ui.AngleCurrent)
            
        self.ui.InputAngle.setText(str(self.ui.AngleCurrent))
#         print("Angle",str(self.ui.AngleCurrent))
        
        # check = self.Angle_encoder_counter_Value / self.AngleCounterRatio
        # check = round(check, 3)
        # print("\nCheck 5: ", self.ui.AngleCurrent)
        # print("Check 6: ", check)

    # Motors
    def UI_Motor_1_up(self):
        
        if self.CamRoller_Pflag == 1:#self.CamRoller_Hflag == 1 and self.CamRoller_Aflag == 1:
        
            # End:
            # Robot was moving forward toward The End and sees the sensor : stop
            if self.control.SensorArray[8] == 1 and self.HPoEnd == 0 :
                self.HPoEnd = 1
            # Robot was moving backward toward The Start and does not see the sensor : go
            if self.control.SensorArray[8] == 0 and self.HPoEnd == 1:
                self.HPoEnd = 0

            # Robot was moving forward toward The Start and does not see the sensor : go
            if self.control.SensorArray[8] == 0 and self.HPoStart == 1:
                self.HPoStart = 0
            
#             print("PES-P1 ",self.ui.PositionCurrent,self.ui.enterPosition.text(),self.Position_counter_Destination / self.PositionCounterRatio)
#             print("DES-P1 ",self.Position_encoder_counter_Value,self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio,self.Position_counter_Destination-self.PositionAccuracy*self.PositionCounterRatio,self.Position_counter_Destination+self.PositionAccuracy*self.PositionCounterRatio)
            
#             print("RR1",self.Position_counter_Destination > 0, self.control.SensorArray[8],self.HPoEnd)
            
            if self.Position_counter_Destination > 0 and self.HPoEnd == 0:
#                 print("II", (self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio),self.Position_counter_Destination,self.PositionAccuracy2)
                if ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) < self.Position_counter_Destination-self.PositionAccuracy2):
#                     print("PUP")

                    self.control.Motor_Position_up()
#                     self.control.Pre_tic_A = self.control.tic_A  #Priority
#                     print("A2",self.control.Pre_tic_A,time.perf_counter())
                    self.flagDir_1 = 1
                #Counter
                elif ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) >= self.Position_counter_Destination-self.PositionAccuracy2):
#                     print("\nPosition1 stopped")
                    self.control.Motor_Position_stop()
                    self.CamRoller_Aflag = 1
#                     if self.flagDir_3=0:
#                         self.control.Pre_tic_A =time.perf_counter()
#                     self.control.Pre_tic_A = self.control.tic_A #Priority
#                     print("A3",self.control.Pre_tic_A,time.perf_counter())
#                     self.flagDir_3 = 1
#                     print("K5",self.flagDir_3)
                    self.flagDir_1 = 0
#                     self.ui.PositionStart = self.ui.PositionCurrent
                    
                    if self.AutoFlag==1:
                        self.AutoFunc2()
                        
    #                 print("XAB",self.AutoFlag)
    #                 if self.AutoFlag==1:
    #                     print("XFLAGS",(self.ui.PositionCurrent <= self.AutoStartPoint+self.PositionAccuracy) , (self.ui.PositionCurrent >= self.AutoStartPoint-self.PositionAccuracy))
    #                     if (self.ui.PositionCurrent <= self.AutoStartPoint+self.PositionAccuracy) and (self.ui.PositionCurrent >= self.AutoStartPoint-self.PositionAccuracy) :
    #                         self.ready = 1
    #                         self.AutoFunc2()
            elif self.Position_counter_Destination > 0 and self.HPoEnd == 1:
                self.Position_counter_Destination = 0
                self.control.Motor_Position_stop()

    def UI_Motor_1_down(self):
        
        if self.CamRoller_Pflag == 1:
#         if self.CamRoller_Hflag == 1 and self.CamRoller_Aflag == 1:
            
            # Start:
            # Robot was moving backward toward The Start and sees the sensor : stop
            if self.control.SensorArray[8] == 1 and self.HPoStart == 0:
                self.HPoStart = 1
            # Robot was moving forward toward The Start and does not see the sensor : go
            if self.control.SensorArray[8] == 0 and self.HPoStart == 1:
                self.HPoStart = 0

            # Robot was moving backward toward The Start and does not see the sensor : go
            if self.control.SensorArray[8] == 0 and self.HPoEnd == 1:
                self.HPoEnd = 0

#             print("PES-P2 ",self.ui.PositionCurrent,self.ui.enterPosition.text(),self.Position_counter_Destination / self.PositionCounterRatio)
#             print("DES-P2 ",self.Position_encoder_counter_Value,self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio,self.Position_counter_Destination-self.PositionAccuracy*self.PositionCounterRatio,self.Position_counter_Destination+self.PositionAccuracy*self.PositionCounterRatio)
            
#             print("RR2",self.Position_counter_Destination < 0,self.control.SensorArray[8],self.HPoStart)
            
            if self.Position_counter_Destination < 0 and self.HPoStart == 0:
#                 print("II2", (self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio),self.Position_counter_Destination,self.PositionAccuracy2)
                if ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) > self.Position_counter_Destination+self.PositionAccuracy2):
                    self.control.Motor_Position_down()
                    self.flagDir_1 = -1
                    # Counter
                elif ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) <= self.Position_counter_Destination+self.PositionAccuracy2):
                    self.control.Motor_Position_stop()
                    self.CamRoller_Aflag = 1
#                     self.control.Pre_tic_A = self.control.tic_A
#                     if self.flagDir_3=0:
#                         self.control.Pre_tic_A =time.perf_counter()
#                     print("A4",self.control.Pre_tic_A)
                    self.flagDir_1 = 0
#                     self.flagDir_3 = 1
#                     print("K6",self.flagDir_3)
#                     self.ui.PositionStart = self.ui.PositionCurrent
                    
                    if self.AutoFlag==1:
                        self.AutoFunc2()
                        
            elif self.Position_counter_Destination < 0 and self.HPoStart == 1:
                self.Position_counter_Destination = 0
                self.control.Motor_Position_stop()
                
    def UI_Motor_1_stop(self):
         if self.CamRoller_Hflag == 1 and self.CamRoller_Aflag == 1:
    #         if ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) <= self.Position_counter_Destination-self.PositionAccuracy) or ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) >= self.Position_counter_Destination+self.PositionAccuracy):
    #             self.control.Motor_Position_stop()
    #             self.flagDir_1 = 0
#             print("Beta",self.Position_counter_Destination)
            if self.Position_counter_Destination == 0:
    #             if ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) == self.Position_counter_Destination):
#                 print("AlFa",self.Position_encoder_counter_Value , self.ui.PositionStart*self.PositionCounterRatio , self.Position_counter_Destination,self.PositionAccuracy)
                if ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) <= self.Position_counter_Destination-self.PositionAccuracy2) or ((self.Position_encoder_counter_Value - self.ui.PositionStart*self.PositionCounterRatio) >= self.Position_counter_Destination+self.PositionAccuracy2):
#                     print("Position2")
                    self.control.Motor_Position_stop()
                    self.CamRoller_Aflag = 1
#                     self.control.Pre_tic_A = self.control.tic_A
#                     if self.flagDir_3=0:
#                         self.control.Pre_tic_A =time.perf_counter()
#                     print("A5",self.control.Pre_tic_A)
                    self.flagDir_1 = 0
#                     self.flagDir_3 = 1
#                     print("K6",self.flagDir_3)
#                     self.ui.PositionStart = self.ui.PositionCurrent
                    

    def UI_Motor_2_up(self):
#         print("DCD",self.CamRoller_Hflag == 1 , self.CamRoller_Aflag ==1 )
#         print("This",self.CamRoller_Hflag, self.CamRoller_Aflag, self.flagDir_1,self.flagDir_3)
        if self.CamRoller_Hflag == 1:# and self.CamRoller_Aflag == 1:
#             print("myFlag1",self.flagDir_1 , self.flagDir_3 )
#             if self.flagDir_1 == 0 and self.flagDir_3 == 0:
#             print("DDD1",-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio),self.Height_counter_Destination-self.HeightAccuracy*self.HeightCounterRatio,self.Height_encoder_counter_Value , self.ui.HeightStart*self.HeightCounterRatio,self.Height_counter_Destination,self.HeightAccuracy*self.HeightCounterRatio)
#             print("H_Start", self.ui.HeightStart)
            # Top:
            # Robot was moving up and sees the sensor : stop
#                 print("Status1",self.control.SensorArray[9],self.control.SensorArray[10],self.HHeStatus,self.GHeStatus)
            if self.control.SensorArray[9] == 1 and self.HHeStatus == 0:
                self.HHeStatus = 1
            # Robot was moving up and does not see the sensor : go
            if self.control.SensorArray[9] == 0 and self.HHeStatus == 1:
                self.HHeStatus = 0

            # Robot was moving down and does not see the sensor : go
            if self.control.SensorArray[10] == 0 and self.GHeStatus == 1:
                self.GHeStatus = 0

            if self.Height_counter_Destination > 0 and self.HHeStatus == 0:
                self.GHeStatus =0
#                 print("DDD2",self.Height_encoder_counter_Value , self.ui.HeightStart*self.HeightCounterRatio,self.Height_counter_Destination,self.HeightAccuracy*self.HeightCounterRatio)
#                 print("PES-H1 ",self.ui.HeightCurrent,self.ui.enterHeight.text(),self.Position_counter_Destination / self.PositionCounterRatio)
#                 print("DES-H1 ",self.Height_encoder_counter_Value,-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio),self.Height_counter_Destination-self.HeightAccuracy*self.HeightCounterRatio,self.Height_counter_Destination+self.HeightAccuracy*self.HeightCounterRatio)
            
                if (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) < self.Height_counter_Destination+self.HeightAccuracy2):
                    # print("motor_2_up")
#                     print("\n\nMotor2 Up\n\n")

                    if self.flag_Dir20==1:
                        self.control.Pre_tic_H =time.perf_counter()
                        self.flag_Dir20 = 0
                        
                    self.control.Motor_Height_up()
                    self.flagDir_2 = 1
                elif (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) >= self.Height_counter_Destination+self.HeightAccuracy2):
                    # print("motor_2_up_stop")
#                     print("motor_2_up_stop", self.ui.HeightCurrent, self.ui.HeightStart + float("{:.3f}".format(((self.Height_encoder_counter_Value - self.ui.HeightStart * self.HeightCounterRatio) / self.HeightCounterRatio))))

                    # print(self.flagDir_2)
#                     print("Motor2 Stop")
                    self.control.Motor_Height_stop()
                    self.flagDir_2 = 0
#                         self.ui.HeightStart = self.ui.HeightCurrent
            if self.Height_counter_Destination > 0 and self.HHeStatus == 1:
                self.control.Motor_Height_stop()
                self.atTop()
                self.flagDir_2 = 0
#                     self.ui.HeightStart = self.ui.HeightCurrent
    def atTop(self):
        self.ui.HeightStart = self.TopPoint
        self.ui.HeightCurrent = self.TopPoint
        self.Height_encoder_counter_Value = self.ui.HeightStart * self.HeightCounterRatio
        
    def UI_Motor_2_down(self):
        if self.CamRoller_Hflag == 1:# and self.CamRoller_Aflag == 1:
#             print("~10",self.flagDir_1 , self.flagDir_3 )
#             if self.flagDir_1 == 0 and self.flagDir_3 == 0:
#             print("~20",self.control.SensorArray[9],self.control.SensorArray[10],self.HHeStatus,self.GHeStatus)
#             if self.flagDir_1 == 0:
            # Down:
            # Robot was moving down and sees the sensor : stop
            if self.control.SensorArray[10] == 1 and self.GHeStatus == 0:
                self.GHeStatus = 1
            # Robot was moving down and does not see the sensor : go
            if self.control.SensorArray[10] == 0 and self.GHeStatus == 1:
                self.GHeStatus = 0

            # Robot was moving up and does not see the sensor : go
            if self.control.SensorArray[9] == 0 and self.HHeStatus == 1:
                self.HHeStatus = 0
            
            if self.Height_counter_Destination < 0 and self.GHeStatus == 0:
                if float(self.ui.InputHeight.text()) <=0:
                    self.GHeStatus =1
#
#                 print("PES-H2 ",self.ui.HeightCurrent,self.ui.enterHeight.text(),self.Position_counter_Destination / self.PositionCounterRatio)
#                 print("DES-H2 ",self.Height_encoder_counter_Value,-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio),self.Height_counter_Destination-self.HeightAccuracy*self.HeightCounterRatio,self.Height_counter_Destination+self.HeightAccuracy*self.HeightCounterRatio)
            
                if (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) > self.Height_counter_Destination-self.HeightAccuracy2):


                    if self.flag_Dir20==1:
                        self.control.Pre_tic_H =time.perf_counter()
                        self.flag_Dir20 = 0
                    
#                     print("motor_2_down", self.ui.HeightCurrent, self.ui.HeightStart + (self.Height_encoder_counter_Value - self.ui.HeightStart * self.HeightCounterRatio) / self.HeightCounterRatio,self.Height_encoder_counter_Value , self.ui.HeightStart,self.HeightCounterRatio , self.Height_counter_Destination,self.HeightAccuracy2)
                    self.control.Motor_Height_down()
                    self.flagDir_2 = -1
                elif (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) <= self.Height_counter_Destination-self.HeightAccuracy2):
#                     print("motor_2_down_stop")
                    # print(self.flagDir_2)
#                         print("HERE5")
#                     print("motor_2_up_stop", self.ui.HeightCurrent, self.ui.HeightStart + (self.Height_encoder_counter_Value - self.ui.HeightStart * self.HeightCounterRatio) / self.HeightCounterRatio,self.ui.HeightStart ,self.Height_encoder_counter_Value , self.ui.HeightStart , self.HeightCounterRatio , self.HeightCounterRatio)
                    self.control.Motor_Height_stop()
                    self.flagDir_2 = 0
#                         self.flagDir_22 = 0
#                         self.ui.HeightStart = self.ui.HeightCurrent
            if self.GHeStatus == 1:
                self.control.Motor_Height_stop()
                self.flagDir_2 = 0
#                     self.ui.HeightStart = self.ui.HeightCurrent
                    
    def UI_Motor_2_stop(self):
        if self.CamRoller_Hflag == 1 and self.CamRoller_Aflag == 1:
            if self.Height_counter_Destination == 0:
#                 print("102~",-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) ,self.Height_counter_Destination-self.HeightAccuracy*self.HeightCounterRatio,self.Height_encoder_counter_Value , self.ui.HeightStart*self.HeightCounterRatio,self.Height_counter_Destination+self.HeightAccuracy*self.HeightCounterRatio)
                if (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) <= self.Height_counter_Destination-self.HeightAccuracy2) or (-(self.Height_encoder_counter_Value - self.ui.HeightStart*self.HeightCounterRatio) >= self.Height_counter_Destination+self.HeightAccuracy2):
    #                 pass
#                     print("\nMotor2 Stop")
                    self.control.Motor_Height_stop()
#                     self.control.Pre_tic_H =time.perf_counter()
                    self.flagDir_2 = 0
#                     self.ui.HeightStart = self.ui.HeightCurrent
                    # print("motor_2_stop")


    def UI_Motor_3_right(self):
        if self.CamRoller_Aflag == 1: #and self.CamRoller_Hflag == 1 
            # Check if motor_1 is stopped
#             if self.flagDir_1 == 0:
#             if self.flagDir_1 == 0 and  self.control.SensorArray[9]==0:
            # End:
            # Robot was rotating right toward and sees the sensor : stop
#                 print("ARight1",self.control.SensorArray[11] , self.HAnRight,self.PreHAnRight)
#             if self.control.SensorArray[11] == 1 and self.HAnRight == 0 and self.PreHAnRight == 0 and self.control.FirstTime_HAnRight>30:
            if self.control.SensorArray[11] == 1 and self.HAnRight == 0 and self.flagDir_3 == 1 and self.PreHAnRight == 0 and self.control.FirstTime_HAnRight>30:
                self.HAnRight = 1
                self.PreHAnRight = self.control.SensorArray[11]
            # Robot was rotating right and does not see the sensor : go
            if self.control.SensorArray[11] == 0 :#and self.HAnRight == 1:
                self.HAnRight = 0
                self.PreHAnRight = 0
            # Robot was rotating Left and does not see the sensor : go
            if self.control.SensorArray[11] == 0 :#and self.HAnLeft == 1:
                self.HAnLeft = 0
                self.PreHAnLeft = 0
                
#                 print("ARight2",self.control.SensorArray[11] , self.HAnRight,self.PreHAnRight)
            if self.Angle_counter_Destination > 0 and self.HAnRight == 0:
                
#                 print("PES-A1 ",self.ui.AngleCurrent,self.ui.enterAngle.text(),self.Angle_counter_Destination / self.AngleCounterRatio)
#                 print("DES-A1 ",self.Angle_encoder_counter_Value,(self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio),self.Angle_counter_Destination-self.AngleAccuracy*self.AngleCounterRatio,self.Angle_counter_Destination+self.AngleAccuracy*self.AngleCounterRatio)
            

                
                if ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) < self.Angle_counter_Destination-self.AngleAccuracy2):
#                     print("31-1",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                         print("KK11",self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                     print("KK21 Angle",(self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio)/self.AngleCounterRatio,(self.Angle_counter_Destination-self.AngleAccuracy)/self.AngleCounterRatio)
#                     print("motor_31_right",time.perf_counter())
                    
                    if self.flag_Dir30==1:
                        self.control.Pre_tic_A =time.perf_counter()
                        self.flag_Dir30 = 0
#                     print("31-10",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)

                    self.control.Motor_Angle_right()
                    self.flagDir_3 = 1
                elif ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) >= self.Angle_counter_Destination-self.AngleAccuracy2):
#                     print("31-2",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                         print("KK12",self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                     print("KK22",(self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio)/self.AngleCounterRatio,(self.Angle_counter_Destination-self.AngleAccuracy)/self.AngleCounterRatio)
#                         print("motor_31_up_stop")
                    # print(self.flagDir_3)
#                     print("Stop-11")
                    self.control.Motor_Angle_stop()
#                     self.atAngleHome()
                    self.CamRoller_Hflag = 1
#                     self.flagDir_2 = 1
                    self.flagDir_3 = 0
                    
#                         self.ui.AngleStart = self.ui.AngleCurrent
            if self.Angle_counter_Destination > 0 and self.HAnRight == 1:
#                 print("Stop-12")
                self.atAngleHome()
                self.control.Motor_Angle_stop()
                self.CamRoller_Hflag = 1
                self.flagDir_3 = 0
#                 self.flagDir_2 = 1
#                     self.ui.AngleStart = self.ui.AngleCurrent
                    
    def UI_Motor_3_left(self):
        if self.CamRoller_Aflag == 1: #and self.CamRoller_Hflag == 1 
#             if self.flagDir_1 == 0 :

#             if self.flagDir_1 == 0 and  self.control.SensorArray[9]==0:
            # End:
            # Robot was rotating right toward and sees the sensor : stop
#                 print("ALeft1",self.control.SensorArray[11] , self.HAnLeft,self.PreHAnLeft)
            if self.control.SensorArray[11] == 1 and self.HAnLeft == 0 and self.flagDir_3 == -1 and self.PreHAnLeft == 0 and self.control.FirstTime_HAnLeft>30:
                self.HAnLeft = 1
                self.PreHAnLeft = self.control.SensorArray[11] 
            # Robot was rotating right and does not see the sensor : go
            if self.control.SensorArray[11] == 0:# and self.HAnLeft == 1:
                self.HAnLeft = 0
                self.PreHAnLeft =0

            # Robot was rotating Left and does not see the sensor : go
            if self.control.SensorArray[11] == 0:# and self.HAnRight == 1:
                self.HAnRight = 0
                self.PreHAnRight =0

#                 print("ALeft2",self.control.SensorArray[11] , self.HAnLeft,self.PreHAnLeft)
            if self.Angle_counter_Destination < 0 and self.HAnLeft == 0 :
                
#                 print("PES-A2 ",self.ui.AngleCurrent,self.ui.enterAngle.text(),self.Angle_counter_Destination / self.AngleCounterRatio)
#                 print("DES-A2 ",self.Angle_encoder_counter_Value,(self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio),self.Angle_counter_Destination-self.AngleAccuracy*self.AngleCounterRatio,self.Angle_counter_Destination+self.AngleAccuracy*self.AngleCounterRatio)
            
                
                if ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) > self.Angle_counter_Destination+self.AngleAccuracy2):
#                     print("31-3",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                     print("motor_31_left")
                    
                    if self.flag_Dir30==1:
                        self.control.Pre_tic_A =time.perf_counter()
                        self.flag_Dir30 = 0
#                     print("31-30",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
                    
                    self.control.Motor_Angle_left()
                    self.flagDir_3 = -1
                elif ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) <= self.Angle_counter_Destination+self.AngleAccuracy2):
#                     print("31-4",self.Angle_encoder_counter_Value , self.ui.AngleStart*self.AngleCounterRatio , self.Angle_counter_Destination-self.AngleAccuracy)
#                         print("motor_31_left_stop")
                    # print(self.flagDir_3)
#                     print("Stop-15")
                    self.control.Motor_Angle_stop()
#                     self.atAngleHome()
                    self.CamRoller_Hflag = 1
                    self.flagDir_3 = 0
#                     self.flagDir_2 = 1
#                         self.ui.AngleStart = self.ui.AngleCurrent
            if self.Angle_counter_Destination < 0 and self.HAnLeft == 1:
#                 print("Stop-14")
                self.control.Motor_Angle_stop()
                self.CamRoller_Hflag = 1
                self.atAngleHome()
                self.flagDir_3 = 0
#                 self.flagDir_2 = 1
#                     self.ui.AngleStart = self.ui.AngleCurrent
                
    def atAngleHome(self):
        self.ui.AngleStart = 0
        self.ui.AngleCurrent = 0
#         print("*1")
        self.Angle_encoder_counter_Value = self.ui.AngleStart * self.AngleCounterRatio
        
    def UI_Motor_3_stop(self):
        if self.CamRoller_Hflag == 1 and self.CamRoller_Aflag == 1:
            if self.Angle_counter_Destination == 0:
#                 print("3~",self.Angle_encoder_counter_Value -self.ui.AngleStart*self.AngleCounterRatio, self.Angle_counter_Destination,self.AngleAccuracy*self.AngleCounterRatio)
                if ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) <= self.Angle_counter_Destination-self.AngleAccuracy2) or ((self.Angle_encoder_counter_Value - self.ui.AngleStart*self.AngleCounterRatio) >= self.Angle_counter_Destination+self.AngleAccuracy2):
#                     print("Stop-13")
                    self.control.Motor_Angle_stop()
                    self.CamRoller_Hflag = 1
#                     self.atAngleHome()
                    self.flagDir_3 = 0
                    
#                     self.flagDir_2 = 1
#                     self.ui.AngleStart = self.ui.AngleCurrent
                    # print("motor_3_stop")


    # Other
    def updateSensors(self):

#         self.ui.sensorValues[0] = randint(80, 100)
#         self.ui.sensorValues[1] = randint(10, 20)
#         self.ui.sensorValues[2] = randint(5, 10)
#         self.ui.sensorValues[3] = randint(20, 30)
#         self.ui.sensorValues[4] = randint(25, 30)
#         self.ui.sensorValues[5] = 82

        self.ui.sensorValues[0] = self.control.SensorArray[0]
        self.ui.sensorValues[1] = self.control.SensorArray[1]
        self.ui.sensorValues[2] = self.control.SensorArray[2]
        self.ui.sensorValues[3] = self.control.SensorArray[3]
        self.ui.sensorValues[4] = self.control.SensorArray[4]
        self.ui.sensorValues[5] = self.control.SensorArray[5]  #Volt
        self.ui.sensorValues[6] = self.control.SensorArray[12] #Temp Bat
        self.ui.sensorValues[7] = self.control.SensorArray[13] #Ampr
        
#         print("Main")
#         print("[O2,CO,CH, Hu, T, TB, Am, Vo]")
#         print(self.ui.sensorValues[0:5], self.ui.sensorValues[6], self.ui.sensorValues[7],  self.ui.sensorValues[5])
        
#         self.ui.sensorValues = [randint(0, 100) for i in range(8)]
        # print(self.sensorValues)

        self.ui.text_O2.setText(str(self.ui.sensorValues[0]))
        self.ui.text_Co2.setText(str(self.ui.sensorValues[1]))
        self.ui.text_CH4.setText(str(self.ui.sensorValues[2]))
        self.ui.text_Humidity.setText(str(self.ui.sensorValues[3]))
        self.ui.text_Temperature.setText(str(self.ui.sensorValues[4]))
        self.ui.text_BatTemp.setText(str(self.ui.sensorValues[6]))
#         print("GGG", self.ui.sensorValues[5])
        self.ui.text_BatVolt.setText(str((round(float(self.ui.sensorValues[5]),2))))
#         self.ui.text_BatVolt.setText(":.1f".format((float(self.ui.sensorValues[5]))))
#         print("GGG", self.ui.sensorValues[7])
#         self.ui.text_BatAmp.setText(":.1f".format(str(float(self.ui.sensorValues[7]))))
        self.ui.text_BatAmp.setText(str((round(float(self.ui.sensorValues[7]),2))))

        # print(self.ui.text_Temperature.text())

        # controller
#         sensor_val = my_controller.read_sensors(self.control)
# #         print(type(sensor_val) , sensor_val)
#
# #         self.ui.list_command2.addItem(sensor_val)
# #         self.ui.list_command2.insertItem(0,sensor_val)
#
#         self.ui.text_O2.setText(str(sensor_val[0]))
#         self.ui.text_Co2.setText(str(sensor_val[1]))
#         self.ui.text_CH4.setText(str(sensor_val[2]))
    
    
    def showResult(self):

        my_flag1 = image_processor.checkOption(self.ImPr, self.ui.motion_check.isChecked(),self.ui.face_check.isChecked())

        if my_flag1:
            self.frame1 = self.ImPr.Result()
            self.frame1 = cv2.cvtColor(self.frame1, cv2.COLOR_BGR2RGB)
            height, width, channel = self.frame1.shape
            step = channel * width
            # create QImage from RGB frame
            qImg = QImage(self.frame1.data, width, height, step, QImage.Format_RGB888)
            qImg = qImg.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
            # show frame in img_label
            self.ui.image_label.setPixmap(QPixmap.fromImage(qImg))

    # start/stop timer
    def controlTimer(self):
        # if timer is stopped
        if not self.timer.isActive():
            self.ImPr.capture_frame()
            self.timer.start(20)
            self.ui.control_bt.setText("Stop")

        # if timer is started
        else:
            self.timer.stop()
            self.ImPr.cap.release()
            self.ui.control_bt.setText("Start")
            
    def  LED_up(self):
        if self.LED_up_flag  == 0:
            self.LED_up_flag  = 1
            self.ui.LED_up_btn.setText("LED OFF")
            self.control.LED_up_on()
        else:
            self.LED_up_flag  = 0
            self.ui.LED_up_btn.setText("LED ON")
            self.control.LED_up_off()
            
    
    def  LED_down(self):
        if self.LED_down_flag  == 0:
            self.LED_down_flag  = 1
            self.ui.LED_down_btn.setText("LED OFF")
            self.control.LED_down_on()
        else:
            self.LED_down_flag  = 0
            self.ui.LED_down_btn.setText("LED ON")
            self.control.LED_down_off()
        
    
    def start_thermal_func(self):
        if not self.timerT.isActive():
            print("T")
            self.capT = cv2.VideoCapture(0)
            # self.capT = cv2.VideoCapture(2 , cv2.CAP_DSHOW)
            self.timerT.start(20)
            self.ui.start_thermal_btn.setText("Stop")
        else:
            self.timerT.stop()
            self.capT.release()
            self.ui.start_thermal_btn.setText("Start")
        
    def show_thermal_func(self):
        retT0, self.frame_T1 = self.capT.read()
        self.frame_T1 = cv2.rotate(self.frame_T1,cv2.ROTATE_180)
        if retT0:
            height, width, channel = self.frame_T1.shape
        
            dim = (4*width, 4*height)
            self.frame_T2 = cv2.resize( self.frame_T1, dim, interpolation = cv2.INTER_AREA)
            
            self.frame_T3 = cv2.cvtColor(self.frame_T1, cv2.COLOR_BGR2RGB)
            # create QImage from RGB frame
            step = channel * width
            qImgT = QImage(self.frame_T3.data, width, height, step, QImage.Format_RGB888)
            qImgT = qImgT.scaled(640, 480, QtCore.Qt.KeepAspectRatio)
            # show frame in img_label
            self.ui.image_label2.setPixmap(QPixmap.fromImage(qImgT))

    def ThermalcapturedPic(self,position):
        self.NumThermalcapturedPic +=1
        name = self.upFolder + '/Users/' + self.ImPr.OperatorName +'/'+ self.ImPr.ProjectName + '/Pictures/Thermal_Camera/' + 'frame' + str(self.NumThermalcapturedPic) +'_P'+position+ '.jpg'
        cv2.imwrite(name,self.frame_T2)

    def Vid_Recorder(self):
        print("AAA")
        print(self.Flag_Vid_Recorder)
        self.Flag_Vid_Recorder +=1
        if self.Flag_Vid_Recorder % 2 == 1:
            self.Timer_Vid_recorder.start(20)
            self.ui.camera_vid_btn.setText("Stop Recording")
        else:
            self.Timer_Vid_recorder.stop()
            self.ui.camera_vid_btn.setText("Start Recording")
            self.ImPr.capturedVid_End()


    def VidT_Recorder(self):
        print("TTT")
        print(self.Flag_VidT_Recorder)
        self.Flag_VidT_Recorder +=1
        if self.Flag_VidT_Recorder % 2 == 1:
            self.Timer_VidT_recorder.start(20)
            self.ui.thermal_vid_btn.setText("Stop Recording")
        else:
            self.Timer_VidT_recorder.stop()
            self.ui.thermal_vid_btn.setText("Start Recording")
            self.capturedVidT_End()
        
    def capturedVidT_Start(self):
        if self.NumcapturedVidT2 == 0:
            self.NumcapturedVidT1 +=1
            nameVid = self.upFolder + '/Users/' + self.ImPr.OperatorName + '/' + self.ImPr.ProjectName + '/Videos/Thermal_Camera/' + 'vid_' + str(self.NumcapturedVidT1) + '.avi'
            height, width, channel = self.frame_T2.shape
            self.fourcc = cv2.VideoWriter_fourcc(*'XVID')
            self.outT = cv2.VideoWriter(nameVid, self.fourcc, 10, (width,height))
            self.NumcapturedVidT2 = 1
        self.outT.write(self.frame_T2)
        
    def capturedVidT_End(self):
        self.NumcapturedVidT2 = 0
        self.outT.release()
        
if __name__ == '__main__':

    app = QApplication(sys.argv)
    # QApplication.setStyle(QtWidgets.QStyleFactory.create('Cleanlooks'))
    mainWindow = MainWindow()
    mainWindow.show()
    sys.exit(app.exec_())