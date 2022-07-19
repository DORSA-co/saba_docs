
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
from PySide6 import QtCore as sQtCore
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
import copy
from qt_material import apply_stylesheet
ui, _ = loadUiType("notif_window.ui")

movey_max = 100
movex_time = 1
movey_time = 2
progressbar_time = 50
global notifs_list
notifs_list = []
def rearange_active_notifes():
    global notifs_list
    i = 0 
    for i in range(len(notifs_list)):
        if not notifs_list[i].is_active:
            
            for j in range(i+1, len(notifs_list)):
                
                notifs_list[j].win_move_down_run_timer(reverse=True)


class notification_manager():
    def __init__(self) :
        self.n_active_notifs = 0

    
    def create_new_notif(self, massage='', win_color=None, font_size=None, font_style=None, level=0):
        global notifs_list
        self.check_active_notifs()
        #
        notif_ui = UI_main_window(order=0)
        notif_ui.msg_label.setText(massage)
        #
        if win_color != None:
            notif_ui.background_frame.setStyleSheet('background-color:%s;' % (win_color)) # confirm window color
        if font_size != None and font_style != None:
            notif_ui.setStyleSheet('font: %spt "%s"' % (font_size, font_style)) # confirm window font-style and font-size

        # window icon
        if level == 0:
            icon = sQPixmap("images/tick.png")
        elif level == 1:
            icon = sQPixmap("images/alert2.png")
        if level == 2:
            icon = sQPixmap("images/error.png")
        
        try:
            notif_ui.icon_label.setPixmap(icon)
        except:
            pass
        #
        notifs_list.insert(0, notif_ui)
        self.n_active_notifs+=1
        notif_ui.show()


    def check_active_notifs(self):
        global notifs_list
        # pop the last one
        if len(notifs_list)>0 and not notifs_list[-1].is_active:
            notifs_list.pop()
        #
        for notif in notifs_list:
            notif.win_move_down_run_timer()
        #
        self.n_active_notifs = len(notifs_list)





os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%
class UI_main_window(QMainWindow, ui):
    global widgets
    widgets = ui

    def __init__(self, order=0):

        super(UI_main_window, self).__init__()


        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        #self.activate_()

        self.is_active = True
        self.close_btn_pressed = False
        self.order = order

        
        



        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Notification"

        self.setWindowTitle(title)

        
        # SET LANGUAGE
        #//////////////////////////////////////////////
        # self.set_language()
        self.language = 'en'

        self._old_pos = None

        self.win_startpoint()

        # win apear
        self.appearvalue = 0
        self.appeartimer = sQtCore.QTimer()
        self.appeartimer.timeout.connect(self.win_appear)
        self.appeartimer.start(movex_time)

        # win disapear
        self.disappeartimer = sQtCore.QTimer()
        self.disappeartimer.timeout.connect(self.win_disappear)


        # progressbar
        self.progressvalue = 0
        self.progresstimer = sQtCore.QTimer()
        self.progresstimer.timeout.connect(self.progressbar)
        self.progresstimer.start(progressbar_time)

        #sQtCore.QTimer.singleShot(2000, self.progressbar)

        # self.password.setEchoMode(QLineEdit.Password)
        #self.show_pass.clicked.connect(self.showPassword)

        self.close_btn.clicked.connect(self.buttonClick)
       

    def showPassword(self, show):
        echo=str(self.password.echoMode()).split(".", 4)[-1]

        if echo == 'Password':
            
            self.password.setEchoMode(QLineEdit.Normal)
            icon = QIcon()
            icon.addPixmap(QPixmap('images/show.png'))
            # icon.addPixmap(QPixmap('disabled.png'), QIcon.Disabled)
            # icon.addPixmap(QPixmap('clicking.png'), QIcon.Active)
            # icon.addPixmap(QPixmap('on.png'), QIcon.Normal, QIcon.On)
            self.show_pass.setIcon(icon)         
        
        else:
            self.password.setEchoMode(QLineEdit.Password)
            icon = QIcon()
            icon.addPixmap(QPixmap('images/hidden.png'))    
            self.show_pass.setIcon(icon)            

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
        self.close()
        #sys.exit()

    def close_win_2(self):
        self.progresstimer.stop()
        self.appeartimer.stop()
        self.disappeartimer.start(movex_time)



    def buttonClick(self):
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        if btnName =='close_btn':
            self.progresstimer.stop()
            self.appeartimer.stop()
            self.disappeartimer.start(movex_time)
            self.close_btn_pressed = True

    
 

    def get_user_pass(self):
        self.user_name_value=self.user_name.text()
        self.password_value=self.password.text()

        return self.user_name_value,self.password_value


    def set_login_message(self,text,color):
        self.login_message.setText(text)
        self.login_message.setStyleSheet("color:#{}".format(color))

    
    def progressbar(self):
        # setting for loop to set value of progress bar
        self.progressBar.setValue(self.progressvalue)
        self.progressvalue+=1
        if self.progressvalue >= 100:
            self.progresstimer.stop()
            self.disappeartimer.start(movex_time)


    def win_startpoint(self):
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(center_loc.x())
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())

        # qtRectangle = self.frameGeometry()
        # centerPoint = QDesktopWidget().availableGeometry().topLeft()
        # centerPoint.setX
        # qtRectangle.moveCenter(centerPoint)
        # self.move(qtRectangle.topLeft())
    

    def win_appear(self):
        self.appearvalue+=1
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(center_loc.x()-self.appearvalue)
        center_loc.setY(center_loc.y() + 20 + (self.order*movey_max))

        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())
        #
        if self.appearvalue >= 420:
            self.appeartimer.stop()
        #print('a:', frame_geo.x())
    

    def win_disappear(self):
        self.appearvalue-=1
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(center_loc.x()-self.appearvalue)
        center_loc.setY(center_loc.y() + 20 + (self.order*movey_max))
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())

        if self.appearvalue <= 0:
            self.disappeartimer.stop()
            self.is_active = False
            if self.close_btn_pressed:
                rearange_active_notifes()
            self.close_win()

    
    def win_move_down_run_timer(self, reverse=False):
        if not reverse:
            self.order+=1
        else:
            self.order-=1
            

        self.movedownvalue = 0
        self.movedowntimer = sQtCore.QTimer()
        if not reverse:
            self.movedowntimer.timeout.connect(self.win_move_down)
        else:
            self.movedowntimer.timeout.connect(self.win_move_top)

        self.movedowntimer.start(movey_time)
        
        
    def win_move_down(self):
        #print(self.movedownvalue, self.order*100)
        self.movedownvalue+=1
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(frame_geo.x())
        center_loc.setY(center_loc.y() + 20 + ((self.order-1)*movey_max+self.movedownvalue))
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())
        #
        if self.movedownvalue >= movey_max:
            self.movedowntimer.stop()
    

    def win_move_top(self):
        #print(self.movedownvalue, self.order, self.order*100)
        self.movedownvalue+=1
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(frame_geo.x())
        center_loc.setY(center_loc.y() + 20 + ((self.order+1)*movey_max-self.movedownvalue))
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())
        #
        if self.movedownvalue >= movey_max:
            self.movedowntimer.stop()
    
    
if __name__ == "__main__":
    app = QApplication()
    # win = UI_main_window()
    # # apply_stylesheet(app,theme='dark_cyan.xml')
    # #api = login_api.API(win)
    # win.show()
    
    # notif_ui = UI_main_window(order=1)
    # notif_ui.msg_label.setText('Start removing old files')
    # notif_ui.show()

    # notif_ui2 = UI_main_window(order=0)
    # notif_ui2.msg_label.setText('Start')
    # notif_ui2.show()

    notif_manager = notification_manager()

    notif_manager.create_new_notif(massage='hi')
    notif_manager.create_new_notif(massage='hi2')
    # notif_manager.create_new_notif(massage='hi3')
    # notif_manager.create_new_notif(massage='hi4')

    
    sys.exit(app.exec())
