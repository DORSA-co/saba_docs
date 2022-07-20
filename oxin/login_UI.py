
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
from PySide6.QtGui import QImage as sQImage
from PySide6.QtGui import QPixmap as sQPixmap
from PyQt5.QtGui import QPainter
from PyQt5.QtGui import QPainter
import os
import threading

from . import login_api
from .backend import texts, colors_pallete


ui, _ = loadUiType("oxin/login_setting.ui")
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%


class UI_main_window(QMainWindow, ui):
    """
    this class initializes a login window for user to login to app

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
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # remove the frame of the window, and make window stay on top
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        # app title
        title = "SABA - login"
        self.setWindowTitle(title)
        self._old_pos = None

        # close button connect
        self.activate_()
        
        # SET LANGUAGE of the app
        self.language = language

        # flag to dont run another thread until one is available
        self.show_mesagges_thread_lock = False

        # translate titles in the login window
        if self.language == 'fa':
            try:
                self.label.setText(texts.Titles['User Login'][self.language])
                self.user_name.setPlaceholderText(texts.Titles['Username'][self.language])
                self.password.setPlaceholderText(texts.Titles['Password'][self.language])
                self.login_btn.setText(texts.Titles['Login'][self.language])
            
            except:
                pass

        # connect pawword show/hide button to its function
        self.show_pass.clicked.connect(self.showPassword)
       

    def showPassword(self, show):
        """
        this functino is used for showing/hiding password text in password lineedit

        Inputs: None

        :returns: None
        """
        
        echo = str(self.password.echoMode()).split(".", 4)[-1]

        if echo == 'Password':
            self.password.setEchoMode(QLineEdit.Normal)
            # change eye icon
            self.show_pass.setIcon(sQPixmap.fromImage(sQImage('images/show.png')))
        
        # set password mode to password (hiding password text/showing boolets except text)
        else:
            self.password.setEchoMode(QLineEdit.Password)
            # change eye icon
            self.show_pass.setIcon(sQPixmap.fromImage(sQImage('images/hidden.png')))      


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
        this function is used for closing login window, also on closing, the password and username fileds are cleared

        Inputs: None

        :returns: None
        """
        
        self.password.setText('')
        self.user_name.setText('')
        self.close()
        #sys.exit()


    def buttonClick(self):
        """
        this function is used to connect each button to its functionality, on button click

        Inputs: None

        :returns: None
        """
        
        btn = self.sender()
        btnName = btn.objectName()

        if btnName =='toggleButton':
            self.toggleMenu(True)
 

    def get_user_pass(self):
        """
        this function is used to get/return entered username and password from fields

        Inputs: None

        :returns:
            username: in string
            password: in string
        """
        
        self.user_name_value=self.user_name.text()
        self.password_value=self.password.text()

        return self.user_name_value,self.password_value
    

    def set_login_message(self, text='', level=0, clearable=True, prefix=True):
        """
        this function is used to show input message in input label, also there is a message level determining the color of label, and a timer to clear meesage after a while

        Inputs:
            label_name: label element name to show the message in
            text: input message to show (in string)
            level: level of the message (in int), its a value betweem [0, 2] determining the bakground color of message label
            clearable: a boolean value determining whater to clear the message after timeout or not
            prefix: a boolean value determinign wheater to show the message prefix or not
        
        :returns: None
        """
        
        if text != '':
            if level == 0:
                self.login_message.setText(text)
                self.login_message.setStyleSheet('background-color: %s ; color: white;' % (colors_pallete.successfull_green))
            #
            if level == 1:
                if prefix:
                    self.login_message.setText(text)
                else:
                    self.login_message.setText(text)
                self.login_message.setStyleSheet('background-color: %s; color: white;' % (colors_pallete.warning_yellow))
            #
            if level >= 2:
                if prefix:
                    self.login_message.setText(text)
                else:
                    self.login_message.setText(text)
                self.login_message.setStyleSheet('background-color: %s; color: white;' % (colors_pallete.failed_red))

            #
            if clearable and not self.show_mesagges_thread_lock:
                self.show_mesagges_thread_lock = True
                # timer to clear the message
                self.thread = threading.Timer(2, self.set_login_message)
                self.thread.start()

        # clear the message after timeout
        else:
            self.login_message.setText('')
            self.login_message.setStyleSheet('')
            # unlock thread
            self.show_mesagges_thread_lock = False




if __name__ == "__main__":
    app = QApplication()
    win = UI_main_window()
    # apply_stylesheet(app,theme='dark_cyan.xml')
    api = login_api.API(win)
    win.show()
    sys.exit(app.exec())
    