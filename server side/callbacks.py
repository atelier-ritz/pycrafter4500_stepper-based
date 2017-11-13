from PyQt5 import uic
from PyQt5.QtCore import QFile, QRegExp, QTimer
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox

qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

class GUI(QMainWindow,Ui_MainWindow):
    def __init__(self,sensor):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)
        
        self.setupTimer()
        self.sensor = sensor

    def setupTimer(self):
        self.my_timer = QTimer()
        self.my_timer.timeout.connect(self.update)
        self.my_timer.start(300) # msec
        
    def update(self):
        s = self.sensor
        self.lbl_x.setNum(s.field[0])
        self.lbl_y.setNum(s.field[1])
        self.lbl_z.setNum(s.field[2])
        self.lbl_mag.setNum(s.mag)
        self.lbl_phi.setNum(s.phi)
        self.lbl_theta.setNum(s.theta)
