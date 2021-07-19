# import RPi.GPIO as GPIO
from time import sleep

# from encoder import Encoder
# from pwmServo import PWMServo

# GPIO.setwarnings(False) #disable warnings
# GPIO.setmode(GPIO.BCM)

import numpy as np
from random import randint

import serial
from time import sleep
import json


class my_controller():
    def __init__(self):
        super().__init__()

        self.ser = serial.Serial("COM5", 115200, timeout=0)  # Open port with baud rate
        # self.SensorArray = np.array(7)
        # self.SensorArray = [1, 1, 1, 1, 1, 1, 1]
        self.SensorArray = [1, 1, 1, 1, 1, 1, 1, 0, 0, 0, 0, 0]
        self.MotorArray = {"PP": 0,"PS": 1000, "PD": 0, "PE": 0,"HP": 0, "HS": 1000, "HD": 0, "HE": 0, "AP": 0,"AS": 1000, "AD": 0, "AE": 0}

        # Parameters
        self.cnt_1 = 0
        flag_Start = 1  # sensor_2
        flag_End = 0  # sensor_3

        # Serial

    def SensorDataFunc_old(self):
        self.SensorArray[0] = randint(80, 100)
        self.SensorArray[1] = randint(10, 20)
        self.SensorArray[2] = randint(5, 10)
        self.SensorArray[3] = randint(20, 30)
        self.SensorArray[4] = randint(25, 30)
        self.SensorArray[5] = 82

    def SensorDataFunc(self):

        received_data = self.ser.readline()
        # print("A",received_data)
        sleep(0.1)
        data_left = self.ser.inWaiting()  # check for remaining byte
        received_data += self.ser.read(data_left)
        print("AAA", received_data)
        if received_data != b'':
            text = received_data.decode()
            # 0 82 83
            # 0 165 166
            # 0 168 169
            # 0 190 191 - 0 191 192 - 0 383 384
            # 0 138 139 - 0 139 140 -  0 251 252
            print(len(text))
            if len(text) >= 139: #83:  # 105:
                text1 = [i for i, x in enumerate(text) if x == "{"]
                text2 = [i for i, x in enumerate(text) if x == "}"]
                text11 = text.rfind('{')
                text12 = text.rfind('}')
                text21 = text.index('{')
                text22 = text.rfind('}')
                LE = len(text)
                # print(text)
                print("RR", text21, text22, LE)
                if text22 < text21:
                    print(text22 < text21)

                    ## print(text[104],'\n\n')
                    ## print(text[text22+1:105],'\n\n')
                    ## print(text[0:text21],'\n\n')

                    sleep(0.05)
                    data_left = self.ser.inWaiting()  # check for remaining byte
                    received_data += self.ser.read(data_left)
                    print("AAA2", received_data)
                    text = received_data.decode()
                    print(len(text))
                    text11x = text.rfind('{')
                    text12x = text.rfind('}')
                    text21x = text.index('{')
                    text22x = text.rfind('}')
                    LEx = len(text)
                    # print(text)
                    print("RRx", text21x, text22x, LEx)
                    print("WWx", text[text21x:text22x + 1])

                    print("\nAya")
                    Matn = text[text21x:text22x + 1]
                    print("MATN", Matn)
                    received_data = Matn

                    # print("\nAya")
                    # Matn = text[text22 + 1:140] + text[0:text21]
                    # print("MATN", Matn)
                    # received_data = Matn
                else:
                    print("WW", text[text21:text22 + 1])
                    received_data = text[text21:text22 + 1]

                if len(text) >= (2 * 138):
                    print("RR2", text1, text2, text11, text12, text21, text22, LE)
                    received_data = text[text1[0]:text1[1]]
                    ## received_data = text[text21:text21 +85]
                    print("PP\n", received_data)

                print("Ready\n", received_data)
                rd = json.loads(received_data)
                print("Final\n", rd)
                # print("O2: ", rd["O2"], "CO2: ", rd["CO2"], "CH4: ", rd["CH4"],
                #       "Hum: ", rd["Hum"], "Tem: ", rd["Tem"], "Bat: ", rd["Bat"],
                #       "Enc: ", rd["Enc"],"Counter: ", rd["Counter"],
                #       "HomeRobot: ", rd["HomeRobot"], "HeightUp: ", rd["HeightUp"],
                #       "HomeAngle: ", rd["HomeAngle"], "HeightDown: ", rd["HeightDown"]
                #       )

                self.SensorArray[0] = rd["O2"]
                self.SensorArray[1] = rd["CO2"]
                self.SensorArray[2] = rd["CH4"]
                self.SensorArray[3] = rd["Hum"]
                self.SensorArray[4] = rd["Tem"]
                self.SensorArray[5] = rd["Bat"]
                self.SensorArray[6] = rd["Enc"]
                self.SensorArray[7] = rd["Cnt"]
                self.SensorArray[8] = rd["HPo"]
                self.SensorArray[9] = rd["HHe"]
                self.SensorArray[10] = rd["GHe"]
                self.SensorArray[11] = rd["HAn"]

    # def read_sensors(self):
    #     received_data = self.ser.readline()
    #     sleep(0.05)
    #     data_left = self.ser.inWaiting()  # check for remaining byte
    #     received_data += self.ser.read(data_left)
    #     if received_data != b'':
    #         gama = json.loads(received_data.decode())
    #         print("Received", gama)
    #         print("O2: ", gama["O2"], "CO2: ", gama["CO2"], "CH4: ", gama["CH4"], "Humidity: ", gama["Humidity"],
    #               "Temperature: ", gama["Temperature"], "Battery: ", gama["Battery"])
    #         self.SensorArray[0] = gama["O2"]
    #         self.SensorArray[1] = gama["CO2"]
    #         self.SensorArray[2] = gama["CH4"]
    #         self.SensorArray[3] = gama["Humidity"]
    #         self.SensorArray[4] = gama["Temperature"]
    #         self.SensorArray[5] = gama["Battery"]
    #         self.SensorArray[6] = gama["Encoder"]
    #     return self.SensorArray

    def changeSpeed_func(self, PositionSpeed, HeightSpeed, AngleSpeed):
        print("SPEED: ", PositionSpeed, HeightSpeed, AngleSpeed)
        self.MotorArray["PS"] = int(PositionSpeed)
        self.MotorArray["HS"] = int(HeightSpeed)
        self.MotorArray["AS"] = int(AngleSpeed)
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Position_up(self):
        print("motor_Position_up")
        self.MotorArray["PP"] = 1
        self.MotorArray["PD"] = 1
        self.MotorArray["PE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Position_down(self):
        print("motor_Position_down")
        self.MotorArray["PP"] = 1
        self.MotorArray["PD"] = 0
        self.MotorArray["PE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Position_stop(self):
        print("motor_Position_stop")
        self.MotorArray["PP"] = 0
        self.MotorArray["PD"] = 0
        self.MotorArray["PE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)
        sleep(0.1)
        self.ser.write(self.MotorOutput)

    def Motor_Height_up(self):
        print("motor_Height_up")
        self.MotorArray["HP"] = 1
        self.MotorArray["HD"] = 0
        self.MotorArray["HE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Height_down(self):
        print("motor_Height_down")
        self.MotorArray["HP"] = 1
        self.MotorArray["HD"] = 1
        self.MotorArray["HE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Height_stop(self):
        print("motor_Height_stop")
        self.MotorArray["HP"] = 0
        self.MotorArray["HD"] = 0
        self.MotorArray["HE"] = 0
        self.MotorArray["AP"] = 0
        self.MotorArray["AD"] = 0
        self.MotorArray["AE"] = 0

        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)
        sleep(0.1)
        self.ser.write(self.MotorOutput)

    def Motor_Angle_right(self):
        print("motor_Angle_right")
        self.MotorArray["AP"] = 1
        self.MotorArray["AD"] = 1
        self.MotorArray["AE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Angle_left(self):
        print("motor_Angle_left")
        self.MotorArray["AP"] = 1
        self.MotorArray["AD"] = 0
        self.MotorArray["AE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)

    def Motor_Angle_stop(self):
        print("motor_Angle_stop")
        self.MotorArray["HP"] = 0
        self.MotorArray["HD"] = 0
        self.MotorArray["HE"] = 0
        self.MotorArray["AP"] = 0
        self.MotorArray["AD"] = 0
        self.MotorArray["AE"] = 0
        print(self.MotorArray)
        self.MotorOutput = json.dumps(self.MotorArray, indent=1)
        self.MotorOutput = self.MotorOutput.encode()
        self.ser.write(self.MotorOutput)
        sleep(0.1)
        self.ser.write(self.MotorOutput)