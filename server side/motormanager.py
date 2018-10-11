
from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
import atexit
import RPi.GPIO as GPIO
import threading
import time
import math

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)

def fieldDeg2shaftDeg(val): # the single magnetic dipole model is used to calculate theta vs alpha_2
    fieldRad = val / 180 * math.pi
    shaftRad = math.atan2(2*math.sin(fieldRad),math.cos(fieldRad))
    shaftDeg = shaftRad / math.pi * 180
    return shaftDeg

def reverseDir(direction):
    if direction == 1:
        direction = 2
    else:
        direction = 1
    return direction

def getSingularityAngle():
    return 15

def getTolPhi():
    return 1

def getTolTheta():
    return 1

def getStateTheta(deg):
    if deg < getSingularityAngle():
        return 1
    elif deg >  180 - getSingularityAngle():
        return 2
    else:
        return 0

class MotorManager():
    def __init__(self,controller,sensor):
        self.controller = controller
        self.sensor = sensor
        self.degperstep = 0.9
        self.thetaMode = 1 #1:S pole is located at x+   -1: N pole is located at x+
        self.lastStateTheta = getStateTheta(sensor.theta) # 0: 15-165 1:0-15 2:165-180
        self.svr = None
        self.phiSingularity = 0 # always go to phi=0 when entering singularity at theta = 0-15

    def set_param(self,stepPerRev1,stepPerRev2,spd1,spd2):
        mystepper1 = self.controller.getStepper(1)
        mystepper2 = self.controller.getStepper(2)
        mystepper1.setStepsPerRev(stepPerRev1)
        mystepper2.setStepsPerRev(stepPerRev2)
        mystepper1.setSpeed(spd1)
        mystepper2.setSpeed(spd2)

    def set_phiSingularity(self,phi):
        self.phiSingularity = phi

    def power_on(self):
        GPIO.output(20,False)

    def power_off(self):
        GPIO.output(20,True)
#============================================
# basic driving without sensor feedback
#============================================
    def _stepper_worker(self,stepper, numsteps, direction, style=Adafruit_MotorHAT.INTERLEAVE):
        # print("Motor {} starts stepping!".format(stepper.motornum))
        stepper.step(numsteps, direction, style)
        # print("Motor {} is done!".format(stepper.motornum))

    def motor_run(self,motorId,step,direction,wait=True):
        if wait:
            self._stepper_worker(self.controller.getStepper(motorId),step,direction)
        else:
            thread = threading.Thread(target=self._stepper_worker,
                                    args=(self.controller.getStepper(motorId), step, direction,))
            thread.start()

    def _shiftThetaMode(self):
        self.thetaMode *= -1
        numsteps = 200 # 180 deg
        direction = 1
        self.motor_run(2,numsteps,direction)

#============================================
# advanced driving with sensor feedback
#============================================
    def motor1_toPhi(self,phi_cmd,tol=getTolPhi()):
        phi_cmd = phi_cmd % 360 # convert to 0-360 deg
        thetaMode = self.thetaMode
        if thetaMode  == 1:
            if phi_cmd > 180:
                phi_cmd -= 360
            while True:
                phi_msr = self.sensor.phi # [-90,90] deg
                error = phi_cmd - phi_msr
                if error < tol and error > -tol:
                    break
                if error <= tol:
                    direction = 1
                else:
                    direction = 2
                numsteps = max(int(self.degperstep * abs(error)),1)
                self.motor_run(1,numsteps,direction)
                time.sleep(.3)
        else:
            while True:
                phi_msr = self.sensor.phi # [-180,-90]or[90,180] deg
                if phi_msr < 0:
                    phi_msr += 360
                error = phi_cmd - phi_msr
                if error < tol and error > -tol:
                    break
                if error <= tol:
                    direction = 1
                else:
                    direction = 2
                numsteps = max(int(self.degperstep * abs(error)),1)
                self.motor_run(1,numsteps,direction)
                time.sleep(.3)

    def motor2_toTheta(self,theta_cmd,tol=getTolTheta()):
        thetaMode = self.thetaMode
        while True:
            theta_msr = self.sensor.theta # [0,180] deg
            errorField = theta_cmd - theta_msr
            if errorField < tol and errorField > -tol:
                break
            if errorField >= tol:
                direction = 1
            else:
                direction = 2
            if thetaMode == -1:
                direction = reverseDir(direction)
            errorShaft = fieldDeg2shaftDeg(theta_cmd) - fieldDeg2shaftDeg(theta_msr)
            numsteps = max(int(self.degperstep * abs(errorShaft)),1)
            self.motor_run(2,numsteps,direction)
            time.sleep(.5)

#============================================
# advanced control that considers singularities
#============================================

    def motor12_goto_field(self,phi_cmd,theta_cmd):
        phi_cmd = phi_cmd % 360 # convert to 0-360 deg
        print("Motors start going to phi = {} theta = {}!".format(phi_cmd,theta_cmd))
        thetaMode = self.thetaMode
        #==================================================
        # left singularity if theta is in [0,15]or[165,180]
        #==================================================
        if not self.lastStateTheta == 0:
            direction = self.lastStateTheta
            if thetaMode == -1:
                direction = reverseDir(direction)
            self.motor_run(2,30,direction)
            time.sleep(1)
        #==================================================
        # shift thetaMode if necessary
        #==================================================
        if phi_cmd > 90 and phi_cmd < 270:
            if self.thetaMode == 1:
                self._shiftThetaMode()
        else:
            if self.thetaMode == -1:
                self._shiftThetaMode()
        #==================================================
        # any theta < 15 isconsidered theta = 0
        # any theta > 165 is considered theta  = 180
        #==================================================
        nextState = getStateTheta(theta_cmd)
        if nextState == 0:
            self.motor12_gotoField(phi_cmd,theta_cmd)
            self.lastStateTheta = 0
        if nextState == 1:
            self.motor12_gotoField(self.phiSingularity,90,0.8,0.8)
            self.motor_run(2,98,2)
            self.lastStateTheta = 1
        if nextState == 2:
            self.motor12_gotoField(self.phiSingularity,90,0.8,0.8)
            self.motor_run(2,109,1)
            self.lastStateTheta = 2
        #==================================================
        # send finish flag to the client
        #==================================================
        self.svr.client[0][0].sendto('Motor is done!'.encode(), self.svr.client[0][1])

    def motor12_gotoField(self,phi_cmd,theta_cmd,tolPhi=getTolPhi(),tolTheta=getTolTheta()): # far away from the singularity points
        while True:
            th1 = threading.Thread(target=self.motor1_toPhi,args=(phi_cmd,tolPhi,))
            th2 = threading.Thread(target=self.motor2_toTheta,args=(theta_cmd,tolTheta,))
            th1.start()
            th2.start()
            th1.join()
            th2.join()
            errorPhi = min(abs(phi_cmd - self.sensor.phi),abs(phi_cmd - 360 - self.sensor.phi))
            if errorPhi < tolPhi and abs(theta_cmd - self.sensor.theta) < tolTheta:
                break
            time.sleep(1)
    #============================================
    # oscillation
    #============================================
    def motor1_randomize(self):
        self.motor_run(2,200,1)
        self.motor_run(2,200,-1)
    def motor2_randomize(self):
        self.motor_run(1,200,1)
        self.motor_run(1,200,-1)

    def randomize(self,count=1):
        self.motor12_goto_field(90,90)
        for i in range(count):
            th1 = threading.Thread(target=self.motor1_randomize)
            th2 = threading.Thread(target=self.motor2_randomize)
            # th2 = threading.Thread(target=self.motor2_randomize,args=(time,))
            th1.start()
            th2.start()
            th1.join()
            th2.join()
            time.sleep(1)

    def oscPitch(self):
        self.motor_run(2,50,1)
        time.sleep(1)
        self.motor_run(2,100,2)
        time.sleep(1)
        self.motor_run(2,90,1)
        time.sleep(1)
        self.motor_run(2,80,2)
        time.sleep(1)
        self.motor_run(2,70,1)
        time.sleep(1)
        self.motor_run(2,60,2)
        time.sleep(1)
        self.motor_run(2,50,1)
        time.sleep(1)
        self.motor_run(2,40,2)
        time.sleep(1)
        self.motor_run(2,30,1)
        time.sleep(1)
        self.motor_run(2,20,2)
        time.sleep(1)
        self.motor_run(2,10,1)

    def oscYaw(self):
        self.motor_run(1,50,1)
        time.sleep(1)
        self.motor_run(1,100,2)
        time.sleep(1)
        self.motor_run(1,90,1)
        time.sleep(1)
        self.motor_run(1,80,2)
        time.sleep(1)
        self.motor_run(1,70,1)
        time.sleep(1)
        self.motor_run(1,60,2)
        time.sleep(1)
        self.motor_run(1,50,1)
        time.sleep(1)
        self.motor_run(1,40,2)
        time.sleep(1)
        self.motor_run(1,30,1)
        time.sleep(1)
        self.motor_run(1,20,2)
        time.sleep(1)
        self.motor_run(1,10,1)
