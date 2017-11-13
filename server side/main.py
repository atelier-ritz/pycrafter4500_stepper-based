from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT, Adafruit_StepperMotor
from server import Server
from TLV493D import TLV493D
import threading
import atexit
import RPi.GPIO as GPIO
import time
import sys

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(20,GPIO.OUT)

mh = Adafruit_MotorHAT()

sensor = TLV493D()


def turnOffMotors():
    mh.getStepper(1).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(2).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(3).run(Adafruit_MotorHAT.RELEASE)
    mh.getStepper(4).run(Adafruit_MotorHAT.RELEASE)
    GPIO.cleanup()
atexit.register(turnOffMotors)

def stepper_worker(stepper, numsteps, direction, style):
    print("Motor {} starts stepping!".format(stepper.motornum))
    stepper.step(numsteps, direction, style)
    print("Motor {} is done!".format(stepper.motornum))

def analyzecmd(cmd):
    print('Command - {}'.format(cmd))
    if cmd[0] == 'motorGoAndTouch':
        th1 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(1), int(cmd[1]), int(cmd[2]),
                                Adafruit_MotorHAT.SINGLE,))
        th2 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(2), int(cmd[3]), int(cmd[4]),
                                Adafruit_MotorHAT.SINGLE,))
        th1.start()
        th2.start()
        th1.join()
        th2.join()
        time.sleep(.5)
        svr.client[0][0].sendto('Motor is done!'.encode(), svr.client[0][1])
    if cmd[0] == 'powerOn':
        GPIO.output(20,False)
    if cmd[0] == 'powerOff':
        GPIO.output(20,True)
    if cmd[0] == 'setparam':
        mystepper1 = mh.getStepper(1)
        mystepper2 = mh.getStepper(2)
        mystepper1.setStepsPerRev(int(cmd[3]))
        mystepper2.setStepsPerRev(int(cmd[4]))
        mystepper1.setSpeed(int(cmd[1]))
        mystepper2.setSpeed(int(cmd[2]))
    if cmd[0] == 'motorgo1':
        th1 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(1), int(cmd[1]), int(cmd[2]),
                                Adafruit_MotorHAT.INTERLEAVE,))
        th1.start()
    if cmd[0] == 'motorgo2':
        th2 = threading.Thread(target=stepper_worker,
                                args=(mh.getStepper(2), int(cmd[1]), int(cmd[2]),
                                Adafruit_MotorHAT.INTERLEAVE,))
        th2.start()

if __name__ == "__main__":
    svr = Server()
    svr.start()
    while True:
        command = svr.getcmd()
        if command == 'quit':
            break
        if not command == ['']:
            analyzecmd(command)
            svr.clccmd()
        time.sleep(.05)
    sys.exit()
