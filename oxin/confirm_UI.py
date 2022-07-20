
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtGui import *
from pyparsing import col
from pyqt5_plugins import *
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPainter
import os
from . import login_api

from .backend import texts


ui, _ = loadUiType("oxin/confirm_window.ui")
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%


class UI_main_window(QMainWindow, ui):
    """
    this class initializes a confirm/message window for user. it has two buttons, yes or no, to accept or deny the operation will be done

    Inputs:
        ui: login UI object
        language: the main language for window and messages (in string)

    Outputs: None
    """
    
    global widgets
    widgets = ui


    def __init__(self, language='en'):

        super(UI_main_window, self).__init__()


        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # removing the window frame and attache it to top
        self.pos_ = self.pos()
        self._old_pos = None
        self.setWindowFlags(flags)
        # window title
        title = "SABA - Confrim message"
        self.setWindowTitle(title)

        # set default app language to as confirm window language
        self.language = language
        #
        # translate ui texts
        if self.language == 'fa':
            try:
                self.yes_btn.setText(texts.Titles['Yes'][self.language])
                self.no_btn.setText(texts.Titles['No'][self.language])
            
            except:
                pass
         

    # -----------------------------------------------------
    # functions for mouse click, relaese and move
    # def mousePressEvent(self, event):
    #     if event.button() == QtCore.Qt.LeftButton:
    #         self._old_pos = event.pos()

    # def mouseReleaseEvent(self, event):
    #     if event.button() == QtCore.Qt.LeftButton:
    #         self._old_pos = None

    # def mouseMoveEvent(self, event):
    #     if not self._old_pos:
    #         return
    #     delta = event.pos() - self._old_pos
    #     self.move(self.pos() + delta)


    def activate_(self):
        """
        this function connects the close button to its functionality

        Inputs: None

        :returns: None
        """

        self.close_btn.clicked.connect(self.close_win)



    def close_win(self):
        """
        this function is used for closing login window

        Inputs: None

        :returns: None
        """

        self.close()
        #sys.exit()



    def buttonClick(self):
        """
        this function is used to connect each button to its functionality, on button click

        Inputs: None

        :returns: None
        """

        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName =='toggleButton':
            self.toggleMenu(True)
 

    
if __name__ == "__main__":
    app = QApplication()
    win = UI_main_window()
    # apply_stylesheet(app,theme='dark_cyan.xml')
    api = login_api.API(win)
    win.show()
    sys.exit(app.exec())
    