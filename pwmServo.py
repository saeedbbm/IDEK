import RPi.GPIO as GPIO
from time import sleep

class PWMServo:
    """
    Base class doing setup and get PWM instance
    """
    def __init__(self, pin):
        GPIO.setup(pin, GPIO.OUT)
        self.pwm = GPIO.PWM(pin, 1000)
#         self.pwm.ChangeFrequency(6000)
        self.pwm.start(1)

    def change_duty_cycle(self, duty):
        self.pwm.ChangeDutyCycle(duty)
        sleep(0.3)