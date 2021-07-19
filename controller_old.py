import RPi.GPIO as GPIO
from time import sleep
import time
from encoder import Encoder
from pwmServo import PWMServo
from random import randint
import serial
import board
import numpy as np

GPIO.setwarnings(False) #disable warnings
GPIO.setmode(GPIO.BCM)
        
class my_controller():
    def __init__(self):

        self.SensorArray = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0 , 1, 1]
        self.ser = serial.Serial('/dev/ttyACM0', 9600, timeout=1.0)
        self.ser.flush()
        self.readCnt=0
        self.readCnt2=0
        self.readTotal=5
        self.readArray = np.arange(8*self.readTotal).reshape(8,self.readTotal)
        self.readArray = self.readArray.astype('float64')
        
        self.LED_up = 9
        GPIO.setup(self.LED_up,GPIO.OUT)
        self.LED_down = 11
        GPIO.setup(self.LED_down,GPIO.OUT)
        
        
        self.toc_H=0
        self.tic_H=0
        self.Pre_tic_H = 0
        
        self.toc_A=0
        self.tic_A=0
        self.Pre_tic_A = 0
        
        self.FirstTime_HAnLeft =0
        self.FirstTime_HAnRight =0
        
        self.PositionSpeed = 6000
        self.HeightSpeed = 2000
        self.AngleSpeed = 2000
        
        # sensors
        self.Counter = 5   #Counter
        self.HomeRobot = 26  #Home Robot
        self.HeightUp = 13  #Home Pan # Camera Up
        self.HomeAngle = 19  #Position Tilt
        self.HeightDown = 22  #Ground   # Camera Down
#         self.sensor_6 = 2   #6

        GPIO.setup(self.Counter, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.HomeRobot, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.HeightUp, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.HomeAngle, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        GPIO.setup(self.HeightDown, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
#         GPIO.setup(self.sensor_6, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
        
        self.O2 = 90 #777
        self.CO2= 8 #777
        self.CH4 = 3#777
        self.Battery_Temp = 3#777
        self.Humidity = 3#777
        self.Temperature = 3#777
        self.EncValue = 0#777
        self.Battery_Amp = 0#777
        self.Battery_Volt = 5#777
    
        # Encoder
        self.encoder_1 = 17  #Ground
        self.encoder_2 = 27  #Ground
        # self.valueChanged
        self.EncVal = Encoder(self.encoder_2, self.encoder_1)
        
        # Motors
        self.ENB1 = 23
        self.DIR1=24
        self.ENB2= 12
        self.DIR2=16
        self.ENB3= 20
        self.DIR3=21
        GPIO.setup(self.ENB1,GPIO.OUT) # set ENB as an outpot/pin38
        GPIO.setup(self.DIR1,GPIO.OUT) # set DIR as an outpot/pin36
        GPIO.setup(self.ENB2,GPIO.OUT)# set ENB2 as an outpot/pin37
        GPIO.setup(self.DIR2,GPIO.OUT)# set DIR2 as an outpot/pin35
        GPIO.setup(self.ENB3,GPIO.OUT)# set ENB3 as an outpot/pin33
        GPIO.setup(self.DIR3,GPIO.OUT)# set DIR3 as an outpot/pin31
        
        self.DRV1 = 18
        self.DRV2=7
        self.DRV3=25
        self.Servo_Position = PWMServo(pin=self.DRV1)  # Main Motor
#         self.Servo_Position.pwm.start(1)
        self.Servo_Position.pwm.stop()
        GPIO.output(self.ENB1,0)
        self.Servo_Height = PWMServo(pin=self.DRV2)   # Camera Up/Down
#         self.Servo_Height.pwm.start(1)
        self.Servo_Height.pwm.stop()
        GPIO.output(self.ENB2,0)
        self.Servo_Angle = PWMServo(pin=self.DRV3)  # Camera Rotate
#         self.Servo_Angle.pwm.start(1)
        self.Servo_Angle.pwm.stop()
        GPIO.output(self.ENB3,0)
        
        
    def SensorDataFunc(self):

        if self.ser.in_waiting > 0:
#             line = self.ser.readline().decode('utf-8').rstrip()
#             serData = line.split(',')
            
            line = self.ser.readline().decode('utf-8').rstrip()
            sleep(0.03)
            data_left = self.ser.inWaiting()  # check for remaining byte
            line += self.ser.read(data_left).decode('utf-8').rstrip()
            serData = line.split(',')
        
#             print("raw", line)
#             print("seperated",serData, serData[6], float((1.4*float(serData[6]))))
            
            if self.readCnt != self.readTotal:
                self.readArray[0,self.readCnt] = randint(81, 83)
                self.readArray[1,self.readCnt] = float(float(serData[0]))
                self.readArray[2,self.readCnt] = float(float(serData[1]))
                self.readArray[3,self.readCnt] = float(float(serData[3]))
                self.readArray[4,self.readCnt] = float(float(serData[4])/3)
                self.readArray[5,self.readCnt] = float(float(serData[5])/3)
                self.readArray[6,self.readCnt] = float(abs(1.3*float(serData[6])))
                self.readArray[7,self.readCnt] = float(float(serData[7])/18.5)
                self.readCnt +=1
            if self.readCnt == self.readTotal:
                self.readArray[0,self.readCnt2] = randint(81, 83)
                self.readArray[1,self.readCnt2] = float(float(serData[0]))
                self.readArray[2,self.readCnt2] = float(float(serData[1]))
                self.readArray[3,self.readCnt2] = float(float(serData[3]))
                self.readArray[4,self.readCnt2] = float(float(serData[4])/3)
                self.readArray[5,self.readCnt2] = float(float(serData[5])/3)
                self.readArray[6,self.readCnt2] = float(abs(1.3*float(serData[6])))
#                 print("TT", self.readArray[6,self.readCnt2] , float((1.4*float(serData[6]))))
                self.readArray[7,self.readCnt2] = float(float(serData[7])/18)
                self.readCnt2 +=1
                
                if self.readCnt2 == 5:
                    self.readCnt2 = 0
                    
                self.O2 = int(np.average(self.readArray[0,:]))
                self.Battery_Temp = int(np.average(self.readArray[1,:]))
                self.Temperature = int(np.average(self.readArray[2,:]))
                self.Humidity = int(np.average(self.readArray[3,:]))
                self.CO2 = int(np.average(self.readArray[4,:]))
                self.CH4 = int(np.average(self.readArray[5,:]))
                self.Battery_Amp = float(np.average(self.readArray[6,:]))
#                 print("RERE1", self.readArray[6,:])
#                 print("RERE2", self.readArray[7,:])
                self.Battery_Volt = float(np.average(self.readArray[7,:]))
                

            self.EncValue = self.EncVal.getValue()
 
 
        Cnt = GPIO.input(self.Counter)
        HPo = GPIO.input(self.HomeRobot)
        HHe = GPIO.input(self.HeightUp)
#         GHe = GPIO.input(self.HeightDown)
        GHe = 0
        HAn = GPIO.input(self.HomeAngle)

#         print("Sensors",Cnt,HPo,HHe,GHe,HAn)     
            
        self.SensorArray[0] = self.O2
        self.SensorArray[1] = self.CO2
        self.SensorArray[2] = self.CH4
        self.SensorArray[3] = self.Humidity
        self.SensorArray[4] = self.Temperature
        self.SensorArray[5] = self.Battery_Volt
        self.SensorArray[6] = -self.EncValue
        self.SensorArray[7] = Cnt
#         self.SensorArray[8] = 0#HPo
        self.SensorArray[8] = HPo
        self.SensorArray[9] = HHe
        self.SensorArray[10] = GHe
        self.SensorArray[11] = HAn

        self.SensorArray[12] = self.Battery_Temp
        self.SensorArray[13] = self.Battery_Amp
        
    def LED_up_on(self):
        print("LED_UP_ON")
        GPIO.output(self.LED_up,1)
    
    def LED_up_off(self):
        print("LED_UP_OFF")
        GPIO.output(self.LED_up,0)

    def LED_down_on(self):
        print("LED_DOWN_ON")
        GPIO.output(self.LED_down,1)
    
    def LED_down_off(self):
        print("LED_DOWN_OFF")
        GPIO.output(self.LED_down,0)
        
    def changeSpeed_func(self,PositionSpeed,HeightSpeed,AngleSpeed):
#         print("SPEED: ", PositionSpeed, HeightSpeed, AngleSpeed)
        if PositionSpeed != '':
            self.PositionSpeed = PositionSpeed
            self.Servo_Position.pwm.ChangeFrequency(int(PositionSpeed))
        if HeightSpeed != '':
            self.HeightSpeed = HeightSpeed
            self.Servo_Height.pwm.ChangeFrequency(int(HeightSpeed))
        if AngleSpeed != '':
            self.AngleSpeed = AngleSpeed
            self.Servo_Angle.pwm.ChangeFrequency(int(AngleSpeed))

    def Motor_Position_up(self):
#         print("motor_Position_up")
        self.Servo_Position.pwm.start(1)
        self.Servo_Position.pwm.ChangeFrequency(int(self.PositionSpeed))
        self.tic_P = time.perf_counter()
        GPIO.output(self.ENB1,0)
        GPIO.output(self.DIR1,0)

    def Motor_Position_down(self):
#         print("motor_Position_down")
        self.Servo_Position.pwm.start(1)
        self.Servo_Position.pwm.ChangeFrequency(int(self.PositionSpeed))
        self.tic_P = time.perf_counter()
        GPIO.output(self.ENB1,0)
        GPIO.output(self.DIR1,1)

    def Motor_Position_stop(self):
#         print("motor_Position_stop")
        self.Servo_Position.pwm.stop()
        self.toc_P = time.perf_counter()
        
        GPIO.output(self.ENB1,0)
        GPIO.output(self.DIR1,0)

    def Motor_Height_up(self):
#         print("motor_Height_up")
        self.Servo_Height.pwm.start(1)
        self.Servo_Height.pwm.ChangeFrequency(int(self.HeightSpeed))
        self.tic_H = time.perf_counter()
        GPIO.output(self.ENB2,0)
        GPIO.output(self.DIR2,0)

    def Motor_Height_down(self):
#         print("motor_Height_down")
        self.Servo_Height.pwm.start(1)
        self.Servo_Height.pwm.ChangeFrequency(int(self.HeightSpeed))
        self.tic_H = time.perf_counter()
        GPIO.output(self.ENB2,0)
        GPIO.output(self.DIR2,1)

    def Motor_Height_stop(self):
#         print("motor_Height_stop")
        self.Servo_Height.pwm.stop()
        self.toc_H = time.perf_counter()
        self.Pre_tic_H=self.tic_H
        GPIO.output(self.ENB2,0)
        GPIO.output(self.DIR2,0)

    def Motor_Angle_right(self):
#         print("motor_Angle_right")
        self.Servo_Angle.pwm.start(1)
        self.Servo_Angle.pwm.ChangeFrequency(int(self.AngleSpeed))
        self.tic_A = time.perf_counter()
#         print("\nB1: "+str(self.tic_A)+"\n")
        GPIO.output(self.ENB3,0)
        GPIO.output(self.DIR3,1)
        self.FirstTime_HAnLeft =0
        self.FirstTime_HAnRight +=1

    def Motor_Angle_left(self):
#         print("motor_Angle_left")
        self.Servo_Angle.pwm.start(1)
        self.Servo_Angle.pwm.ChangeFrequency(int(self.AngleSpeed))
        self.tic_A = time.perf_counter()
#         print("\nB2: "+str(self.tic_A)+"\n")
        GPIO.output(self.ENB3,0)
        GPIO.output(self.DIR3,0)
        self.FirstTime_HAnRight =0
        self.FirstTime_HAnLeft +=1

    def Motor_Angle_stop(self):
#         print("motor_Angle_stop")
        self.Servo_Angle.pwm.stop()
        self.toc_A = time.perf_counter()
#         print("\nB3: "+str(self.tic_A)+"\n")
        self.Pre_tic_A=self.tic_A
#         print("A1",self.Pre_tic_A)
        GPIO.output(self.ENB3,0)
        GPIO.output(self.DIR3,0)
