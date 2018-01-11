import syntax
import math
import time
import re
import pycrafter4500
from textprocess import TextProcess
from client import Client
from motormanager import MotorManager
from PyQt5 import uic
from PyQt5.QtCore import QFile, QRegExp
from PyQt5.QtWidgets import QApplication, QFileDialog, QMainWindow, QMenu, QMessageBox
#=========================================================
# a class that handles the signal and callbacks of the GUI
#=========================================================
# UI config
qtCreatorFile = "mainwindow.ui"
Ui_MainWindow, QtBaseClass = uic.loadUiType(qtCreatorFile)

client = Client()
mm = MotorManager(client)
tp = TextProcess(client,mm)
#=========================================================
# a class that handles the signal and callbacks of the GUI
#=========================================================
class GUI(QMainWindow,Ui_MainWindow):
    def __init__(self):
        QMainWindow.__init__(self)
        Ui_MainWindow.__init__(self)
        self.setupUi(self)

        self.setupFileMenu()
        self.setupHelpMenu()
        self.setupCallbacksLED()
        self.setupMotors()
        self.setupCallbacksEditor()


    def setupCallbacksLED(self):
        self.btn_LED_set.clicked.connect(self.on_btn_LED_set)

    def setupMotors(self):
        self.btn_motor1_run.clicked.connect(self.on_btn_motor1_run)
        self.btn_motor2_run.clicked.connect(self.on_btn_motor2_run)
        self.btn_phi_theta_run.clicked.connect(self.on_btn_phi_theta_run)
        self.btn_phi_at_singularity.clicked.connect(self.on_btn_phi_at_singularity)
        self.btn_macro1.clicked.connect(self.on_btn_macro1)
    def setupCallbacksEditor(self):
        self.currentFilePath = ''
        self.btn_editor_update.clicked.connect(self.on_btn_editor_update)
        self.highlighter = syntax.Highlighter(self.editor.document())

    def about(self):
        QMessageBox.about(self, "About Pycrafter 4500",
                "<p>The <b>Pycrafter4500</b> is based on the DLPC350 USB API. " \
                "Please refer to <b>DLPC350 Programmer’s Guide</b> for a list of commands. " \
                "Many thanks to API Python wrapper <b>https://github.com/SivyerLab/pyCrafter4500</b>. " \
                "Tianqi</p>")

    def aboutFiles(self):
        QMessageBox.about(self, "About Files",
                "<p>"
                "<b>syntax</b> editor keyword highlighting <br>"
                "<b>Pixel</b> database class that handles pixel information <br>"
                "<b>callbacks</b> GUI class that handles callbacks <br>"
                "</p>")

    def newFile(self):
        self.editor.clear()
        self.currentFilePath = ''

    def openFile(self, path=None):
        if not path:
            path, _ = QFileDialog.getOpenFileName(self, "Open File", '',
                    "txt Files (*.txt)")
        if path:
            self.currentFilePath = path
            self.setWindowTitle(path)
            inFile = QFile(path)
            if inFile.open(QFile.ReadOnly | QFile.Text):
                text = inFile.readAll()
                text = str(text, encoding='ascii')
                self.editor.setPlainText(text)

    def saveFile(self):
        if self.currentFilePath == '':
            self.currentFilePath, _ = QFileDialog.getSaveFileName(self, "Save file", '',
                    "txt Files (*.txt)")
        path = self.currentFilePath
        saveFile = open(path, "w")
        text = str(self.editor.toPlainText())
        saveFile.write(text)
        saveFile.close()

    def setupFileMenu(self):
        fileMenu = QMenu("&File", self)
        self.menuBar().addMenu(fileMenu)
        fileMenu.addAction("&New Editor", self.newFile, "Ctrl+N")
        fileMenu.addAction("&Open Editor...", self.openFile, "Ctrl+O")
        fileMenu.addAction("&Save Editor", self.saveFile, "Ctrl+S")
        fileMenu.addAction("E&xit", QApplication.instance().quit, "Ctrl+Q")

    def setupHelpMenu(self):
        helpMenu = QMenu("&Help", self)
        self.menuBar().addMenu(helpMenu)
        helpMenu.addAction("&About", self.about)
        helpMenu.addAction("About &Files", self.aboutFiles)

    def on_btn_LED_set(self):
        time_ms = self.spb_LED_exposureTime.value()
        intensity = 0xFF - self.spb_LED_intensity.value()
        if time_ms == 0:
            pycrafter4500.set_LED_current(intensity)
        else:
            pycrafter4500.set_LED_current(intensity)
            time.sleep(time_ms/1000)
            pycrafter4500.set_LED_current(255)

    def on_btn_motor1_run(self):
        val = self.spb_motor1_step.value()
        mm.motorgo(0,val)

    def on_btn_motor2_run(self):
        val = self.spb_motor2_step.value()
        mm.motorgo(1,val)

    def on_btn_phi_run(self):
        val = self.spb_phi.value()
        mm.phiGo(val)

    def on_btn_theta_run(self):
        val = self.spb_theta.value()
        mm.thetaGo(val)
    def on_btn_phi_theta_run(self):
        phi = self.spb_phi.value()
        theta = self.spb_theta.value()
        mm.magneticFieldGo(phi,theta)
    def on_btn_phi_at_singularity(self):
        phi = self.spb_phi_at_singularity.value()
        mm.setPhiSingularity(phi)
    def on_btn_macro1(self):
        mm.macro1()
    def on_btn_editor_update(self):
        tp.clear()
        tp.set_exposureTime(self.spb_LED_exposureTime.value())
        tp.set_intensityUV(self.spb_LED_intensity.value())
        tp.process(self.editor.toPlainText().splitlines())
