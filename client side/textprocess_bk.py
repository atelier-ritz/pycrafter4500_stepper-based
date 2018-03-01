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
            if name == 'gripperhinge':
                self._macro_gripper_hinge()
            if name == 'gripperthree':
                self._macro_gripper_three()
            if name == 'gripperfour':
                self._macro_gripper_four()
            if name == 'batchGripperTest':
                self._macro_batch_gripper()
            if name == 'swimmer':
                self._macro_fabricate_swimmer()
            if name == 'door':
                self._macro_fabricate_door()
            if name == 'swimmerb':
                self._macro_batch_fabricate_swimmer()
            if name == 'geit':
                self._macro_fabricate_tripodGeit2()
            if name == 'pedal':
                self._macro_fabricate_pedal()
            if name == 'macro1':
                self.mm.macro1()
            if name == 'macro2':
                self.mm.macro2()

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

    def _macro_gripper(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        hinge = 0.002 * p
        curingOrder = [2,3,1,5,4]
        ''' 1    2    3    4    5  '''  # pieceId
        ''' l1   l2   l3   l2   l1 '''  # length
        ''' L150 L120 U    R120 R150  '''  # magnetization
        ''' 2    3    1    5    4  '''  # curingOrder
        def f1(): self._showCureRect(-90,150+15, [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],osc=True,waitTime_s=120)
        def f2(): self._showCureRect(-90,120,    [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],osc=False,waitTime_s=40)
        def f3(): self._showCureRect(0,0,        [0.5-0.5*w,0.5-0.5*l3,      w,l3],osc=True,waitTime_s=120)
        def f4(): self._showCureRect(90,120,     [0.5-0.5*w,0.5+0.5*l3,      w,l2],osc=False,waitTime_s=40)
        def f5(): self._showCureRect(90,150+15,  [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],osc=True,waitTime_s=120)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_gripper_hinge(self):
        p = 0.9
        w = 0.25 * p
        hingeW = 0.5 * w
        arm = 0.12 * p
        finger = 0.12 * p
        body = 0.16 * p
        hinge = 0.08 * p
        self._showCureRect(90,180,[0.5-0.5*w,0.5+0.5*body+hinge+arm+hinge,w,finger],1200)# right finger
        self._showCureRect(90,180,[0.5-0.5*hingeW,0.5+0.5*body+hinge+arm,hingeW,hinge],800)
        self._showCureRect(90,120,[0.5-0.5*w,0.5+0.5*body+hinge,w,arm],1200) # right arm
        self._showCureRect(90,120,[0.5-0.5*hingeW,0.5+0.5*body,hingeW,hinge],800)
        self._showCureRect(0,0,[0.5-0.5*w,0.5-0.5*body,w,body],1200) #center
        self._showCureRect(-90,120,[0.5-0.5*hingeW,0.5-0.5*body-hinge,hingeW,hinge],800) # left arm
        self._showCureRect(-90,120,[0.5-0.5*w,0.5-0.5*body-hinge-arm,w,arm],1200)
        self._showCureRect(-90,180,[0.5-0.5*hingeW,0.5-0.5*body-hinge*2-arm,hingeW,hinge],800) # left finger
        self._showCureRect(-90,180,[0.5-0.5*w,0.5-0.5*body-hinge*2-arm-finger,w,finger],1200)

    def _macro_fabricate_door(self):
        p = 0.9
        w = 0.15*p
        gap = 0.08*p
        l = 0.3*p
        edge = 0.15*p

        self._showCureRect(90,90,[0.5+0.5*edge+gap,0.5-l-gap,w,l+gap])
        self._showCureRect(0,180,[0.5+0.5*edge+gap,0.5,w,l])
        self._showCureRect(0,180,[0.5-0.5*edge-gap-w,0.5-l,w,l])
        self._showCureRect(-90,90,[0.5-0.5*edge-gap-w,0.5,w,l+gap])

        self._field_go(0,0)
        self.rect.append([0.5-0.5*edge,0.5-l-gap,edge,2*l+2*gap])
        self.rect.append([0.5+0.5*edge+gap+w+gap,0.5-l-gap,edge,2*l+2*gap])
        self.rect.append([0.5-0.5*edge-gap-w-gap-edge,0.5-l-gap,edge,2*l+2*gap])
        self.rect.append([0.5-0.5*edge-gap-w-gap-edge,0.5-l-gap-edge,edge*3+gap*4+w*2,edge])
        self.rect.append([0.5-0.5*edge-gap-w-gap-edge,0.5+l+gap,edge*3+gap*4+w*2,edge])
        self._show()
        self._cure()

    def _macro_gripper_three(self):
        p = 0.6
        w = 0.3 * p
        arm = 0.35 * p
        finger = 0.2 * p

        self._field_go(0,0)
        self._polygon_append([0.5-w/(2*math.sqrt(3)),0.5-w/(2*math.sqrt(3)),0.5+w/(math.sqrt(3)),0.5-w/2,0.5+w/2,0.5])
        self._show()
        self._cure()



        self._field_go(0,150)
        self._polygon_append([0.5-w/(2*math.sqrt(3))-arm,0.5-w/(2*math.sqrt(3))-arm-finger,0.5-w/(2*math.sqrt(3))-arm,
                            0.5-w/2,0.5,0.5+w/2])
        self._show()
        self._cure()

        self._field_go(120,150)
        self._polygon_append([0.5-w/(2*math.sqrt(3))+arm/2, 0.5-w/(2*math.sqrt(3))+arm/2+w/4*math.sqrt(3)+finger/2, 0.5-w/(2*math.sqrt(3))+arm/2+w/2*math.sqrt(3),
                            0.5+w/2+arm/2*math.sqrt(3), 0.5+w/4+arm/2*math.sqrt(3)+finger/2*math.sqrt(3), 0.5+arm/2*math.sqrt(3)])
        self._show()
        self._cure()

        self._field_go(240,150)
        self._polygon_append([0.5-w/(2*math.sqrt(3))+arm/2,0.5-w/(2*math.sqrt(3))+arm/2+w/4*math.sqrt(3)+finger/2,0.5-w/(2*math.sqrt(3))+arm/2+w/2*math.sqrt(3),
                            0.5-w/2-arm/2*math.sqrt(3),0.5-w/4-arm/2*math.sqrt(3)-finger/2*math.sqrt(3),0.5-arm/2*math.sqrt(3)])
        self._show()
        self._cure()

        self._field_go(0,120)
        self._polygon_append([0.5-w/(2*math.sqrt(3)),0.5-w/(2*math.sqrt(3))-arm,0.5-w/(2*math.sqrt(3))-arm,0.5-w/(2*math.sqrt(3)),
                            0.5-w/2,0.5-w/2,0.5+w/2,0.5+w/2])

        self._show()
        self._cure()

        self._field_go(120,120)
        self._polygon_append([0.5-w/(2*math.sqrt(3)),0.5-w/(2*math.sqrt(3))+arm/2,0.5-w/(2*math.sqrt(3))+arm/2+w/2*math.sqrt(3),0.5+w/math.sqrt(3),
                            0.5+w/2,0.5+w/2+arm/2*math.sqrt(3),0.5+arm/2*math.sqrt(3),0.5])
        self._show()
        self._cure()

        self._field_go(240,120)
        self._polygon_append([0.5-w/(2*math.sqrt(3)),0.5-w/(2*math.sqrt(3))+arm/2,0.5-w/(2*math.sqrt(3))+arm/2+w/2*math.sqrt(3),0.5+w/math.sqrt(3),
                            0.5-w/2,0.5-w/2-arm/2*math.sqrt(3),0.5-arm/2*math.sqrt(3),0.5])
        self._show()
        self._cure()

    def _macro_gripper_four(self):
        a = 0.15
        hinge = 0.001

        self._field_go(0,0)
        self.rect.append([0.5-1.5*a-hinge,0.5-0.5*a,hinge,a])
        self.rect.append([0.5-0.5*a-hinge,0.5-0.5*a,hinge,a])
        self.rect.append([0.5+0.5*a-hinge,0.5-0.5*a,hinge,a])
        self.rect.append([0.5+1.5*a-hinge,0.5-0.5*a,hinge,a])
        self.rect.append([0.5-0.5*a,0.5-1.5*a-hinge,a,hinge])
        self.rect.append([0.5-0.5*a,0.5-0.5*a-hinge,a,hinge])
        self.rect.append([0.5-0.5*a,0.5+0.5*a-hinge,a,hinge])
        self.rect.append([0.5-0.5*a,0.5+1.5*a-hinge,a,hinge])
        self._show()
        self._cure()

        self._field_go(0,0)
        self.rect.append([0.5-0.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(0,120)
        self.rect.append([0.5-1.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(180,120)
        self.rect.append([0.5+0.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(90,120)
        self.rect.append([0.5-0.5*a,0.5+0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(270,120)
        self.rect.append([0.5-0.5*a,0.5-1.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(0,150)
        self.rect.append([0.5-2.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(180,150)
        self.rect.append([0.5+1.5*a,0.5-0.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(90,150)
        self.rect.append([0.5-0.5*a,0.5+1.5*a,a,a])
        self._show()
        self._cure()

        self._field_go(270,150)
        self.rect.append([0.5-0.5*a,0.5-2.5*a,a,a])
        self._show()
        self._cure()

    def _macro_fabricate_swimmer(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        hinge = 0.002 * p
        curingOrder = [4,1,3,2,5]
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        def f1(): self._showCureRect(90,90,   [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],osc=False,waitTime_s=5)
        def f2(): self._showCureRect(0,0,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],osc=True,waitTime_s=120)
        def f3(): self._showCureRect(-90,90,  [0.5-0.5*w,0.5-0.5*l3,      w,l3],osc=False,waitTime_s=5)
        def f4(): self._showCureRect(0,180,   [0.5-0.5*w,0.5+0.5*l3,      w,l2],osc=True,waitTime_s=120)
        def f5(): self._showCureRect(90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],osc=False,waitTime_s=5)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_batch_fabricate_swimmer(self): # doesn't cure in order
        pixel = 5
        width = 0.05
        length = 0.25
        lengthPerPixel = length/pixel

        self._field_go(0,0)
        self._batch_line_append(0,length,0.05,0.05,2,5,0.5,0.17)
        self._batch_line_append(length,length,0.05,0.05+width,2,5,0.5,0.17)
        self._batch_line_append(0,length,0.05+width,0.05+width,2,5,0.5,0.17)
        self._batch_line_append(0,0,0.05,0.05+width,2,5,0.5,0.17)
        self._show()
        self._cure()

        self._batch_rect_append(1*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        self._show()
        self._cure()

        self._field_go(0,180)
        self._batch_rect_append(3*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        self._show()
        self._cure()

        self._field_go(180,90)
        self._batch_rect_append(2*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        self._show()
        self._cure()

        self._field_go(0,90)
        self._batch_rect_append(4*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        self._batch_rect_append(0*lengthPerPixel,0.05,lengthPerPixel,width,2,5,0.5,0.17)
        self._show()
        self._cure()

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

    def _batch_rect_append(self,xo,yo,width,height,numX,numY,dx,dy):
        for i in range(numX):
            for j in range(numY):
                xOff = dx * i
                yOff = dy * j
                self.rect.append([xOff+xo,yOff+yo,width,height])

    def _showCureRect(self,phi,theta,rectArray,osc=False,waitTime_s=0,exposureTime_ms=0):
        self._field_go(phi,theta)
        if(osc):
            self.mm.macro1()
            time.sleep(15)
        if not waitTime_s == 0:
            self.mm.powerOff()
            time.sleep(waitTime_s)
            self.mm.powerOn()
        self.rect.append(rectArray)
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
