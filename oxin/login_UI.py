
import sys
from PyQt5 import QtCore, QtGui, QtWidgets
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtGui import *
from pyparsing import col
from pyqt5_plugins import *
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *
from PySide6.QtGui import QImage as sQImage
from PySide6.QtGui import QPixmap as sQPixmap
from PyQt5.QtGui import QPainter
import numpy as np
import threading
import time
from PyQt5.QtGui import QPainter
import os
import login_api
import cv2
from qt_material import apply_stylesheet
ui, _ = loadUiType("login_setting.ui")


os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%
class UI_main_window(QMainWindow, ui):
    global widgets
    widgets = ui

    def __init__(self):

        super(UI_main_window, self).__init__()


        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        self.activate_()
        



        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "SABA - logim"

        self.setWindowTitle(title)

        
        # SET LANGUAGE
        #//////////////////////////////////////////////
        # self.set_language()
        self.language = 'en'

        self._old_pos = None

        # self.password.setEchoMode(QLineEdit.Password)
        self.show_pass.clicked.connect(self.showPassword)
       

    def showPassword(self, show):
        echo=str(self.password.echoMode()).split(".", 4)[-1]

        if echo == 'Password':
            self.password.setEchoMode(QLineEdit.Normal)
            # icon = QIcon()
            # icon.addPixmap(QPixmap('images/show.png'))
            # self.show_pass.setIcon(icon)
            self.show_pass.setIcon(sQPixmap.fromImage(sQImage('images/show.png')))
        
        else:
            self.password.setEchoMode(QLineEdit.Password)
            # icon = QIcon()
            # icon.addPixmap(QPixmap('images/hidden.png'))    
            # self.show_pass.setIcon(icon)
            self.show_pass.setIcon(sQPixmap.fromImage(sQImage('images/hidden.png')))      

        # self.password.setEchoMode(QLineEdit.Normal if show else QLineEdit.Password)

        

    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._old_pos = event.pos()

    def mouseReleaseEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self._old_pos = None

    def mouseMoveEvent(self, event):
        if not self._old_pos:
            return
        delta = event.pos() - self._old_pos
        self.move(self.pos() + delta)




    #///////////////////// LANGUAGE
    # def set_language(self):
    #     print(detect_lenguage.language())
    #     if detect_lenguage.language()=='Persian(فارسی)':
    #         detect_lenguage.main_window(self)
    
 
    # Label Dorsa
    # ///////////////////////////////////////////////     
    # def label_dorsa_open(self, enable):
    #     if enable:
    #         # GET WIDTH
    #         width = self.label_dorsa.width()
    #         maxExtend = 150
    #         standard = 0

    #         # SET MAX WIDTH
    #         if width == 0:
    #             #print('OPEN')
    #             # self.toggleButton.setStyleSheet("background-image: url(:/icons/images/icons/t2.png);")
    #             widthExtended = maxExtend
    #             #print(widthExtended)
    #         else:
    #             # self.toggleButton.setStyleSheet("background-image: url(:/icons/images/icons/t1.png);")
    #             #print('Close')
    #             widthExtended = standard
    #             #print(widthExtended)

    #         # ANIMATION
    #         self.animation = QPropertyAnimation(self.label_dorsa, b"minimumWidth")
    #         self.animation.setDuration(1200)
    #         self.animation.setStartValue(width)
    #         self.animation.setEndValue(widthExtended)
    #         self.animation.setEasingCurve(QEasingCurve.InOutQuart)
    #         self.animation.start()
 

 
    def activate_(self):
        self.close_btn.clicked.connect(self.close_win)



    def close_win(self):
        self.password.setText('')
        self.user_name.setText('')
        self.close()
        #sys.exit()



    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName =='toggleButton':
            self.toggleMenu(True)
 

    def get_user_pass(self):
        self.user_name_value=self.user_name.text()
        self.password_value=self.password.text()

        return self.user_name_value,self.password_value


    def set_login_message(self,text,color):
        self.login_message.setText(text)
        self.login_message.setStyleSheet("color:#{}".format(color))








if __name__ == "__main__":
    app = QApplication()
    win = UI_main_window()
    # apply_stylesheet(app,theme='dark_cyan.xml')
    api = login_api.API(win)
    win.show()
    sys.exit(app.exec())
    