from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
import atexit
import RPi.GPIO as GPIO
import threading

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)

class MotorManager():
    def __init__(self,controller,sensor):
        self.controller = controller
        self.sensor = sensor

    def set_param(self,stepPerRev1,stepPerRev2,spd1,spd2):
        mystepper1 = self.controller.getStepper(1)
        mystepper2 = self.controller.getStepper(2)
        mystepper1.setStepsPerRev(stepPerRev1)
        mystepper2.setStepsPerRev(stepPerRev2)
        mystepper1.setSpeed(spd1)
        mystepper2.setSpeed(spd2)

    def power_on(self):
        GPIO.output(20,True)
    def power_off(self):
        GPIO.output(20,False)

        
    def stepper_worker(self,stepper, numsteps, direction, style):
        print("Motor {} starts stepping!".format(stepper.motornum))
        stepper.step(numsteps, direction, style)
        print("Motor {} is done!".format(stepper.motornum))
    def motor1_run(self,step,direction):
        th1 = threading.Thread(target=self.stepper_worker,
                               args=(self.controller.getStepper(1), step, direction,
                               Adafruit_MotorHAT.INTERLEAVE))
        th1.start()
    def motor2_run(self,step,direction):
        th2 = threading.Thread(target=self.stepper_worker,
                               args=(self.controller.getStepper(2), step, direction,
                               Adafruit_MotorHAT.INTERLEAVE))
        th2.start()
