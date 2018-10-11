from Adafruit_MotorHAT_Motors import Adafruit_MotorHAT
from TLV493D import TLV493D
from motormanager import MotorManager
from server import Server
from callbacks import GUI
from PyQt5 import QtWidgets
import sys

mh = Adafruit_MotorHAT()
sensor = TLV493D()
mm = MotorManager(mh,sensor)
svr = Server(mm)
mm.svr = svr

if __name__ == "__main__":
    svr.start()
    app = QtWidgets.QApplication(sys.argv)
    window = GUI(sensor)
    window.show()
    sys.exit(app.exec_())
 
