from plot import MyPlot
import numpy as np
import matplotlib
import pycrafter4500
import math
import time
import re
import mathfx


class TextProcess(object):
    def __init__(self,client,mm):
        self.line = [] # [[x1,x2,y1,y2],[],...]
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.cir = [] #
        self.ring = []
        self.polygon = []
        self.variables = {} # store the variables in the editor
        self.plot = MyPlot()
        self.exposureTime = 0
        self.intensityUV = 0
        self.client = client
        self.mm = mm

    def clear(self):
        self.line = []
        self.rect = [] # store the squares created by function "rect(x,y,w,h)"
        self.cir = []
        self.ring = []
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
            # if name == 'line':
            #     args = list(map(float, args))
            #     x1,x2,y1,y2 = args
            #     theta = math.atan2(y1-y2,x1-x2)
            #     w = 0.0001
            #     x = [x1-w*math.cos(theta),x2-w*math.cos(theta),x2+w*math.cos(theta),x1+w*math.cos(theta)]
            #     y = [y1-w*math.sin(theta),y2-w*math.sin(theta),y2+w*math.sin(theta),y1+w*math.sin(theta)]
            #     vertices = np.column_stack((x,y))
            #     item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
            #     self.polygon.append(item)
            if name == 'line':
                self.line.append(args)
                self._show()
            if name == 'rect':
                args = list(map(float, args))
                self.rect.append([args[0],args[1],args[2],args[3]])
            if name == 'ring':
                args = list(map(float, args))
                self.ring.append([args[0],args[1],args[2],args[3],args[4],args[5]])
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
            if name == 'sample':
                self._macro_sample()
            if name == 'tripod':
                self._macro_tripod() # only has up and down magnetization in the body
            if name == 'tripodneo':
                self._macro_tripodneo() # has <- and -> magnetization in the body
            if name == 'tripodneo2':
                self._macro_tripodneo2() # has <- and -> magnetization in the body
            if name == 'tripodthree':
                self._macro_tripodthree()
            if name == 'turtle':
                self._macro_turtle()
            if name == 'accordion':
                self._macro_accordion(int(args[0]))
            if name == 'pandemo':
                self._macro_pandemo()
            if name == 'capsule':
                self._macro_capsule()
            if name == 'capsule2':
                self._macro_capsule_twoarm()
            if name == 'magiccarpet':
                self._macro_carpet()
            if name == 'hatch':    # latch by -> ->
                self._macro_hatch()
            if name == 'hatchneo': #latch by -> and <- on top of each other
                self._macro_hatchneo()
            if name == 'gripper':
                self._macro_gripper()
            if name == 'gripperfour':
                self._macro_gripperfour()
            if name == 'multiaxis':
                self._macro_multiaxis()
            if name == 'grippermulti':
                self._macro_grippermulti()
            if name == 'twist':
                self._macro_twist()
            if name == 'swimmer':
                self._macro_swimmer()
            if name == 'swimmerdisp':
                self._macro_swimmerdisp()
            if name == 'cylinderr':
                self._macro_cylinder_r()
            if name == 'cylindera':
                self._macro_cylinder_a()
            if name == 'flagella':
                self._macro_flagella()
            if name == 'crawler': # crawling doghnut
                self._macro_crawler()
            if name == 'doghnut': # buckling ring
                self._macro_doghnut()
            if name == 'standingman':
                self._macro_standingman()
            if name == 'opticalstage':
                self._macro_opticalstage()
            if name == 'waves':
                self._macro_waves()
            if name == 'fingers':
                self._macro_fingers()
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
    def _macro_sample(self):
        ''' print an array of squares, triangles, and circles of different sizes '''
        # L1 squares
        # L2 circles
        # L3 triangles
        p = 0.2
        ox1 = 0 * p + 0.2
        ox2 = 0.3 * p + 0.4
        ox3 = 0.6 * p + 0.6
        for i in range(6):
            h = 0.09 * (0.8**i) * p
            self.rect.append([ox1,0.3+i*0.05,h,h])
        for i in range(6):
            r = 0.09 * 0.5 * (0.8**i) * p
            self.cir.append([ox2+r,0.3+i*0.05+r,r])
        for i in range(6):
            a = 0.09 * (0.8**i) * p
            x = [ox3,ox3,ox3 + 1.732*0.5*a]
            y = [0.3+i*0.05,0.3+i*0.05+a,0.3+i*0.05+0.5*a]
            vertices = np.column_stack((x,y))
            item = matplotlib.patches.Polygon(vertices,closed=True,color='white')
            self.polygon.append(item)
        self._show()
        # self._cure(800)

    def _macro_carpet(self):
        p = 0.8
        w = 0.4 * p
        l1 = 0.1 * p
        l2 = 0.1 * p
        curingOrder = [1,2,3,4,5]

        def f1():
            self.rect.append([0.5-0.5*w,0.5-0.5*w,w,w])
            self.rect.append([0.5-0.5*w-2*l2-l1,0.5-0.5*w,l1,w])
            self.rect.append([0.5+0.5*w+2*l2,0.5-0.5*w,l1,w])
            self.rect.append([0.5-0.5*w,0.5-0.5*w-2*l2-l1,w,l1])
            self.rect.append([0.5-0.5*w,0.5+0.5*w+2*l2,w,l1])
            # self._showCureRect(-90,90, [0.5+0.5*w,0.5-0.5*l_body-l_leg,w,l_leg],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():#U
            self.rect.append([0.5+0.5*w,0.5-0.5*w,l2,w])
            self.rect.append([0.5-0.5*w-2*l2,0.5-0.5*w,l2,w])
            # self._showCureRect(0,0,    [0.5+w,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f3():#D
            self.rect.append([0.5+0.5*w+l2,0.5-0.5*w,l2,w])
            self.rect.append([0.5-0.5*w-l2,0.5-0.5*w,l2,w])
            # self._showCureRect(-90,90,        [0.5+0.5*w,0.5+0.5*l_body,     w,l_leg],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f4():#L
            self.rect.append([0.5-0.5*w,0.5-0.5*w-l2,w,l2])
            self.rect.append([0.5-0.5*w,0.5+0.5*w+l2,w,l2])
            # self._showCureRect(0,180,     [0.5  ,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f5():#R
            self.rect.append([0.5-0.5*w,0.5-0.5*w-2*l2,w,l2])
            self.rect.append([0.5-0.5*w,0.5+0.5*w,w,l2])
            # self._showCureRect(0,0,  [0.5-w,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        # self._field_go(0,90)
        self._show()

    def _macro_turtle(self):
        p = 0.4
        w = 0.25 * p
        l_leg = 0.35 * p
        l_body = 0.2 * p
        curingOrder = [5,1,6,3,2,7,4,8]

        # ''' boundaries '''
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3      ,0.5-0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3      ,0.5+0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2   ,0.5+0.5*l3+l2   ])
        # self._show()
        # self._cure(800)
        # ''' boundaries '''
        def f1(): self._showCureRect(-90,90, [0.5+0.5*w,0.5-0.5*l_body-l_leg,w,l_leg],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2(): self._showCureRect(0,0,    [0.5+w,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f3(): self._showCureRect(-90,90,        [0.5+0.5*w,0.5+0.5*l_body,     w,l_leg],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f4(): self._showCureRect(0,180,     [0.5  ,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f5(): self._showCureRect(0,0,  [0.5-w,0.5-0.5*l_body,     w,l_body],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f6():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90,        [0.5-1.5*w,0.5-0.5*l_body-l_leg,w,l_leg],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f7(): self._showCureRect(0,180,     [0.5-2*w,0.5-0.5*l_body,      w,l_body],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f8(): self._showCureRect(90,90,  [0.5-1.5*w,0.5+0.5*l_body,      w,l_leg],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_tripodneo(self):
        p = 0.8
        wl = 0.1 * p#0.14
        ll = 0.14 * p#0.2
        wb = 0.8 * p
        lb = 0.03 * p #0.05
        wg = 0.03 * p #0.04
        lg = 0.07 * p #0.1
        wg2 = (wb - 4 * wg)/8
        curingOrder = [1,2]

        ''' boundaries '''
        def f1():
            # self._field_go(90,15)
            # time.sleep(10)
            self.rect.append([0.5-2*wg-3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5       +wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-2*wg-3*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])

            self.rect.append([0.5-0.5*wb,0.5-0.5*lb,wb,0.5*lb])#left body
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            # self._showCureRect(-90,90, [0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        def f2():
            # self._field_go(90,15)
            # time.sleep(10)
            self.rect.append([0.5-wg-wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-wg-wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])

            self.rect.append([0.5-0.5*wb,0.5,wb,0.5*lb])# right body
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            # self._showCureRect(90,90,[0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        def f3():
            self.rect.append([0.5-0.1*wb,0.5-0.5*lb,0.2*wb,lb])#mid
            self._showCureRect(0,90, [0.5-0.1*wb,0.5-0.5*lb,0.2*wb,lb],oscAzimuth=True,oscPolar=True,waitTime_s=60)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        # self._field_go(0,90)
        self._show()


    def _macro_tripodneo2(self):
        p = 0.8
        wl = 0.1 * p#0.14
        ll = 0.14 * p#0.2
        wb = 0.8 * p
        lb = 0.03 * p #0.05
        wg = 0.03 * p #0.04
        lg = 0.07 * p #0.1
        wg2 = (wb - 4 * wg)/8
        curingOrder = [1,2]

        ''' boundaries '''
        def f1():
            # self._field_go(90,15)
            # time.sleep(10)
            self.rect.append([0.5+wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-wg-wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-2*wg-3*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5-0.5*wb,0.5-0.5*lb,wb,0.5*lb])#left body
            self._showCureRect(-90,90, [0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        def f2():
            self._field_go(90,15)
            time.sleep(10)
            self.rect.append([0.5       +wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-wg-wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5-2*wg-3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])

            self.rect.append([0.5-0.5*wb,0.5,wb,0.5*lb])# right body
            self._showCureRect(90,90,[0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)
        # self._show()

    def _macro_tripodthree(self):
        p = 0.5
        wl = 0.16 * p  #0.16
        ll = 0.2 * p
        wb = 0.7 * p
        lb = 0.05 * p
        wg = 0.05 * p
        lg = 0.05 * p #0.1
        wg2 = (wb - 3 * wg)/6
        curingOrder = [3,4,1,2]

        def f1():
            self.rect.append([0.5-1.5*wg-2*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-1*wg-2*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-1.5*wg-2*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-1*wg-2*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+0.5*wg+2*wg2,0.5-0.5*lb-lg,wg,lg+lg])
            self.rect.append([0.5+1*wg+2*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5+0.5*wg+2*wg2,0.5+0.5*lb,wg,lg])
            self._showCureRect(-90,90, [0.5+1*wg+2*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():
            self._field_go(90,15)
            time.sleep(10)
            self.rect.append([0.5-0.5*wg,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-0.5*wg,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self._showCureRect(90,90,[0.5-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f3():
            self.rect.append([0.5-0.5*wb,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+2*wg2+1*wg,0.5-0.5*lb,wg2,lb])
            self._showCureRect(0,0, [0.5-0.5*wb+4*wg2+2*wg,0.5-0.5*lb,wg2,lb],oscAzimuth=True,oscPolar=True,waitTime_s=40)
        def f4():
            self.rect.append([0.5-0.5*wb+1*wg2+1*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+3*wg2+2*wg,0.5-0.5*lb,wg2,lb])
            self._showCureRect(0,180,[0.5-0.5*wb+5*wg2+3*wg,0.5-0.5*lb,wg2,lb],oscAzimuth=True,oscPolar=True,waitTime_s=40)

        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_tripod(self):
        p = 0.4
        wl = 0.16 * p
        ll = 0.2 * p
        wb = 1.0 * p
        lb = 0.05 * p #0.05
        wg = 0.04 * p #0.04
        lg = 0.09 * p #0.1
        wg2 = (wb - 4 * wg)/8
        curingOrder = [1,2]
        ''' boundaries '''
        def f1():
            self.rect.append([0.5-0.5*wb,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+1*wg2+1*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+4*wg2+2*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+5*wg2+3*wg,0.5-0.5*lb,wg2,lb])


            self.rect.append([0.5-2*wg-3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5       +wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+0.5*wg+wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-2*wg-3*wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-1.5*wg-3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+wg2,0.5+0.5*lb,wg,lg])
            self._showCureRect(-90,90, [0.5+0.5*wg+wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():
            self._field_go(90,15)
            time.sleep(10)

            self.rect.append([0.5-0.5*wb+2*wg2+1*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+3*wg2+2*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+7*wg2+4*wg,0.5-0.5*lb,wg2,lb])
            self.rect.append([0.5-0.5*wb+6*wg2+3*wg,0.5-0.5*lb,wg2,lb])

            self.rect.append([0.5-wg-wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5-0.5*lb-lg,wg,lg+lb])
            self.rect.append([0.5+1.5*wg+3*wg2-0.5*wl,0.5-0.5*lb-lg-ll,wl,ll])
            self.rect.append([0.5-wg-wg2,0.5+0.5*lb,wg,lg])
            self.rect.append([0.5-0.5*wg-1*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll])
            self.rect.append([0.5+wg+3*wg2,0.5+0.5*lb,wg,lg])
            self._showCureRect(90,90,[0.5+1.5*wg+3*wg2-0.5*wl,0.5+0.5*lb+lg,wl,ll],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)


    def _macro_accordion(self,num):
        p = 0.9
        l = 0.5 / num * p
        w = 0.6 * p
        for i in range(num):
            self.rect.append([0.5-0.5*w,0.5-l*num + i * 2 * l,w,l*0.8])
            self.rect.append([0.5-0.5*0.5*w,0.5-l*num + i * 2 * l+l*0.9,w*0.5,l*0.2])
        self._showCureRect(90,90,    [0.5-0.5*w,0.5-l*num,w,l],oscAzimuth=True,oscPolar=False,waitTime_s=15)
        self._field_go(-90,25)
        time.sleep(10)
        for i in range(num):
            if not i == 2:
                self.rect.append([0.5-0.5*w,0.5-l*num + l + i * 2 * l,w,l*0.8])
                self.rect.append([0.5-0.5*0.5*w,0.5-l*num + l + i * 2 * l+ l*0.9,w*0.5,l*0.2])
            else:
                self.rect.append([0.5-0.5*w,0.5-l*num + l + i * 2 * l,w,l])
        self._showCureRect(-90,90,   [0.5-0.5*w,0.5-l*num + l,w,l],oscAzimuth=True,oscPolar=False,waitTime_s=15)
        # self._show()

    def _macro_capsule(self):
        p = 0.6
        w_body = 0.8 * p
        w = 0.25 * p
        w_hatch = 0.1 * p
        l_body = 0.4 * p
        l = 0.12 * p
        curingOrder = [1,4,2,5,3,6]

        # ''' boundaries '''
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3      ,0.5-0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3      ,0.5+0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2   ,0.5+0.5*l3+l2   ])
        # self._show()
        # self._cure(800)
        # ''' boundaries '''
        def f1(): self._showCureRect(0,0, [0.5-0.5*w_body,0.5-(l_body+5*l),w_body,l_body],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f2():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90,    [0.5-0.5*w,0.5-(l_body+5*l)+l_body,w,l],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f3(): self._showCureRect(0,0,        [0.5-0.5*w,0.5-(l_body+5*l)+l_body+l,w,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f4(): self._showCureRect(90,90,    [0.5-0.5*w,0.5-(l_body+5*l)+l_body+l*2,w,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f5(): self._showCureRect(0,180,  [0.5-0.5*w,0.5-(l_body+5*l)+l_body+l*3,w,l],oscAzimuth=False,oscPolar=True,waitTime_s=40)
        def f6():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,       [0.5-0.5*w_hatch,0.5-(l_body+5*l)+l_body+l*4,w_hatch,l],oscAzimuth=True,oscPolar=False,waitTime_s=10)

        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_capsule_twoarm(self):
        p = 0.55 #.8
        w_body = 0.7 * p
        w = 0.3 * p
        l_body = 0.25 * p
        l3 = 0.12 * p
        l2 = 0.15 * p
        l1 = 0.2 * p
        center_a = 0.001 #0.09
        curingOrder = [5,7,2,3,4,6,8,1]

        # ''' boundaries '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.line.append([0.5-0.5*center_a,0.5-0.5*center_a,0.5+0.5*center_a,0.5-0.5*center_a])
        self.line.append([0.5+0.5*center_a,0.5+0.5*center_a,0.5+0.5*center_a,0.5-0.5*center_a])
        self.line.append([0.5-0.5*center_a,0.5+0.5*center_a,0.5-0.5*center_a,0.5-0.5*center_a])
        self.line.append([0.5-0.5*center_a,0.5+0.5*center_a,0.5+0.5*center_a,0.5+0.5*center_a])
        self._show()
        self._cure(800)
        # ''' boundaries '''
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90, [0.5-0.5*w,0.5-0.5*l_body-l1-l2-l3,w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,    [0.5-0.5*w,0.5-0.5*l_body-l2-l3,w,l2],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f3(): self._showCureRect(0,0,        [0.5-0.5*w,0.5-0.5*l_body-l3,w,l3],oscAzimuth=True,oscPolar=True,waitTime_s=40)
        def f4(): self._showCureRect(0,0,    [0.5-0.5*w_body,0.5-0.5*l_body,w_body,l_body],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f5(): self._showCureRect(0,0,  [0.5-0.5*w,0.5+0.5*l_body,w,l3],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f6():
            self._showCureRect(90,90,       [0.5-0.5*w,0.5+0.5*l_body+l3,w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f7():
            self._showCureRect(-90,90,       [0.5-0.5*w,0.5+0.5*l_body+l3+l2,w,l1],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f8(): #center block
            self._showCureRect(90,90,       [0.5-0.5*center_a,0.5-0.5*center_a,center_a,center_a],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_hatch(self):
        p = 0.6
        w = 0.48 * p
        w_hatch = 0.4 * p #0.15
        l1 = 0.6 * p
        l2 = 0.2 * p
        l3 = 0.09 * p
        curingOrder = [2,3,1]

        def f1(): self._showCureRect(90,20,   [0.5-0.5*w,0.5-0.5*(l1+l2+l3),w,l1],oscAzimuth=True,oscPolar=True,waitTime_s=35)
        def f2(): self._showCureRect(90,90, [0.5-0.5*w,0.5-0.5*(l1+l2+l3)+l1,w,l2],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f3(): self._showCureRect(0,180, [0.5-0.5*w_hatch,0.5-0.5*(l1+l2+l3)+l1+l2,w_hatch,l3],oscAzimuth=False,oscPolar=True,waitTime_s=35)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_hatchneo(self):
        p = 0.6
        w_latch = 0.15 * p
        w_arm = 0.2 * p
        w_base = 0.6 * p
        w = w_latch + w_arm + w_base
        l = 0.48 * p
        l_latch = 0.12 * p
        curingOrder = [1,2,3]

        ''' boundary '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.line.append([0.5+0.5*w-w_latch,0.5+0.5*w-w_latch,0.5-0.5*l_latch,0.5+0.5*l_latch])
        self.line.append([0.5+0.5*w-w_latch-w_arm,0.5+0.5*w-w_latch-w_arm,0.5-0.5*l,0.5+0.5*l])
        self.line.append([0.5+0.5*w-w_latch-2.5*w_arm,0.5+0.5*w-w_latch-2.5*w_arm,0.5-0.5*l_latch,0.5+0.5*l_latch])
        self.line.append([0.5+0.5*w-w_latch-2.5*w_arm-w_latch,0.5+0.5*w-w_latch-2.5*w_arm-w_latch,0.5-0.5*l_latch,0.5+0.5*l_latch])
        self.line.append([0.5+0.5*w-w_latch-2.5*w_arm,0.5+0.5*w-w_latch-2.5*w_arm-w_latch,0.5-0.5*l_latch,0.5-0.5*l_latch])
        self.line.append([0.5+0.5*w-w_latch-2.5*w_arm,0.5+0.5*w-w_latch-2.5*w_arm-w_latch,0.5+0.5*l_latch,0.5+0.5*l_latch])
        self._show()
        self._cure(800)

        def f1():
            self.rect.append([0.5+0.5*w-w_latch-2.5*w_arm,0.5-0.5*l_latch,w_latch,l_latch])
            self._showCureRect(0,90,  [0.5+0.5*w-w_latch,0.5-0.5*l_latch,w_latch,l_latch],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f2():
            self._showCureRect(0,0, [0.5-0.5*w,0.5-0.5*l,w_base,l],oscAzimuth=True,oscPolar=True,waitTime_s=40)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90, [0.5+0.5*w-w_latch-w_arm,0.5-0.5*l,w_arm,l],oscAzimuth=True,oscPolar=True,waitTime_s=35)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_multiaxis(self):
        p = 0.7
        w = 0.23 * p
        r = 0.5 * p
        w_hinge = 0.6 * w
        segment = 3
        startSegment = 0.05
        endSegment = 0.95

        for i in range(segment):
            angle1 = 90+90/segment+360/segment*i
            angle2 = 270/segment-90+360/segment*i
            self.ring.append([0.5,0.5,r-0.5*w_hinge,(w-w_hinge),360/segment*i + 0.0*180/segment, 360/segment*i + startSegment*180/segment])
            self.ring.append([0.5,0.5,r,w*1.0,360/segment*i + startSegment*180/segment, 360/segment*i + endSegment*180/segment])
            self.ring.append([0.5,0.5,r-0.5*w_hinge,(w-w_hinge),360/segment*i + endSegment*180/segment, 360/segment*i + 1.0*180/segment])
            self._showCureRect(int(180-angle1),90, [0,0,0.0001,0.0001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
            self._field_go(int(180-angle1),40)
            self.ring.append([0.5,0.5,r-0.5*w_hinge,(w-w_hinge),360/segment*i + 1.0*180/segment, 360/segment*i + (1+startSegment)*180/segment])
            self.ring.append([0.5,0.5,r,w*1.0,360/segment*i + (1+startSegment)*180/segment, 360/segment*i + (1+endSegment)*180/segment])
            self.ring.append([0.5,0.5,r-0.5*w_hinge,(w-w_hinge),360/segment*i + (1+endSegment)*180/segment, 360/segment*i + 2.0*180/segment])
            self.ring.append([0.5,0.5,r,w, 360/segment*i + 180/segment, 360/segment*(i+1)])
            self._showCureRect(int(180-angle2),90, [0,0,0.0001,0.0001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
            self._field_go(int(180-angle2),40)
        self._field_go(0,90)
        # self._show()

    def _macro_gripper(self):
        p = 0.6
        w = 0.48 * p
        l1 = 0.14 * p
        l2 = 0.14 * p
        l3 = 0.24 * p
        gw = w * 0.5
        gl = 0.015 * p
        curingOrder = [2,3,1,5,4]
        ''' 1    2    3    4    5  '''  # pieceId
        ''' l1   l2   l3   l2   l1 '''  # length
        ''' L150 L120 U    R120 R150  '''  # magnetization
        ''' 2    3    1    5    4  '''  # curingOrder

        def f1():
            self.rect.append([0.5-0.5*gw,0.5-0.5*l3-gl-l2-gl,gw,gl])
            self.rect.append([0.5-0.5*w,0.5-0.5*l3-l2-l1-2*gl,w,l1])
            # self._showCureRect(-90,150+15, [0.5-0.5*w,0.5-0.5*l3-l2-l1-2*gl,w,l1],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f2():
            self.rect.append([0.5-0.5*gw,0.5-0.5*l3-gl,gw,gl])
            self.rect.append([0.5-0.5*w,0.5-0.5*l3-gl-l2,   w,l2])
            # self._showCureRect(-90,120,    [0.5-0.5*w,0.5-0.5*l3-gl-l2,   w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f3():
            self.rect.append( [0.5-0.5*w,0.5-0.5*l3,      w,l3])
            # self._showCureRect(0,0,        [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f4():
            self.rect.append([0.5-0.5*gw,0.5+0.5*l3,gw,gl])
            self.rect.append([0.5-0.5*w,0.5+0.5*l3+gl,      w,l2])
            # self._showCureRect(90,120,     [0.5-0.5*w,0.5+0.5*l3+gl,      w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f5():
            self.rect.append([0.5-0.5*gw,0.5+0.5*l3+gl+l2,gw,gl])
            self.rect.append([0.5-0.5*w,0.5+0.5*l3+l2+gl*2,   w,l1])
            # self._showCureRect(90,150+15,  [0.5-0.5*w,0.5+0.5*l3+l2+gl*2,   w,l1],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._show()
        # self._field_go(0,90)

    def _macro_gripperfour(self):
        p = 0.6
        w = 0.25 * p
        l1 = 0.25 * p
        l2 = 0.25 * p
        l3 = w
        curingOrder = [2,3,1,5,4,6,7,9,8]
        ''' 1    2    3    4    5  '''  # pieceId
        ''' l1   l2   l3   l2   l1 '''  # length
        ''' L150 L120 U    R120 R150  '''  # magnetization
        ''' 2    3    1    5    4  '''  # curingOrder

        # ''' boundaries '''
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        #
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3      ,0.5-0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3      ,0.5+0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2   ,0.5+0.5*l3+l2   ])
        #
        # self.line.append([0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1,0.5-0.5*w,0.5+0.5*w])
        # self.line.append([0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1,0.5-0.5*w,0.5+0.5*w])
        # self.line.append([0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1,0.5-0.5*w,0.5-0.5*w])
        # self.line.append([0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1,0.5+0.5*w,0.5+0.5*w])
        #
        # self.line.append([0.5-0.5*l3-l2,0.5-0.5*l3-l2,0.5-0.5*w,0.5+0.5*w])
        # self.line.append([0.5+0.5*l3+l2,0.5+0.5*l3+l2,0.5-0.5*w,0.5+0.5*w])
        # self.line.append([0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1,0.5-0.5*w,0.5+0.5*w])
        # self.line.append([0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1,0.5-0.5*w,0.5+0.5*w])
        # self._field_go(0,0)
        # self._show()
        # self._cure(800)
        # ''' boundaries '''
        def f1():
            self.rect.append([0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1*.8])
            self._showCureRect(-90,150+15, [0.5-0.5*w*.8,0.5-0.5*l3-l2-l1,w*.8,l1],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f2(): self._showCureRect(-90,120,    [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f3(): self._showCureRect(0,0,        [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f4(): self._showCureRect(90,120,     [0.5-0.5*w,0.5+0.5*l3,      w,l2],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f5():
            self.rect.append([0.5-0.5*w,0.5+0.5*l3+l2+.2*l1,w,l1*.8])
            self._showCureRect(90,150+15,  [0.5-0.5*w*.8,0.5+0.5*l3+l2,   w*.8,l1],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        def f6():
            self.rect.append([0.5-0.5*l3-l2-l1,0.5-0.5*w,l1*.8,w])
            self._showCureRect(0,150+15,   [0.5-0.5*l3-l2-l1,0.5-0.5*w*.8,l1,w*.8],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        def f7(): self._showCureRect(0,120,      [0.5-0.5*l3-l2   ,0.5-0.5*w,l2,w],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f8(): self._showCureRect(180,120,    [0.5+0.5*l3      ,0.5-0.5*w,l2,w],oscAzimuth=False,oscPolar=False,waitTime_s=40)
        def f9():
            self.rect.append([0.5+0.5*l3+l2+.2*l1,0.5-0.5*w,l1*.8,w])
            self._showCureRect(180,150+15, [0.5+0.5*l3+l2   ,0.5-0.5*w*.8,l1,w*.8],oscAzimuth=True,oscPolar=True,waitTime_s=120)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    #
    def _macro_grippermulti(self):
        p = 0.6
        n = 3
        w = 0.2 * p
        l1 = 0.2 * p
        l2 = 0.2 * p
        gw1 = w * 0.5     # width of the hinge 0.5
        gl1 = l1 * 0.2   # length of the hinge 0.2
        gw2 = w * 0.5
        gl2 = l2 * 0.2

        # x1 and y1 are points in the first quadrant.
        y1 = 0.5 + w / 2
        x1 = 0.5 + (w / 2) / mathfx.tand(180/n)
        xArray = []
        yArray = []

        # base
        for i in range(0,n):
            xNew, yNew = mathfx.rotatePoint(origin=(0.5,0.5),point=(x1,y1),angle=(360/n*i))
            xArray.append(xNew)
            yArray.append(yNew)
        xArray = [1-i for i in xArray] # mapping of matlibplot coordinate to the actual coordinate
        pointsArray = xArray + yArray # [x1,x2,x3,...,xn,y1,y2,y3,...,yn]
        self._polygon_append(pointsArray)
        self._showCureRect(0,0,[0,0,0,0],oscAzimuth=True,oscPolar=True,waitTime_s=120)

        for i in range(0,n):
            # arm_far
            # square tip
            # xArray = [x1+l1+gl1,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1+gl2+l2,x1+l1+gl1+gl2+l2,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1]
            # yArray = [0.5-0.5*gw1,0.5-0.5*gw1,0.5-0.5*w,0.5-0.5*w,0.5+0.5*w,0.5+0.5*w,0.5+0.5*gw1,0.5+0.5*gw1]
            # triangular tip
            xArray = [x1+l1+gl1,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1+gl2+l2,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1]
            yArray = [0.5-0.5*gw1,0.5-0.5*gw1,0.5-0.5*w,0.5,0.5+0.5*w,0.5+0.5*gw1,0.5+0.5*gw1]
            xNewArray, yNewArray = mathfx.rotatePointArray((0.5,0.5),xArray,yArray,(360/n*i))
            xNewArray = [1-i for i in xNewArray] # mapping of matlibplot coordinate to the actual coordinate
            self._polygon_append(xNewArray + yNewArray)
            self._showCureRect(int(360/n*i),160,[0,0,0,0],oscAzimuth=True,oscPolar=True,waitTime_s=120)

            # arm_close
            xArray = [x1,x1+gl1,x1+gl1,x1+gl1+l1,x1+gl1+l1,x1+gl1,x1+gl1,x1]
            yArray = [0.5-0.5*gw1,0.5-0.5*gw1,0.5-0.5*w,0.5-0.5*w,0.5+0.5*w,0.5+0.5*w,0.5+0.5*gw1,0.5+0.5*gw1]
            xNewArray, yNewArray = mathfx.rotatePointArray((0.5,0.5),xArray,yArray,(360/n*i))
            xNewArray = [1-i for i in xNewArray] # mapping of matlibplot coordinate to the actual coordinate
            self._polygon_append(xNewArray + yNewArray)
            self._showCureRect(int(360/n*i),125,[0,0,0,0],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        self._show()
        self._field_go(0,90)

    # def _macro_grippermulti(self):
    #     p = 0.2
    #     n = 4
    #     w = 0.7 * p
    #     l1 = 0.7 * p
    #     l2 = 0.606 * p
    #     gw1 = w * 0.214     # width of the hinge 0.8
    #     gl1 = l1 * 0.143   # length of the hinge 0.09
    #     gw2 = w * 0.214
    #     gl2 = l1 * 0.143
    #
    #     # x1 and y1 are points in the first quadrant.
    #     y1 = 0.5 + w / 2
    #     x1 = 0.5 + (w / 2) / mathfx.tand(180/n)
    #     xArray = []
    #     yArray = []
    #
    #     # base
    #     for i in range(0,n):
    #         xNew, yNew = mathfx.rotatePoint(origin=(0.5,0.5),point=(x1,y1),angle=(360/n*i))
    #         xArray.append(xNew)
    #         yArray.append(yNew)
    #     xArray = [1-i for i in xArray] # mapping of matlibplot coordinate to the actual coordinate
    #     pointsArray = xArray + yArray # [x1,x2,x3,...,xn,y1,y2,y3,...,yn]
    #     self._polygon_append(pointsArray)
    #     self._showCureRect(0,0,[0,0,0,0],oscAzimuth=True,oscPolar=True,waitTime_s=120)
    #
    #     for i in range(0,n):
    #         # arm_far
    #         xArray = [x1+l1+gl1,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1+gl2+l2,x1+l1+gl1+gl2,x1+l1+gl1+gl2,x1+l1+gl1]
    #         yArray = [0.5-0.5*gw1,0.5-0.5*gw1,0.5-0.5*w,0.5,0.5+0.5*w,0.5+0.5*gw1,0.5+0.5*gw1]
    #         xNewArray, yNewArray = mathfx.rotatePointArray((0.5,0.5),xArray,yArray,(360/n*i))
    #         xNewArray = [1-i for i in xNewArray] # mapping of matlibplot coordinate to the actual coordinate
    #         self._polygon_append(xNewArray + yNewArray)
    #         self._showCureRect(int(360/n*i),180,[0,0,0,0],oscAzimuth=True,oscPolar=True,waitTime_s=100)
    #
    #         # arm_close
    #         xArray = [x1,x1+gl1,x1+gl1,x1+gl1+l1,x1+gl1+l1,x1+gl1,x1+gl1,x1]
    #         yArray = [0.5-0.5*gw1,0.5-0.5*gw1,0.5-0.5*w,0.5-0.5*w,0.5+0.5*w,0.5+0.5*w,0.5+0.5*gw1,0.5+0.5*gw1]
    #         xNewArray, yNewArray = mathfx.rotatePointArray((0.5,0.5),xArray,yArray,(360/n*i))
    #         xNewArray = [1-i for i in xNewArray] # mapping of matlibplot coordinate to the actual coordinate
    #         self._polygon_append(xNewArray + yNewArray)
    #         self._showCureRect(int(360/n*i),115,[0,0,0,0],oscAzimuth=True,oscPolar=False,waitTime_s=30)
    #     self._show()
    #     self._field_go(0,90)

    def _macro_twist(self):
        p = 0.4
        w = 0.3 * p
        l1 = 0.8 * p
        l2 = 0.5 * p
        curingOrder = [2,1,3]
        def f1():
            self._field_go(180,15)
            time.sleep(10)
            self._showCureRect(180,90,   [0.5-0.5*l1,0.5-0.5*l2-w, l1, w],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f2(): self._showCureRect(0,0,     [0.5-0.5*w,0.5-0.5*l2,    w,  l2],oscAzimuth=False,oscPolar=True,waitTime_s=20)
        def f3():
            self._field_go(0,15)
            time.sleep(10)
            self._showCureRect(0,90,  [0.5-0.5*l1,0.5+0.5*l2,   l1, w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_swimmer(self):
        p = 0.75
        w = 0.3 * p
        l1 = 0.125 * p#0.13
        l2 = 0.275 * p#0.23
        l3 = 0.2 * p#0.23
        curingOrder = [4,1,3,2,5] #41325
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        # self.rect.append([0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1])
        # self.rect.append([0.5-0.5*w,0.5-0.5*l3-l2,   w,l2])
        # self.rect.append([0.5-0.5*w,0.5-0.5*l3,      w,l3])
        # self.rect.append([0.5-0.5*w,0.5+0.5*l3,      w,l2])
        # self.rect.append([0.5-0.5*w,0.5+0.5*l3+l2,   w,l1])
        # self._show()
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self.rect.append([0.5+0.25*w,0.5-0.5*l3-l2-l1,w,l1])
            self._showCureRect(90,90,         [0.5-1.25*w,0.5-0.5*l3-l2-l1,w,l1],oscAzimuth=True,oscPolar=True,waitTime_s=40)
        def f2():
            self.rect.append([0.5+0.25*w,0.5-0.5*l3-l2,   w,l2])
            self._showCureRect(0,0,     [0.5-1.25*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self.rect.append([0.5+0.25*w,0.5-0.5*l3,      w,l3])
            self._showCureRect(-90,90,  [0.5-1.25*w,0.5-0.5*l3,      w,l3],oscAzimuth=True,oscPolar=True,waitTime_s=40)
        def f4():
            self.rect.append([0.5+0.25*w,0.5+0.5*l3,      w,l2])
            self._showCureRect(0,180,   [0.5-1.25*w,0.5+0.5*l3,      w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f5():
            self.rect.append([0.5+0.25*w,0.5+0.5*l3+l2,   w,l1])
            self._showCureRect(90,90,   [0.5-1.25*w,0.5+0.5*l3+l2,   w,l1],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_swimmerdisp(self):
        p = 0.75
        w = 0.3 * p
        curingOrder = [4,1,3,2,5] #41325
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        l1 = [0.125,0.1625,0.2]
        l2 = [0.275,0.2,0.125]
        l3 = [0.2,0.275,0.35]
        l1 = [p*i for i in l1]
        l2 = [p*i for i in l2]
        l3 = [p*i for i in l3]
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self.rect.append([0.5+0.8*w,0.5-0.5*l3[0]-l2[0]-l1[0],w,l1[0]])
            self.rect.append([0.5-0.5*w,0.5-0.5*l3[1]-l2[1]-l1[1],w,l1[1]])
            self.rect.append([0.5-1.8*w,0.5-0.5*l3[2]-l2[2]-l1[2],w,l1[2]])
            self._showCureRect(90,90,[0,0,0.0001,0.0001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        def f2():
            self.rect.append([0.5+0.8*w,0.5-0.5*l3[0]-l2[0],w,l2[0]])
            self.rect.append([0.5-0.5*w,0.5-0.5*l3[1]-l2[1],w,l2[1]])
            self.rect.append([0.5-1.8*w,0.5-0.5*l3[2]-l2[2],w,l2[2]])
            self._showCureRect(0,0,     [0,0,0.0001,0.0001],oscAzimuth=False,oscPolar=True,waitTime_s=60)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self.rect.append([0.5+0.8*w,0.5-0.5*l3[0],      w,l3[0]])
            self.rect.append([0.5-0.5*w,0.5-0.5*l3[1],      w,l3[1]])
            self.rect.append([0.5-1.8*w,0.5-0.5*l3[2],      w,l3[2]])
            self._showCureRect(-90,90,  [0,0,0.0001,0.0001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        def f4():
            self.rect.append([0.5+0.8*w,0.5+0.5*l3[0],      w,l2[0]])
            self.rect.append([0.5-0.5*w,0.5+0.5*l3[1],      w,l2[1]])
            self.rect.append([0.5-1.8*w,0.5+0.5*l3[2],      w,l2[2]])
            self._showCureRect(0,180,   [0,0,0.0001,0.0001],oscAzimuth=False,oscPolar=True,waitTime_s=60)
        def f5():
            self.rect.append([0.5+0.8*w,0.5+0.5*l3[0]+l2[0],   w,l1[0]])
            self.rect.append([0.5-0.5*w,0.5+0.5*l3[1]+l2[1],   w,l1[1]])
            self.rect.append([0.5-1.8*w,0.5+0.5*l3[2]+l2[2],   w,l1[2]])
            self._showCureRect(90,90,   [0,0,0.0001,0.0001],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        # self._show()
        self._field_go(0,90)

    def _macro_cylinder_r(self):
        p = 0.65
        w = 0.48 * p
        l1 = 0.25 * p
        l2 = 0.23 * p
        l3 = 0.23 * p
        curingOrder = [4,1,3,2,5]
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder

        ''' boundaries '''
        # self._field_go(0,0)
        # self.mm.oscPitch()
        # time.sleep(15)
        # self.mm.oscYaw()
        # time.sleep(15)
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3      ,0.5-0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3      ,0.5+0.5*l3      ])
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2   ,0.5+0.5*l3+l2   ])
        # self._show()
        # self._cure(800)
        ''' boundaries '''
        def f1():
            self._showCureRect(-90,90,         [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f2(): self._showCureRect(0,0,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=20)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,  [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f4(): self._showCureRect(0,180,   [0.5-0.5*w,0.5+0.5*l3,      w,l2],oscAzimuth=False,oscPolar=True,waitTime_s=20)
        def f5():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_cylinder_a(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.75 * p
        l2 = 0.23 * p
        curingOrder = [1,2]
        ''' 1   1   1   1   2  '''  # pieceId
        ''' l1              l2 '''  # length
        ''' R   R   R   R   L  '''  # magnetization
        ''' 1   1   1   1   2  '''  # curingOrder
        ''' boundaries '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*(l1+l2),0.5-0.5*(l1+l2)])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*(l1+l2)-l2,0.5+0.5*(l1+l2)-l2])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*(l1+l2),0.5+0.5*(l1+l2)])
        self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*(l1+l2),0.5+0.5*(l1+l2)])
        self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*(l1+l2),0.5+0.5*(l1+l2)])
        self._show()
        self._cure(800)
        ''' boundaries '''
        def f1(): self._showCureRect(180,90,[0.5-0.5*w,0.5-0.5*(l1+l2),w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f2():
            self._field_go(180,15)
            time.sleep(10)
            self._showCureRect(0,90,[0.5-0.5*w,0.5+0.5*(l1+l2)-l2,   w,l2],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_flagella(self):
        # baseket w,l,h = 0.12 0.7 0.9
        p = 0.45  #0.5
        w = 0.16 * p #0.12
        wLeg = 0.13 * p
        l = 0.35 * p #.7
        h = 0.9 * p # pointing down
        g = (h - 4 * wLeg) / 3 # gap between horz pieces
        curingOrder = [5,2,3,1,4]

        ''' boundaries '''
        # self._field_go(0,0)
        # self.mm.oscPitch()
        # time.sleep(15)
        # self.mm.oscYaw()
        # time.sleep(15)
        # self.line.append([0.5-1.5*g-2*w,0.5-,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1]) # left long vert piece
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1]) # right long hotz 1
        # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 2
        # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 3
        # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ]) # right long hotz 4
        # self._show()
        # self._cure(800)
        ''' boundaries '''

        # ''' test print '''
        # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2,   h,w])
        # self.rect.append([0.5+1.5*g+w,   0.5-(l+w)/2+w, w,l])
        # self.rect.append([0.5+0.5*g,     0.5-(l+w)/2+w, w,l])
        # self.rect.append([0.5-0.5*g-w,   0.5-(l+w)/2+w, w,l])
        # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+w, w,l])
        # self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
        # self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
        # self._show()
        # ''' test print '''

        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
            self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
            self._showCureRect(90,90,   [0.5-1.5*g-2*wLeg, 0.5-(l+w)/2+w,   h,w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():
            self._showCureRect(0,180,   [0.5+1.5*g+wLeg,   0.5-(l+w)/2+w, wLeg,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        def f3():
            self._showCureRect(0,0,     [0.5+0.5*g,     0.5-(l+w)/2+w, wLeg,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
        def f4():
            self._showCureRect(0,180,  [0.5-0.5*g-wLeg,   0.5-(l+w)/2+w, wLeg,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
        def f5():
            self._showCureRect(0,0,   [0.5-1.5*g-2*wLeg, 0.5-(l+w)/2+w, wLeg,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    # def _macro_flagella(self):
    #     # baseket w,l,h = 0.12 0.7 0.9
    #     p = 0.45  #0.5
    #     w = 0.11 * p #0.12
    #     wForward = 0.05 * p
    #     wLeg = 0.13 * p
    #     l = 0.35 * p #.7
    #     h = 0.9 * p # pointing down
    #     g = (h - 4 * wLeg) / 3 # gap between horz pieces
    #     curingOrder = [5,2,3,1,4,6]
    #
    #     ''' boundaries '''
    #     # self._field_go(0,0)
    #     # self.mm.oscPitch()
    #     # time.sleep(15)
    #     # self.mm.oscYaw()
    #     # time.sleep(15)
    #     # self.line.append([0.5-1.5*g-2*w,0.5-,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1]) # left long vert piece
    #     # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1]) # right long hotz 1
    #     # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 2
    #     # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 3
    #     # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ]) # right long hotz 4
    #     # self._cure(800)
    #     ''' boundaries '''
    #
    #     # ''' test print '''
    #     # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2,   h,w])
    #     # self.rect.append([0.5+1.5*g+w,   0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5+0.5*g,     0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5-0.5*g-w,   0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+w, w,l])
    #     # self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #     # self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #     # self._show()
    #     # ''' test print '''
    #
    #     def f1():
    #         self._field_go(90,15)
    #         time.sleep(10)
    #         self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #         self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #         self._showCureRect(90,90,   [0.5-1.5*g-2*wLeg, 0.5-(l+w)/2+wForward,   h,w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
    #     def f2():
    #         self._showCureRect(0,180,   [0.5+1.5*g+wLeg,   0.5-(l+w)/2+w+wForward, wLeg,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
    #     def f3():
    #         self._showCureRect(0,0,     [0.5+0.5*g,     0.5-(l+w)/2+w+wForward, wLeg,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
    #     def f4():
    #         self._showCureRect(0,180,  [0.5-0.5*g-wLeg,   0.5-(l+w)/2+w+wForward, wLeg,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
    #     def f5():
    #         self._showCureRect(0,0,   [0.5-1.5*g-2*wLeg, 0.5-(l+w)/2+w+wForward, wLeg,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
    #     def f6():
    #         self._field_go(180,15)
    #         time.sleep(10)
    #         self._showCureRect(180,90,   [0.5-1.5*g-2*wLeg, 0.5-(l+w)/2,   h,wForward],oscAzimuth=True,oscPolar=False,waitTime_s=5)
    #     for i in range(len(curingOrder)):
    #         pieceId = curingOrder.index(i+1)
    #         function = 'f' + str(pieceId+1) + '()'
    #         eval(function)

    # def _macro_flagella(self):
    #     p = 0.85
    #     w = 0.16 * p
    #     l = 0.7 * p
    #     h = 0.9 * p
    #     g = (h - 4 * w) / 3 # gap between horz pieces
    #     curingOrder = [3,4,1,5,2]
    #
    #     # ''' boundaries '''
    #     # self._field_go(0,0)
    #     # self.mm.oscPitch()
    #     # time.sleep(15)
    #     # self.mm.oscYaw()
    #     # time.sleep(15)
    #     # self.line.append([0.5-1.5*g-2*w,0.5-,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1]) # left long vert piece
    #     # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1]) # right long hotz 1
    #     # self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 2
    #     # self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1]) # right long hotz 3
    #     # self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ]) # right long hotz 4
    #     # self._cure(800)
    #     # ''' boundaries '''
    #
    #     # ''' test print '''
    #     # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2,   h,w])
    #     # self.rect.append([0.5+1.5*g+w,   0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5+0.5*g,     0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5-0.5*g-w,   0.5-(l+w)/2+w, w,l])
    #     # self.rect.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+w, w,l])
    #     # self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #     # self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #     # self._show()
    #     # ''' test print '''
    #
    #     def f1():
    #         self._field_go(90,175)
    #         time.sleep(10)
    #         self.ring.append([0.5-1.5*g-2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #         self.ring.append([0.5+1.5*g+2*w, 0.5-(l+w)/2+0.5*w,w/2,w/2*0.7])
    #         self._showCureRect(90,90,   [0.5-1.5*g-2*w, 0.5-(l+w)/2,   h,w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
    #     def f2():
    #         self._showCureRect(90,90,   [0.5+1.5*g+w,   0.5-(l+w)/2+w, w,l],oscAzimuth=False,oscPolar=False,waitTime_s=0)
    #     def f3():
    #         self._showCureRect(0,0,     [0.5+0.5*g,     0.5-(l+w)/2+w, w,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
    #     def f4():
    #         self._field_go(90,15)
    #         time.sleep(10)
    #         self._showCureRect(-90,90,  [0.5-0.5*g-w,   0.5-(l+w)/2+w, w,l],oscAzimuth=True,oscPolar=False,waitTime_s=10)
    #     def f5():
    #         self._showCureRect(0,180,   [0.5-1.5*g-2*w, 0.5-(l+w)/2+w, w,l],oscAzimuth=True,oscPolar=True,waitTime_s=20)
    #     for i in range(len(curingOrder)):
    #         pieceId = curingOrder.index(i+1)
    #         function = 'f' + str(pieceId+1) + '()'
    #         eval(function)
    def _macro_pandemo(self):
        p = 1
        h = 0.2 * p
        w = 0.2 * p
        curingOrder = [1,2]

        def f1():
            self._showCureRect(270,90,[0.5-w,0.5-h/2,w,h],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        def f2():
            self._showCureRect(90,90,[0.5,0.5-h/2,w,h],oscAzimuth=True,oscPolar=False,waitTime_s=20)

        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)


    def _macro_crawler(self):
        p = 0.6
        r = 0.5 * p
        w = 0.3 * p

        ''' boundary '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.ring.append([0.5,0.5,r,0,0,180])
        self.ring.append([0.5,0.5,r-w,0,0,180])
        self.ring.append([0.5,0.5,r,0,180,360])
        self.ring.append([0.5,0.5,r-w,0,180,360])
        self.line.append([0.5-r,0.5-r+w,0.5,0.5])
        self.line.append([0.5+r-w,0.5+r,0.5,0.5])
        ''' boundary '''
        self._showCureRing(90,90,[0.5,0.5,r,w,0,180],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        self._showCureRing(-90,90,[0.5,0.5,r,w,180,360],oscAzimuth=True,oscPolar=False,waitTime_s=10)

    def _macro_doghnut(self):
        p = 0.6
        r = 0.5 * p
        w = 0.25 * p

        ''' boundary '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.ring.append([0.5,0.5,r,0,0,180])
        self.ring.append([0.5,0.5,r-w,0,0,180])
        self.ring.append([0.5,0.5,r,0,180,360])
        self.ring.append([0.5,0.5,r-w,0,180,360])
        self.line.append([0.5-r,0.5-r+w,0.5,0.5])
        self.line.append([0.5+r-w,0.5+r,0.5,0.5])
        self.line.append([0.5,0.5,0.5-r,0.5-r+w])
        self.line.append([0.5,0.5,0.5+r-w,0.5+r])
        self._show()
        self._cure()
        ''' boundary '''
        self._showCureRing(-135,90,[0.5,0.5,r,w,90,180],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        self._showCureRing(135,90,[0.5,0.5,r,w,0,90],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        self._showCureRing(45,90,[0.5,0.5,r,w,270,360],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        self._showCureRing(-45,90,[0.5,0.5,r,w,180,270],oscAzimuth=True,oscPolar=False,waitTime_s=10)

    def _macro_standingman(self):
        p = 0.8
        w = 0.2 * p
        l = 0.35 * p
        curingOrder = [2,3,1,4,5]
        # pieceId (top to down, left to right)
        ''' 1    2    3    4    5     ''' # pieceId
        ''' 2    3    1    5    4  '''  # curingOrder

        ''' boundaries '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.line.append([0.5-0.5*w-l,0.5+0.5*w+l,0.5-0.5*w,0.5-0.5*w])
        self.line.append([0.5-0.5*w-l,0.5+0.5*w+l,0.5+0.5*w,0.5+0.5*w])
        self.line.append([0.5+0.5*w+l,0.5+0.5*w+l,0.5-0.5*w,0.5+0.5*w])
        self.line.append([0.5-0.5*w-l,0.5-0.5*w-l,0.5-0.5*w,0.5+0.5*w])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*w-l,0.5-0.5*w-l])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*w+l,0.5+0.5*w+l])
        self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*w-l,0.5+0.5*w+l])
        self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*w-l,0.5+0.5*w+l])
        self._show()
        self._cure(800)
        ''' boundaries '''
        def f1():
            self._field_go(180,15)
            time.sleep(10)
            self._showCureRect(180,90, [0.5+0.5*w,0.5-0.5*w,l,w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f2():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90, [0.5-0.5*w,0.5-0.5*w-l,w,l],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f3(): self._showCureRect(0,0,    [0.5-0.5*w,0.5-0.5*w,w,w],oscAzimuth=False,oscPolar=True,waitTime_s=120)
        def f4():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,  [0.5-0.5*w,0.5+0.5*w,w,l],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        def f5():
            self._field_go(0,15)
            time.sleep(10)
            self._showCureRect(0,90,   [0.5-0.5*w-l,0.5-0.5*w,l,w],oscAzimuth=True,oscPolar=False,waitTime_s=5)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    def _macro_opticalstage(self):
        p = 0.5
        l1 = 0.16 * p
        l2 = 0.1 * p
        l3 = 0.1 * p
        a_mid = 0.1
        a_out = 0.9
        w_out = 0.2
        self._showCureRect(0,0,[0,0,0,0],oscAzimuth=True,oscPolar=True,waitTime_s=60)
        def addSpring(x,y,theta):
            p = [
                [x,y+l3+l1],[x,y+l3],
                [x-l2,y+l3],[x-l2,y],
                [x+l2,y],   [x+l2,y-l3],
                [x,y-l3],   [x,y-l3-l1]
                ]
            p = [mathfx.rotatePoint(origin=[x,y],point=i,angle=theta) for i in p]
            for i in range(7):
                self.line.append([p[i+1][1],p[i][1],p[i+1][0],p[i][0],3])
        addSpring(0.5,0.5*(1-0.5*a_mid-0.5*a_out+w_out),0)
        addSpring(0.5*(1+0.5*a_mid+0.5*a_out-w_out),0.5,90)
        addSpring(0.5,0.5*(1+0.5*a_mid+0.5*a_out-w_out),180)
        addSpring(0.5*(1-0.5*a_mid-0.5*a_out+w_out),0.5,270)
        self.rect.append([0.5-0.5*a_out,0.5-0.5*a_out,w_out,a_out])
        self.rect.append([0.5-0.5*a_out,0.5+0.5*a_out-w_out,a_out,w_out])
        self.rect.append([0.5+0.5*a_out-w_out,0.5-0.5*a_out,w_out,a_out])
        self.rect.append([0.5-0.5*a_out,0.5-0.5*a_out,a_out,w_out])
        xArray = [0.5-0.5*a_mid,0.5+0.5*a_mid,0.5+0.5*a_mid,0.5-0.5*a_mid]
        yArray = [0.5-0.5*a_mid,0.5-0.5*a_mid,0.5+0.5*a_mid,0.5+0.5*a_mid]
        xNewArray, yNewArray = mathfx.rotatePointArray((0.5,0.5),xArray,yArray,45)
        self._polygon_append(yNewArray + xNewArray)
        self._show()
        self._cure()

    def _macro_waves(self):
        p = 0.85
        w = 0.48 * p
        l1 = 0.1 * p
        l2 = 0.3 * p
        l3 = 0.2 * p
        curingOrder = [2,4,1,3,5]
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   L   U   R   L  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder

        ''' boundaries '''
        self._field_go(0,0)
        self.mm.oscPitch()
        time.sleep(15)
        self.mm.oscYaw()
        time.sleep(15)
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5-0.5*l3-l2-l1])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2+l1,0.5+0.5*l3+l2+l1])
        self.line.append([0.5-0.5*w,0.5-0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        self.line.append([0.5+0.5*w,0.5+0.5*w,0.5-0.5*l3-l2-l1,0.5+0.5*l3+l2+l1])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3-l2   ,0.5-0.5*l3-l2   ])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5-0.5*l3      ,0.5-0.5*l3      ])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3      ,0.5+0.5*l3      ])
        self.line.append([0.5-0.5*w,0.5+0.5*w,0.5+0.5*l3+l2   ,0.5+0.5*l3+l2   ])
        self._show()
        self._cure(800)
        ''' boundaries '''
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self._showCureRect(90,90,  [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f2():
            self._field_go(-90,15)
            time.sleep(10)
            self._showCureRect(-90,90,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],oscAzimuth=True,oscPolar=False,waitTime_s=10)
        def f3(): self._showCureRect(0,0,    [0.5-0.5*w,0.5-0.5*l3,      w,l3],oscAzimuth=False,oscPolar=True,waitTime_s=60)
        def f4(): self._showCureRect(90,90,  [0.5-0.5*w,0.5+0.5*l3,      w,l2],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        def f5(): self._showCureRect(-90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],oscAzimuth=True,oscPolar=False,waitTime_s=0)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_fingers(self):
        p = 0.85
        bh = 0.3 * p
        bv = 0.3 * p
        w = 0.15 * p
        l1 = 0.08 * p #opposite
        l2 = 0.27 * p
        curingOrder = [1,2]

        def f1():
            self.rect.append([0.5-0.5*(bv+l1),0.5-0.5*bh,bv,bh]) #base
            self._showCureRect(0,0,  [0.5-0.5*(bv+l1)+bv,0.5-0.5*w,l2,w],oscAzimuth=False,oscPolar=True,waitTime_s=20)
        def f2():
            self._showCureRect(0,180,  [0.5-0.5*(bv+l1)+bv+l2,0.5-0.5*w,l1,w],oscAzimuth=False,oscPolar=True,waitTime_s=20)
        for i in range(len(curingOrder)):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)

    def _macro_batch_swimmer(self):

        p = 0.2
        w = 0.25 * p
        l1_1 = 0.23 * p
        l2_1 = 0.13 * p
        l3_1 = 0.23 * p
        l1_2 = 0.19 * p
        l2_2 = 0.19 * p
        l3_2 = 0.19 * p
        l1_3 = 0.13 * p
        l2_3 = 0.23 * p
        l3_3 = 0.23 * p

        curingOrder = [4,1,3,2,5]
        # batch param
        lengthX = w # length X of one feature
        lengthY = l1_1+l2_1+l3_1+l2_1+l1_1 # length Y of one feature
        dx = lengthX * 1.25 # gap X between features
        dy = lengthX *1.25 # gap Y between features
        ''' 1   2   3   4   5  '''  # pieceId
        ''' l1  l2  l3  l2  l1 '''  # length
        ''' R   U   L   D   R  '''  # magnetization
        ''' 4   1   3   2   5  '''  # curingOrder
        def f1():
            self._field_go(90,15)
            time.sleep(10)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_1-l2_1-l1_1,w,l1_1],lengthY,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_2-l2_2-l1_2,w,l1_2],0,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_3-l2_3-l1_3,w,l1_3],-lengthY,dy,lengthY)
            self._showCureRect(90,90,[0,0,0.00001,0.00001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        def f2():
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_1-l2_1,w,l2_1],lengthY,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_2-l2_2,w,l2_2],0,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_3-l2_3,w,l2_3],-lengthY,dy,lengthY)
            self._showCureRect(0,0,[0,0,0.00001,0.00001],oscAzimuth=True,oscPolar=False,waitTime_s=60)
        def f3():
            self._field_go(-90,15)
            time.sleep(10)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_1,w,l3_1],lengthY,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_2,w,l3_2],0,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5-0.5*l3_3,w,l3_3],-lengthY,dy,lengthY)
            self._showCureRect(-90,90,  [0,0,0.00001,0.00001],oscAzimuth=True,oscPolar=False,waitTime_s=20)
        def f4():
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_1,w,l2_1],lengthY,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_2,w,l2_2],0,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_3,w,l2_3],-lengthY,dy,lengthY)
            self._showCureRect(0,180,   [0,0,0.00001,0.00001],oscAzimuth=False,oscPolar=True,waitTime_s=60)
        def f5():
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_1+l2_1,w,l1_1],lengthY,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_2+l2_2,w,l1_2],0,dy,lengthY)
            self._batch_rect_append2([0.5-0.5*w,0.5+0.5*l3_3+l2_3,w,l1_3],-lengthY,dy,lengthY)
            self._showCureRect(90,90,   [0,0,0.00001,0.00001],oscAzimuth=False,oscPolar=False,waitTime_s=0)
        for i in range(5):
            pieceId = curingOrder.index(i+1)
            function = 'f' + str(pieceId+1) + '()'
            eval(function)
        self._field_go(0,90)

    # def _macro_batch_swimmer(self):
    #     p = 0.25
    #     w = 0.30 * p
    #     l1 = 0.125 * p
    #     l2 = 0.23 * p
    #     l3 = 0.23 * p
    #     curingOrder = [4,1,3,2,5]
    #     # batch param
    #     lengthX = w # length X of one feature
    #     lengthY = l1+l2+l3+l2+l1 # length Y of one feature
    #     dx = lengthX * 1.25 # gap X between features
    #     dy = lengthX  # gap Y between features
    #     ''' 1   2   3   4   5  '''  # pieceId
    #     ''' l1  l2  l3  l2  l1 '''  # length
    #     ''' R   U   L   D   R  '''  # magnetization
    #     ''' 4   1   3   2   5  '''  # curingOrder
    #
    #     def f1():
    #         self._field_go(90,15)
    #         time.sleep(10)
    #         self._showCureRectBatch(90,90,         [0.5-0.5*w,0.5-0.5*l3-l2-l1,w,l1],dx,dy,lengthX,lengthY,oscAzimuth=True,oscPolar=False,waitTime_s=20)
    #     def f2(): self._showCureRectBatch(0,0,     [0.5-0.5*w,0.5-0.5*l3-l2,   w,l2],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=True,waitTime_s=60)
    #     def f3():
    #         self._field_go(-90,15)
    #         time.sleep(10)
    #         self._showCureRectBatch(-90,90,  [0.5-0.5*w,0.5-0.5*l3,      w,l3],dx,dy,lengthX,lengthY,oscAzimuth=True,oscPolar=False,waitTime_s=20)
    #     def f4(): self._showCureRectBatch(0,180,   [0.5-0.5*w,0.5+0.5*l3,      w,l2],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=True,waitTime_s=60)
    #     def f5(): self._showCureRectBatch(90,90,   [0.5-0.5*w,0.5+0.5*l3+l2,   w,l1],dx,dy,lengthX,lengthY,oscAzimuth=False,oscPolar=False,waitTime_s=0)
    #     for i in range(5):
    #         pieceId = curingOrder.index(i+1)
    #         function = 'f' + str(pieceId+1) + '()'
    #         eval(function)
    #     self._field_go(0,90)

# ==============================================================================
# Internal use
# ==============================================================================
    def _field_go(self,phi,theta,waitSec=3):
        self.mm.magneticFieldGo(phi,theta)
        while self.client.isBusy:
            time.sleep(.5)
        time.sleep(waitSec)

    def _batch_rect_append(self,rectArray,dx,dy,lengthX,lengthY):
        numberHalfSideX = int(0.5*(1-lengthX)/(dx+lengthX))
        numberHalfSideY = int(0.5*(1-lengthY)/(dy+lengthY))
        for i in range(numberHalfSideX*2+1):
            for j in range(numberHalfSideY*2+1):
                newRect = [x + y for x, y in zip(rectArray, [(i-numberHalfSideX)*(dx+lengthX),(j-numberHalfSideY)*(dy+lengthY),0,0])]
                self.rect.append(newRect)

    def _batch_rect_append2(self,rectArray,x,dy,lengthY):
        numberHalfSideY = int(0.5*(1-lengthY)/(dy+lengthY))
        for i in range(numberHalfSideY*2+1):
            newRect = [x + y for x, y in zip(rectArray, [x,(i-numberHalfSideY)*(dy+lengthY),0,0])]
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

    def _showCureRing(self,phi,theta,ringArray,oscAzimuth=False,oscPolar=False,waitTime_s=0,exposureTime_ms=0):
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
        self.ring.append(ringArray)
        self._show()
        self._cure(exposureTime_ms)

    def _batch_line_append(self,lineArray,dx,dy,lengthX,lengthY):
        numberHalfSideX = int(0.5*(1-lengthX)/(dx+lengthX))
        numberHalfSideY = int(0.5*(1-lengthY)/(dy+lengthY))
        for i in range(numberHalfSideX*2+1):
            for j in range(numberHalfSideY*2+1):
                newLine = [x + y for x, y in zip(lineArray, [(i-numberHalfSideX)*(dx+lengthX),(i-numberHalfSideX)*(dx+lengthX),(j-numberHalfSideY)*(dy+lengthY),(j-numberHalfSideY)*(dy+lengthY)]) ]
                self.line.append(newLine)

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
        empty = self.line == [] and self.rect == [] and self.cir == [] and self.polygon == [] and self.ring == []
        if not empty:
            self.plot.clear()
            if self.line:
                [self.plot.addLine(*r) for r in self.line]
                self.line = []
            if self.rect:
                [self.plot.addRect(*r) for r in self.rect]
                self.rect = []
            if self.cir:
                [self.plot.addCir(*r) for r in self.cir]
                self.cir = []
            if self.ring:
                [self.plot.addRing(*r) for r in self.ring]
                self.ring = []
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
