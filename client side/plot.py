import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

class MyPlot(object):
    def __init__(self):
        plt.ion()
        self.fig, self.ax = plt.subplots(facecolor=(0,0,0))
        plt.subplots_adjust(left=0, bottom=0, right=1, top=1)
        self.ax.set_aspect('equal')
        plt.axis('off')
        self.fig.tight_layout()
        #plt.show()
        plt.pause(0.005)

    def clear(self):
        self.addRect(0,0,1,1,'black')

    def addRect(self,x,y,w,h,color='white'):
        self.ax.add_patch(patches.Rectangle((x, y),width=w,height=h,color=color))

    def show(self):
        plt.pause(0.005)