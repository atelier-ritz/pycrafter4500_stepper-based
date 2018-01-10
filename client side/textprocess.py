from plot import MyPlot
import numpy as np
import matplotlib
import pycrafter4500
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
            if name == 'gripperfour':
                self._macro_gripper_four()
            if name == 'batchGripperTest':
                self._macro_batch_gripper()
            if name == 'swimmerlegacy':
                self._macro_fabricate_swimmer_legacy(int(args[0]))
            if name == 'swimmer':
                self._macro_fabricate_swimmer(int(args[0]))
            if name == 'fivepixelswimmer':
                self._macro_fabricate_five_pixel_swimmer()
            if name == 'sevenpixelswimmer':
                self._macro_fabricate_seven_pixel_swimmer()
            if name == 'swimmerb':
                self._macro_batch_fabricate_swimmer(int(args[0]))
            if name == 'geit':
                self._macro_fabricate_tripodGeit2()
            if name == 'pedal':
                self._macro_fabricate_pedal()


# ==============================================================================
# Macros
# ==============================================================================
    def _macro_fabricate_tripodGeit2(self):
        legL = 0.32
        legW = 0.2
        legGap = 0.4
        bodyL = 2 * legW + legGap
        bodyW = 0.16
        originY = 0.5 * (1 - 2 * legL - bodyW)
        originX = 0.5 * (1 - bodyL)

        self.mm.magneticFieldGo(90,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.rect.append([originX+legW+legGap,originY,legW,legL])
        self.rect.append([originX+legW+legGap,originY+legL+bodyW,legW,legL])
        self._show()
        self._cure()


        self.mm.magneticFieldGo(-90,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(1)
        self.rect.append([originX,originY,legW,legL])
        self.rect.append([originX,originY+legL+bodyW,legW,legL])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.motorgo(1,200)
        time.sleep(8)
        self.rect.append([originX+bodyL/4,originY+legL,bodyL/2,bodyW])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)
        time.sleep(8)

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(1)
        self.rect.append([originX,originY+legL,bodyL/4,bodyW])
        self.rect.append([originX+bodyL*3/4,originY+legL,bodyL/4,bodyW])
        self._show()
        self._cure()

    def _macro_fabricate_tripodGeit4(self): ## four legs
        legL = 0.36
        legW = 0.1
        legGap = 0.1
        bodyL = 4 * legW + 3 *legGap
        bodyW = 0.18
        originY = 0.5 * (1 - 2 * legL - bodyW)
        originX = 0.5 * (1 - bodyL)

        self.mm.magneticFieldGo(90,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.rect.append([originX+3*legW+3*legGap,originY,legW,legL])
        self.rect.append([originX+1*legW+1*legGap,originY,legW,legL])
        self.rect.append([originX+3*legW+3*legGap,originY+legL+bodyW,legW,legL])
        self.rect.append([originX+1*legW+1*legGap,originY+legL+bodyW,legW,legL])
        self._show()
        self._cure()


        self.mm.magneticFieldGo(-90,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(1)
        self.rect.append([originX+0*legW+0*legGap,originY,legW,legL])
        self.rect.append([originX+2*legW+2*legGap,originY,legW,legL])
        self.rect.append([originX+0*legW+0*legGap,originY+legL+bodyW,legW,legL])
        self.rect.append([originX+2*legW+2*legGap,originY+legL+bodyW,legW,legL])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.motorgo(1,200)
        time.sleep(8)
        self.rect.append([originX+bodyL*3/7,originY+legL,bodyL/7,bodyW])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)
        time.sleep(8)

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(1)
        self.rect.append([originX,originY+legL,bodyL*3/7,bodyW])
        self.rect.append([originX+bodyL*4/7,originY+legL,bodyL*3/7,bodyW])
        self._show()
        self._cure()

    def _macro_fabricate_five_pixel_swimmer(self):
        width = 0.35
        length = 1.0
        lengthPerPixel = length/5

        self.mm.magneticFieldGo(90,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.motorgo(1,100)
        time.sleep(6)
        self.rect.append([0.5-length/2+lengthPerPixel*1,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(9)
        self.rect.append([0.5-length/2+lengthPerPixel*3,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(6)

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        self.rect.append([0.5-length/2+lengthPerPixel*0,0.5-width/2,lengthPerPixel,width])
        self.rect.append([0.5-length/2+lengthPerPixel*4,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(9)
        self.rect.append([0.5-length/2+lengthPerPixel*2,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)

    def _macro_fabricate_seven_pixel_swimmer(self):
        width = 0.25
        length = 0.9
        lengthPerPixel = length/7

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        self.rect.append([0.5-length/2+lengthPerPixel*6,0.5-width/2,lengthPerPixel,width])
        self.rect.append([0.5-length/2+lengthPerPixel*0,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,210)
        time.sleep(10)
        self.rect.append([0.5-length/2+lengthPerPixel*3,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()
        self.mm.motorgo(1,-210)
        time.sleep(10)

        self.mm.motorgo(1,-52)
        time.sleep(10)
        self.rect.append([0.5-length/2+lengthPerPixel*5,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,210)
        time.sleep(10)
        self.rect.append([0.5-length/2+lengthPerPixel*2,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()
        self.mm.motorgo(1,-210)
        time.sleep(10)

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.motorgo(1,-142)
        time.sleep(10)
        self.rect.append([0.5-length/2+lengthPerPixel*4,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

        self.mm.motorgo(1,197)
        time.sleep(9)
        self.rect.append([0.5-length/2+lengthPerPixel*1,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()
        self.mm.motorgo(1,-197)
        time.sleep(9)
        self.mm.motorgo(1,142)
        time.sleep(10)

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        # self.rect.append([0.5-length/2+lengthPerPixel*0,0.5-width/2,lengthPerPixel,width])
        # self._show()
        # self._cure()

    def _macro_fabricate_swimmer(self,nPixels): # doesn't cure in order
        pixel = nPixels
        steps = int((pixel-1)/2)
        waitAll = 12 # how long it takes for 1 revolution
        waitPerPixel = waitAll/pixel*steps
        stepsAll = 400 # 360 deg
        stepsPerPixel = stepsAll/(pixel-1)
        width = 0.25
        length = 0.9
        lengthPerPixel = length/pixel
        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        for i in range(steps):
            self.rect.append([i*lengthPerPixel,0.5-width/2,lengthPerPixel,width])
            self._show()
            self._cure()
            self.mm.motorgo(1,int(stepsPerPixel)*steps)
            time.sleep(waitPerPixel*steps)
            self.rect.append([(i+steps)*lengthPerPixel,0.5-width/2,lengthPerPixel,width])
            self._show()
            self._cure()
            if i == steps - 1:
                break
            self.mm.motorgo(1,-int(stepsPerPixel)*(steps-1))
            time.sleep(waitPerPixel*(steps-1))
        self.mm.motorgo(1,int(stepsPerPixel))
        time.sleep(waitPerPixel)
        self.rect.append([(pixel-1)*lengthPerPixel,0.5-width/2,lengthPerPixel,width])
        self._show()
        self._cure()

    def _macro_fabricate_swimmer_legacy(self,nPixels): # cires in order
        pixel = nPixels
        waitAll = 12
        waitPerPixel = waitAll/pixel
        stepsAll = 400
        stepsPerPixel = stepsAll/(pixel-1)
        width = 0.4
        length = 0.9
        lengthPerPixel = length/pixel
        for i in range(pixel):
            self.rect.append([i*lengthPerPixel,0.5-width/2,lengthPerPixel,width])
            self._show()
            self._cure()
            self.mm.motorgo(1,int(stepsPerPixel))
            time.sleep(waitPerPixel)

    def _macro_batch_fabricate_swimmer(self,nPixels): # doesn't cure in order
        print(2)
        pixel = nPixels
        steps = int((pixel-1)/2)
        waitAll = 12 # how long it takes for 1 revolution
        waitPerPixel = waitAll/pixel*steps
        stepsAll = 400 # 360 deg
        stepsPerPixel = stepsAll/(pixel-1)
        width = 0.07
        length = 0.37
        lengthPerPixel = length/pixel
        self._batch_rect_append((pixel-1)*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        for i in range(steps):
            self._batch_rect_append(i*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
            self._show()
            self._cure()
            self.mm.motorgo(1,int(stepsPerPixel)*steps)
            time.sleep(waitPerPixel*steps)
            self._batch_rect_append((i+steps)*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
            self._show()
            self._cure()
            if i == steps - 1:
                break
            self.mm.motorgo(1,-int(stepsPerPixel)*(steps-1))
            time.sleep(waitPerPixel*(steps-1))
        self.mm.motorgo(1,int(stepsPerPixel))


    def _macro_gripper(self):
        a = 0.24

        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.motorgo(1,100)
        time.sleep(6)
        self.rect.append([0.5-0.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(90,120)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(6)
        self.rect.append([0.5-0.5*a,0.5+0.5*a,a,a])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(270,120)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(6)
        self.rect.append([0.5-0.5*a,0.5-1.5*a,a,a])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(90,150)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(6)
        self.rect.append([0.5-0.5*a,0.5+1.5*a,a,a])
        self._show()
        self._cure()

        self.mm.magneticFieldGo(270,150)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(6)
        self.rect.append([0.5-0.5*a,0.5-2.5*a,a,a])
        self._show()
        self._cure()



    def _macro_gripper_four(self):
        a = 0.24

        self.mm.magneticFieldGo(0,0)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        self.rect.append([0.5-0.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(12)
        self._polygon_append([0.5-1.5*a,0.5-1.5*a,0.5-2*a,0.5-0.5*a,0.5+0.5*a,0.5])
        self._polygon_append([0.5+1.5*a,0.5+1.5*a,0.5+2*a,0.5-0.5*a,0.5+0.5*a,0.5])
        self._polygon_append([0.5-0.5*a,0.5+0.5*a,0.5,0.5-1.5*a,0.5-1.5*a,0.5-2*a])
        self._polygon_append([0.5-0.5*a,0.5+0.5*a,0.5,0.5+1.5*a,0.5+1.5*a,0.5+2*a])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)
        time.sleep(9)

        self.mm.magneticFieldGo(0,120)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        self.rect.append([0.5-1.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(12)
        self.rect.append([0.5+0.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)
        time.sleep(9)

        self.mm.magneticFieldGo(90,120)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(3)
        self.rect.append([0.5-0.5*a,0.5+0.5*a,a,a])
        self._show()
        self._cure()

        self.mm.motorgo(1,200)
        time.sleep(12)
        self.rect.append([0.5-0.5*a,0.5-1.5*a,a,a])
        self._show()
        self._cure()
        self.mm.motorgo(1,200)
        time.sleep(9)

    def _macro_batch_gripper(self):
        a = 0.035
        g = 0.17
        for i in range(8):
            for j in range(8):
                xOff = g * i
                yOff = g * j
                self.rect.append([xOff+a,yOff+a,a,a])
                self.rect.append([xOff+a,yOff,a,a])
                self.rect.append([xOff,yOff+a,a,a])
                self.rect.append([xOff+2*a,yOff+a,a,a])
                self.rect.append([xOff+a,yOff+2*a,a,a])

    def _macro_fabricate_pedal(self):
        x0 = 0
        y0 = 0
        # self.mm.magneticFieldGo(90,0)
        # while self.client.isBusy:
        #     time.sleep(.5)
        # time.sleep(2)
        self.rect.append([x0,       y0,         0.2,        0.8])
        self.rect.append([x0+0.2,   y0,         0.65,       0.2])
        self.rect.append([x0+0.2,   y0+0.6,    0.65,       0.2])
        self.rect.append([x0+0.85,  y0,         0.2,        0.8])
        self._show()
        self._cure()
        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.mm.magneticFieldGo(0,90)
        while self.client.isBusy:
            time.sleep(.5)
        self.rect.append([x0+0.6,   y0+0.25,     0.2,        0.3])
        self.rect.append([x0+0.2,   y0+0.3,    0.4,        0.2])
        self._show()
        self._cure()

# ==============================================================================
# Internal use
# ==============================================================================
    def _batch_rect_append(self,xo,yo,width,height,numX,numY,dx,dy):
        for i in range(numX):
            for j in range(numY):
                xOff = dx * i
                yOff = dy * j
                self.rect.append([xOff+xo,yOff+yo,width,height])

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

    def _cure(self):
        time_ms=self.exposureTime
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
