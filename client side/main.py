import sys
from callbacks import GUI
from PyQt5 import QtWidgets
import warnings
warnings.filterwarnings("ignore")

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = GUI()
    window.show()
    sys.exit(app.exec_())
