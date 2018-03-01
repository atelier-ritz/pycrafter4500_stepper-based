from plot import MyPlot
import numpy as np
import matplotlib
import pycrafter4500
import math
import time
import re

class TextProcess(object):
    def __init__(self,client,mm):
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.cir = [] #
        self.polygon = []
        self.variables = {} # store the variables in the editor
        self.plot = MyPlot()
        self.exposureTime = 0
        self.intensityUV = 0
        self.client = client
        self.mm = mm

    def clear(self):
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.cir = []
        self.polygon = []
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
        match = re.match(r"(?P<function>[a-z0-9]+)\((?P<args>.*)\)", line)
        if match:
            # function and args preprocessing
            name = match.group('function')
            args = match.group('args')
            args = re.sub(r'\s+', '', args) # strip spaces in args
            args = args.split(',')
            if not args == ['']:
                for i, arg in enumerate(args):# each argument split with ,
                    arg = re.split('([-/*+)(])',arg)
                    for index, item in enumerate(arg):
                        if item in self.variables: arg[index] = self.variables[item]
                    arg = ''.join(arg)
                    args[i] = eval(arg)
            # run functions
            if name == 'line':
                args = list(map(float, args))
                x1,x2,y1,y2 = args
                theta = math.atan2(y1-y2,x1-x2)
                w = 0.0001
                x = [x1-w*math.cos(theta),x2-w*math.cos(theta),x2+w*math.cos(theta),x1+w*math.cos(theta)]
                y = [y1-w*math.sin(theta),y2-w*math.sin(theta),y2+w*math.sin(theta),y1+w*math.sin(theta)]
                vertices = np.column_stack((x,y))
                item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
                self.polygon.append(item)
            if name == 'rect':
                args = list(map(float, args))
                self.rect.append([args[0],args[1],args[2],args[3]])
            if name == 'cir':
                args = list(map(float, args))
                self.cir.append([args[0],args[1],args[2]])
            if name == 'polygon':
                args = list(map(float, args))
                mid = int(len(args)/2)
                x = args[:mid]
                y = args[mid:]
                vertices = np.column_stack((x,y))
                item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
                self.polygon.append(item)
            if name == 'field':
                self.mm.magneticFieldGo(int(args[0]),int(args[1]))
                while self.client.isBusy:
                    time.sleep(.5)
            if name == 'show':
                self._show()
            if name == 'cure':
                self._cure()
            if name == 'print':
                [print(i) for i in args]
            if name == 'wait':
                time.sleep(int(args[0]))
            # macro demo
            if name == 'gripper':
                self._macro_gripper()
            if name == 'swimmer':
                self._macro_swimmer()
            if name == 'swimmerb':
                self._macro_batch_swimmer()
            if name == 'oscPitch':
                self.mm.oscPitch()
            if name == 'oscYaw':
                self.mm.oscYaw()
            if name == 'randomize':
                self.mm.randomize(int(args[0]))

# ==============================================================================
# Macros
# ==============================================================================
    def _macro_gripper(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        curingOrder = [2,3,1,5,4]
        ''' 1    2    3    4    5  '''  # pieceId
        ''' l1   l2   l3   l2   l1 '''  # length
        ''' L150 L120 U    R120 R150  '''  # magnetization
        ''' 2    3    1    5    4  '''  # curingOrder
        def f1(): self._showCureRect(-90,150+15, [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f2(): self._showCureRect(-90,120,    [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f3(): self._showCureRect(0,0,        [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f4(): self._showCureRect(90,120,     [0.5-0.5*w,0.5+0.5*l3,      w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f5(): self._showCureRect(90,150+15,  [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_swimmer(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        curingOrder = [4,1,3,2,5]
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90,         [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f2(): self._showCureRect(0,0,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,  [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f4(): self._showCureRect(0,180,   [0.5-0.5*w,0.5+0.5*l3,      w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f5(): self._showCureRect(90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],oscAzimuth=False,oscPolar=False,waitTime_s=10)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_batch_swimmer(self):
        p = 0.1
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        curingOrder = [4,1,3,2,5]
        # batch param
        lengthX = w # length X of one feature
        lengthY = l1+l2+l3+l2+l1 # length Y of one feature
        dx = lengthX * 1.5 # gap X between features
        dy = lengthX  # gap Y between features
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRectBatch(90,90,         [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],dx,dy,lengthX,lengthY,oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f2(): self._showCureRectBatch(0,0,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRectBatch(-90,90,  [0.5-0.5*w,0.5-0.5*l3,      w,l3],dx,dy,lengthX,lengthY,oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f4(): self._showCureRectBatch(0,180,   [0.5-0.5*w,0.5+0.5*l3,      w,l2],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f5(): self._showCureRectBatch(90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=False,waitTime_s=10)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

# ==============================================================================
# Internal use
# ==============================================================================
    def _field_go(self,phi,theta,waitSec=3):
        self.mm.magneticFieldGo(phi,theta)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(waitSec)

    def _batch_line_append(self,x1,x2,y1,y2,numX,numY,dx,dy):
        for i in range(numX):
            for j in range(numY):
                xOff = dx * i
                yOff = dy * j
                theta = math.atan2(y1-y2,x1-x2)
                w = 0.001
                x = [x1-w*math.cos(theta),x2-w*math.cos(theta),x2+w*math.cos(theta),x1+w*math.cos(theta)]
                y = [y1-w*math.sin(theta),y2-w*math.sin(theta),y2+w*math.sin(theta),y1+w*math.sin(theta)]
                x = [i+xOff for i in x]
                y = [i+yOff for i in y]
                vertices = np.column_stack((x,y))
                item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
                self.polygon.append(item)

    def _batch_rect_append(self,rectArray,dx,dy,lengthX,lengthY):
        numberHalfSideX = int(0.5*(1-lengthX)/(dx+lengthX))
        numberHalfSideY = int(0.5*(1-lengthY)/(dy+lengthY))
        for i in range(numberHalfSideX*2+1):
            for j in range(numberHalfSideY*2+1):
                newRect = [x + y for x, y in zip(rectArray, [(i-numberHalfSideX)*(dx+lengthX),(j-numberHalfSideY)*(dy+lengthY),0,0])]
                self.rect.append(newRect)

    def _showCureRect(self,phi,theta,rectArray,oscAzimuth=False,oscPolar=False,waitTime_s=0,exposureTime_ms=0):
        self._field_go(phi,theta)
        if(oscAzimuth):
            self.mm.oscYaw()
            time.sleep(15)
        if(oscPolar):
            self.mm.oscPitch()
            time.sleep(15)
        if not waitTime_s == 0:
            self.mm.powerOff()
            time.sleep(waitTime_s)
            self.mm.powerOn()
        self.rect.append(rectArray)
        self._show()
        self._cure(exposureTime_ms)

    def _showCureRectBatch(self,phi,theta,rectArray,dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=False,waitTime_s=0,exposureTime_ms=0):
        self._field_go(phi,theta)
        if(oscAzimuth):
            self.mm.oscYaw()
            time.sleep(15)
        if(oscPolar):
            self.mm.oscPitch()
            time.sleep(15)
        if not waitTime_s == 0:
            self.mm.powerOff()
            time.sleep(waitTime_s)
            self.mm.powerOn()
        self._batch_rect_append(rectArray,dx,dy,lengthX,lengthY)
        self._show()
        self._cure(exposureTime_ms)

    def _polygon_append(self,array):
        args = list(map(float, array))
        mid = int(len(args)/2)
        x = args[:mid]
        y = args[mid:]
        vertices = np.column_stack((x,y))
        item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
        self.polygon.append(item)

    def _show(self):
        empty = self.rect == [] and self.cir == [] and self.polygon == []
        if not empty:
            self.plot.clear()
            if self.rect:
                [self.plot.addRect(*r) for r in self.rect]
                self.rect = []
            if self.cir:
                [self.plot.addCir(*r) for r in self.cir]
                self.cir = []
            if self.polygon:
                [self.plot.addPolygon(r) for r in self.polygon]
                self.polygon = []
            self.plot.show()

    def _cure(self,time_ms=0):
        if time_ms == 0: time_ms=self.exposureTime
        intensity = 0xFF - self.intensityUV
        if time_ms == 0:
            pycrafter4500.set_LED_current(intensity)
            time.sleep(0.01)
        else:
            pycrafter4500.set_LED_current(intensity)
            time.sleep(time_ms/1000)
            pycrafter4500.set_LED_current(255)
            time.sleep(1)


    def _process_variableAssignments(self,line):
        line = re.sub(r'\s+', '', line) # strip spaces in args
        match = re.match(r"(?P<variable>[a-z]+)=(?P<value>[0-9.]+)", line)
        if match:
            name = match.group('variable')
            value = match.group('value')
            self.variables[name] = value
