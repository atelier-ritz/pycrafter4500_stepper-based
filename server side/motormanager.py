from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
import atexit
import RPi.GPIO as GPIO
import threading
import time
import math

def fieldDeg2shaftDeg(val): # the single magnetic dipole model is used to calculate theta vs alpha_2
    fieldRad = val / 180 * math.pi
    shaftRad = math.atan2(2*math.sin(fieldRad),math.cos(fieldRad))
    shaftDeg = shaftRad / math.pi * 180
    return shaftDeg

def getSingularityAngle():
    return 15

def getTolPhi():
    return 1

def getTolTheta():
    return 1

def getState(deg):
    if deg < getSingularityAngle():
        return 1
    elif deg >  180 - getSingularityAngle():
        return 2
    else:
        return 0

# def getTolThetaSgl(theta_cmd):
#     state = getState(theta_cmd)
#     if state == 0:
#         return getTolTheta()
#     else:
#         if state == 2:
#             theta_cmd = 180 - theta_cmd
#         # the closer to the singularity is the goal, the more we should loosen the tolerance
#         # it is selected such that
#         # model tolerance(theta_cmd) = exp(a * theta_cmd +b),
#         # where tolerance(getSingularityAngle) = TOL_THETA, tolerance(0) = k * TOL_THETA
#         k = 3
#         b = math.log(k * getTolTheta())
#         a = (math.log(getTolTheta()) - b) / getSingularityAngle()
#         tol = math.exp(a * theta_cmd + b)
#         return tol

class MotorManager():
    def __init__(self,controller,sensor):
        self.controller = controller
        self.sensor = sensor
        self.degperstep = 0.9
        self.lastState = getState(sensor.theta)
        self.svr = None
        self.phiSingularity = 0

    def set_param(self,stepPerRev1,stepPerRev2,spd1,spd2):
        mystepper1 = self.controller.getStepper(1)
        mystepper2 = self.controller.getStepper(2)
        mystepper1.setStepsPerRev(stepPerRev1)
        mystepper2.setStepsPerRev(stepPerRev2)
        mystepper1.setSpeed(spd1)
        mystepper2.setSpeed(spd2)

    def set_phiSingularity(self,phi):
        self.phiSingularity = phi
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

#============================================
# advanced driving with sensor feedback
#============================================
    def motor1_toPhi(self,phi_cmd):
        tol = getTolPhi()
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
            self.motor_run(1,numsteps,direction)
            time.sleep(.3)

    def motor2_toTheta(self,theta_cmd):
        state = getState(theta_cmd)
        if state == 0:
            tol = getTolTheta()
        else:
            tol = getTolThetaSgl(theta_cmd)
        while True:
            theta_msr = self.sensor.theta # [0,180] deg
            errorField = theta_cmd - theta_msr
            if errorField < tol and errorField > -tol:
                break
            if errorField >= tol:
                direction = 1
            else:
                direction = 2
            errorShaft = fieldDeg2shaftDeg(theta_cmd) - fieldDeg2shaftDeg(theta_msr)
            numsteps = max(int(self.degperstep * abs(errorShaft)),1)
            self.motor_run(2,numsteps,direction)
            time.sleep(.5)

#============================================
# advanced control that considers singularities
#============================================
# any theta < 15 isconsidered theta = 0
# any theta > 165 is considered theta  = 180
    def motor12_choose_strategy(self,phi_cmd,theta_cmd):
        print("Motors start going to phi = {} theta = {}!".format(phi_cmd,theta_cmd))
        nextState = getState(theta_cmd)
        # leave singularity
        if not self.lastState == 0:
            self.motor_run(2,30,self.lastState)
            time.sleep(1)
            print('left singularity')
        # go to the destination
        if nextState == 0:
            self.motor12_gotoField(phi_cmd,theta_cmd)
            self.lastState = 0
        if nextState == 1:
            self.motor12_gotoField(self.phiSingularity,90)
            self.motor_run(2,100,2)
            # self.motor12_approachSingularity(1)
            self.lastState = 1
        if nextState == 2:
            self.motor12_gotoField(self.phiSingularity,90)
            self.motor_run(2,100,1)
            # self.motor12_approachSingularity(2)
            self.lastState = 2
        print('done')
        self.svr.client[0][0].sendto('Motor is done!'.encode(), self.svr.client[0][1])

    def motor12_gotoField(self,phi_cmd,theta_cmd): # far away from the singularity points
        while True:
            th1 = threading.Thread(target=self.motor1_toPhi,args=(phi_cmd,))
            th2 = threading.Thread(target=self.motor2_toTheta,args=(theta_cmd,))
            th1.start()
            th2.start()
            th1.join()
            th2.join()
            if abs(phi_cmd - self.sensor.phi) < getTolTheta() and abs(theta_cmd - self.sensor.theta) < getTolTheta():
                break
            time.sleep(1)
    #============================================
    # testing
    #============================================
    def macro1(self):
        theta = []
        self.motor12_choose_strategy(30,90)
        for i in range(50):
            self.motor_run(2,2,1)
            time.sleep(1)
            theta.append(self.sensor.theta)
            print(theta)
