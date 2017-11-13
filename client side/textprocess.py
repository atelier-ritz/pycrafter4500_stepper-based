from gimbal import Gimbal
from plot import MyPlot
# import Adafruit_GPIO.FT232H as FT232H
import pycrafter4500
import time
import re

# FT232H.use_FT232H()
# ft232h = FT232H.FT232H()
# spi1 = FT232H.SPI(ft232h, cs=8, max_speed_hz=100000, mode=0, bitorder=FT232H.MSBFIRST)
# spi2 = FT232H.SPI(ft232h, cs=9, max_speed_hz=100000, mode=0, bitorder=FT232H.MSBFIRST)

# gimbal = Gimbal(0.3,0.7,spi1,spi2)                 # initialize (yaw and pitch data)
# gimbal.yawGoto(0)                          # initialize yaw (physically)
# gimbal.writeSpi(1,128)                           # initialize pitch (physically)

class TextProcess(object):
    def __init__(self):
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.variables = {} # store the variables in the editor
        self.plot = MyPlot()
        self.exposureTime = 0
        self.intensityUV = 0

    def clear(self):
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.variables = {} # store the variables in the editor

    def set_exposureTime(self,time):
        self.exposureTime = time

    def set_intensityUV(self,intensity):
        self.intensityUV = intensity

    def process(self,text):
        processedLines = []
        for line in text:
            line = line.split('//')[0]  # strip after //
            line = line.strip()         # strip spaces at both ends
            if not line == '':
                processedLines.append(line)
        for line in processedLines:
            self._process_functions(line)
            self._process_variableAssignments(line)

    def _process_functions(self,line):
        match = re.match(r"(?P<function>[a-z]+)\((?P<args>.+)\)", line)
        if match:
            # function and args preprocessing
            name = match.group('function')
            args = match.group('args')
            args = re.sub(r'\s+', '', args) # strip spaces in args
            args = args.split(',')
            for i, arg in enumerate(args):# each argument split with ,
                arg = re.split('([-/*+)(])',arg)
                for index, item in enumerate(arg):
                    if item in self.variables: arg[index] = self.variables[item]
                arg = ''.join(arg)
                args[i] = eval(arg)
            # run functions
            if name == 'rect':
                args = list(map(float, args))
                self.rect.append([args[0],args[1],args[2],args[3]])
            if name == 'gimbal':
                gimbal.goto(float(args[0]),float(args[1]))
            if name == 'show':
                if self.rect:
                    self.plot.clear()
                    [self.plot.addRect(*r) for r in self.rect]
                    self.plot.show()
                    self.rect = []
                    time.sleep(int(args[0]))
            if name == 'cure':
                time_ms = self.exposureTime
                intensity = 0xFF - self.intensityUV
                if time_ms == 0:
                    pycrafter4500.set_LED_current(intensity)
                    time.sleep(0.01)
                else:
                    pycrafter4500.set_LED_current(intensity)
                    time.sleep(time_ms/1000)
                    pycrafter4500.set_LED_current(255)
                    time.sleep(1)
            if name == 'print':
                [print(i) for i in args]
            if name == 'wait':
                time.sleep(int(args[0]))

    def _process_variableAssignments(self,line):
        line = re.sub(r'\s+', '', line) # strip spaces in args
        match = re.match(r"(?P<variable>[a-z]+)=(?P<value>[0-9.]+)", line)
        if match:
            name = match.group('variable')
            value = match.group('value')
            self.variables[name] = value
