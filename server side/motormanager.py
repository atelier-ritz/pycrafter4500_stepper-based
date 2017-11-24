from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
import atexit
import RPi.GPIO as GPIO
import threading
import time
import math
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)

class MotorManager():
    TOL_PHI = 1   # tolerance of phi (deg)
    TOL_THETA = 1 # tolerance of theta (deg)
    def __init__(self,controller,sensor):
        self.controller = controller
        self.sensor = sensor
        self.degperstep = 0.9

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

    def fieldDeg2shaftDeg(self,val):
        fieldRad = val / 180 * math.pi
        shaftRad = math.atan2(2*math.sin(fieldRad),math.cos(fieldRad))
        shaftDeg = shaftRad / math.pi * 180
        return shaftDeg

    def motor2_run_theta(self,theta):
        stepper = self.controller.getStepper(2)
        theta_cmd = theta
        tol = self.TOL_THETA
        while True:
            theta_msr = self.sensor.theta # [0,180] deg
            errorField = theta_cmd - theta_msr
            if errorField < tol and errorField > -tol:
                break
            if errorField >= tol:
                direction = 1
            else:
                direction = 2
            errorShaft = self.fieldDeg2shaftDeg(theta_cmd) - self.fieldDeg2shaftDeg(theta_msr)
            numsteps = max(int(self.degperstep * abs(errorShaft)),1)
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(1)

    def motor2_run_theta0(self):
        stepper = self.controller.getStepper(2)
        while True:
            theta_msr = self.sensor.theta 
            numsteps = 1
            direction = 2
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(.5)
            if theta_msr < 1:
                break

    def motor2_run_theta180(self,theta):
        stepper = self.controller.getStepper(2)
        theta_cmd = theta
        tol = self.TOL_THETA
        while True:
            theta_msr = self.sensor.theta # [0,180] deg
            errorField = theta_cmd - theta_msr
            if errorField < tol and errorField > -tol:
                break
            if errorField >= tol:
                direction = 1
            else:
                direction = 2
            errorShaft = self.fieldDeg2shaftDeg(theta_cmd) - self.fieldDeg2shaftDeg(theta_msr)
            numsteps = max(int(self.degperstep * abs(errorShaft)),1)
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(1)

    def motor1_run_phi(self,phi):
        stepper = self.controller.getStepper(1)
        phi_cmd = phi
        tol = self.TOL_PHI
        while True:
            phi_msr = self.sensor.phi # [-180,180] deg
            error = phi_cmd - phi_msr
            if error < tol and error > -tol:
                break
            if error <= tol:
                direction = 1
            else:
                direction = 2
            numsteps = max(int(self.degperstep * abs(error)),1)
            stepper.step(numsteps,direction,Adafruit_MotorHAT.INTERLEAVE)
            time.sleep(1)

    def motor1_run(self,step,direction):
        th1 = threading.Thread(target=self.stepper_worker,
                               args=(self.controller.getStepper(1), step, direction,
                               Adafruit_MotorHAT.INTERLEAVE))
        th1.start()
        if wait == True:
            th1.join()
    def motor2_run(self,step,direction,wait=False):
        th2 = threading.Thread(target=self.stepper_worker,
                               args=(self.controller.getStepper(2), step, direction,
                               Adafruit_MotorHAT.INTERLEAVE))
        th2.start()
        if wait == True:
            th2.join()
    def motor_phi_run(self,val):
        print("Motor starts going to phi = {}!".format(val))
        th1 = threading.Thread(target=self.motor1_run_phi,args=(val,))
        th1.start()
        print("Motor is done!")
        
    def motor_theta_run(self,val):
        print("Motor starts going to theta = {}!".format(val))
        th2 = threading.Thread(target=self.motor2_run_theta,args=(val,))
        th2.start()
        print("Motor is done!")

    def motor_toField_run(self,phi_cmd,theta_cmd):
        print("Motor starts going to phi = {} theta = {}!".format(phi_cmd,theta_cmd))
        if theta_cmd < 5:
            self.motor_phi_theta_run(phi_cmd,15)
            print('s')
            self.motor2_run(2,30,wait=True)
            print('start microtuning')
        elif theta_cmd <  15: 
            self.motor_phi_theta_run(phi_cmd,15)
            self.motor_theta_run(theta_cmd)
        elif theta_cmd > 175:
            return
        elif theta_cmd > 165:
            self.motor_phi_theta_run(phi_cmd,165)
            self.motor_theta_run(theta_cmd)
        else:
            self.motor_phi_theta_run(phi_cmd,theta_cmd)
        print("Motors are done!")
    def motor_phi_theta_run(self,phi_cmd,theta_cmd):
        while True:
            th1 = threading.Thread(target=self.motor1_run_phi,args=(phi_cmd,))
            th2 = threading.Thread(target=self.motor2_run_theta,args=(theta_cmd,))
            th1.start()
            th2.start()
            th1.join()
            th2.join()
            if abs(phi_cmd - self.sensor.phi) < self.TOL_PHI and abs(theta_cmd - self.sensor.theta) < self.TOL_THETA:
                break
            time.sleep(.5)
