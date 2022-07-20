# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file 'eror_window.ui'
#
# Created by: PyQt5 UI code generator 5.15.4
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


import sys


from PyQt5.QtGui import *
from PyQt5.QtGui import *
from PyQt5.QtGui import *
import cv2
from pyqt5_plugins import *
from PyQt5 import QtCore,QtGui

from PySide6.QtCore import *
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *

ui2, _ = loadUiType("oxin/eror_window.ui")


class UI_eror_window(QMainWindow, ui2):
    global widgets
    widgets_eror = ui2
    image_glob=0
    close_sign=0
    def __init__(self):
        super(UI_eror_window, self).__init__()
        self.setupUi(self)
        # Remove default frame
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        self.activate_()
        self.set_text()
        # self.show()
        self._old_pos = None

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
     #   sys.exit(app.exec())
    def set_text(self,msg='خطای سیستم',level=3):
        self.label.setText(msg)
        if level==1:
            print('awdwq')
            self.frame.setStyleSheet("background-color: green")

        if level==3:
            self.frame.setStyleSheet("background-color: red")
            # x=cv2.imread('images/alert.png')
            # self.label_2.setPixmap(QPixmap.fromImage('images/alert.png'))
            # pixmap =  QtGui.QPixmap('images/alert.png')
            # self.label_2.setPixmap(pixmap)
            # self.frame.setStyleSheet("background-color: Transparent")


        if level==2:
            self.frame.setStyleSheet("background-color: yellow")

            # x=cv2.imread('images/warning.png')
            # self.label_2.setPixmap(QPixmap.fromImage('images/warning.png'))
            # pixmap =  QtGui.QPixmap('images/warning.png')
            # self.label_2.setPixmap(pixmap)
            # self.frame_3.setStyleSheet("background-color: yellow;border-radius:15px")


    def activate_(self):
        self.close_btn.clicked.connect(self.close_win)
        self.close_btn_2.clicked.connect(self.close_win)
    def close_win(self):
        self.close_sign=1
        self.close()

if __name__ == "__main__":
    app = QApplication()
    win = UI_eror_window()
    win.show()
    sys.exit(app.exec())
