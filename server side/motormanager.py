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
        self.degperstep = 1.4

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

    def macro1(self):
        stepper = self.controller.getStepper(2)
        theta_cmd = 90
        tol = 5 % tolerance
        while True:
            theta_msr = self.sensor.theta # [-180,180] deg
            errorField = theta_cmd - theta_msr
            if errorField < tol and errorField > -tol:
                break
            if errorField >= tol:
                direction = 1
            else:
                direction = 2
            errorShaft = ??????????????
            numsteps = self.degperstep * abs(errorShaft)
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(1)

    def macro2(self,phi):
        stepper = self.controller.getStepper(1)
        phi_cmd = phi
        tol = 5 % tolerance
        while True:
            phi_msr = self.sensor.phi # [-180,180] deg
            error = phi_cmd - phi_msr
            if error < tol and error > -tol:
                break
            if error >= tol:
                direction = 1
            else:
                direction = 2
            numsteps = self.degperstep * abs(error)
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(1)

    def stepper_worker_polar(self,phi):


    def stepper_worker_theta(self,theta):


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
    def motor12_goto_field(self,phi,theta):
        self.macro1() # fix the turntable and rotate the magnet
        self.macro2(phi) # fix the magnet and rotate the turntable
        self.macro3(theta) # fix the turntable and rotate the magnet again
        # th1 = threading.Thread(target=stepper_worker_phi,args=(mh.getStepper(1), phi,))
        # th2 = threading.Thread(target=stepper_worker_theta,args=(mh.getStepper(2),theta,))
        # th1.start()
        # th2.start()
        # th1.join()
        # th2.join()
        # time.sleep(.5)
