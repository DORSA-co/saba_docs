
import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from PyQt5.QtGui import *
import cv2
from pyqt5_plugins import *
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *
from PySide6 import QtCore as sQtCore
from PySide6.QtGui import QPixmap as sQPixmap 
from PyQt5.QtGui import QPainter
import os



ui, _ = loadUiType("notif_window.ui")
os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%


movey_max = 100 # this is the vertical movement value for notification windows in pixel
movex_time = 500 # time for window horizintal moving (show/hide), time for window apearing/disapearing
movey_time = 2 # time for window vertical moving
progressbar_time = 50 # window max apear/showing time
pos_offset = 30
y_offest = 10
# a list contatingin active notifications
global notifs_list
notifs_list = []


def rearange_active_notifes():
    """
    on every call of this function, all notifications in notification list are checked, and if a notifiacton is deactived (finished),
    the other actived notifications rearranged and moved to take right position

    Inputs: None

    Returns: None
    """
    
    global notifs_list
    i = 0 
    for i in range(len(notifs_list)):
        if not notifs_list[i].is_active:
            
            for j in range(i+1, len(notifs_list)):
                
                notifs_list[j].win_move_down_run_timer(reverse=True)



class notification_manager():
    """
    this class is used to create and handle pop-up notifications of the app, it has functions to create new notification,
    and manage actived notificaions

    Inputs: None

    Returns: None
    """
    
    def __init__(self) :
        self.n_active_notifs = 0

    
    def create_new_notif(self, massage='', win_color=None, font_size=None, font_style=None, level=0):
        """
        this function is used to create a new pop-up notification, by taking as input the notification message and some other params

        Inputs:
            message: the notification message (in string)
            win_color: color of the window (same as the main app default color)
            font_size: font size of the messsage (same as the main app default)
            font_style: font style of the messsage (same as the main app default)
            level: the level of the message, in range of [0, 2], determinnig statues and importance of the message:
                0: good statues, only notification
                1: warning message
                2: error message
        
        Returens: None
        """

        
        
        global notifs_list

        # check, manage and rearange the previous notifications
        self.check_active_notifs()

        # create new notification window with order of zero
        notif_ui = UI_main_window(order=0)
        notif_ui.msg_label.setText(massage) # assign message to notif

        # assign appearanve parameters to window
        if win_color != None:
            notif_ui.background_frame.setStyleSheet('background-color: %s;' % (win_color)) # confirm window color
        if font_size != None and font_style != None:
            notif_ui.setStyleSheet('font: %spt %s;' % (font_size, font_style)) # confirm window font-style and font-size

        # window icon, assign window icon according to the level of message
        if level == 0:
            icon = sQPixmap("images/tick.png")
        #
        elif level == 1:
            icon = sQPixmap("images/alert2.png")
        #
        if level == 2:
            icon = sQPixmap("images/error.png")
        
        try:
            notif_ui.icon_label.setPixmap(icon)

        except:
            pass

        # add new notification to notifications list
        notifs_list.insert(0, notif_ui) # add to top
        self.n_active_notifs+=1 # update number of active notifs
        notif_ui.show() # start showing the window


    def check_active_notifs(self):
        """
        on every notification creation, this function is called to check the states of previous notifications, and if the last notification is
        deactived/finished, it most be removed from the actived notifications list

        Input: None

        Returns: None
        """
        
        global notifs_list
        # pop the last notification if its deactived
        if len(notifs_list)>0 and not notifs_list[-1].is_active:
            del notifs_list[-1]

        # rearange other notifications to move to right place
        for notif in notifs_list:
            notif.win_move_down_run_timer()

        # update number of actived notifications
        self.n_active_notifs = len(notifs_list)




class UI_main_window(QMainWindow, ui):
    """
    this class is used to create a new notification window object

    Inputs:
        order: order of the window (for arranging the notifications and determining their order)

    Returns: None
    """
    
    global widgets
    widgets = ui

    def __init__(self, order=0):

        super(UI_main_window, self).__init__()


        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint | Qt.WindowStaysOnTopHint) # removing the window frame and attache it to top
        self.pos_ = self.pos()
        self._old_pos = None
        self.setWindowFlags(flags)
        # APP NAME
        # ///////////////////////////////////////////////////////////////
        title = "Notification"
        self.setWindowTitle(title)

        #self.activate_()

        self.is_active = True # a flag for determingig if the window is actived or finished/closed
        self.close_btn_pressed = False # a flag for determinig if the window is closed by its close button
        self.order = order # the notification order

        # language of the window (same as the main app langage)
        self.language = 'en'

        # determine the startpoint of the window when it startes/created
        self.win_startpoint()

        # -----------------------------------------------------------------------------------
        # window apear, the window is started from top right of the screen and slides/moved left to appear, a timer is used to do this animation effet by in a defined time
        self.appearvalue = 0 # position value of the window in horizntal (x), from start point

        # -----------------------------------------------------------------------------------
        # window disapear, after finishing the alive time of notif/closing the notification, the window is slides/moved right to disappear,
        # a timer is used to do this animation effet by in a defined time


        # -----------------------------------------------------------------------------------
        # window alive-time, a progressbar on notification window is started at window creaton, and updated by the timer, until the progressbar
        # is completed (alive time of the window is finished)
        # progressbar
        self.progressvalue = 0 # progressbar value
        self.progresstimer = sQtCore.QTimer() # timer
        self.progresstimer.timeout.connect(self.progressbar) # connect timer to its function

        # connect close button to its function
        self.close_btn.clicked.connect(self.buttonClick)

        self.win_appear()

        self.move_flag = False
       

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

        Returns: None
        """

        self.close_btn.clicked.connect(self.close_win)



    def close_win(self):
        """
        this function is used for closing login window

        Inputs: None

        Returns: None
        """

        self.close()
        #sys.exit()


    def close_win_2(self):
        """
        this function is used for closing login window, also stoping progressbar and apear timers and start disapear timers

        Inputs: None

        Returns: None
        """

        self.progresstimer.stop()
        self.appeartimer.stop()
        self.disappeartimer.start(movex_time)


    def buttonClick(self):
        """
        this function is used to connect ui buttons to their functions

        Inputs: None

        Returns: None
        """
        
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()

        # window closing
        if btnName =='close_btn':
            self.close_btn_pressed = True
            self.progresstimer.stop()

            self.is_active = False # change window flag to deactived
            # rearange other acitive notifications if the current window is closed by close button
            self.close_win()
            rearange_active_notifes()
    

    def progressbar(self):
        """
        this function us used to update the progressbar value, by a timer.
        progressbar determines the remained time to finish and close the notfication

        Inputs: None

        Outputs: None
        """
        
        # setting for loop to set value of progress bar
        self.progressBar.setValue(self.progressvalue) # update progressbar value on ui
        self.progressvalue+=1 # update progressbar value

        # stop progressbar tomer if notifacation alive-time has finished (progress bar completed by 100%), and start disapearing timer to 
        # disapear and close the notifacation
        if self.progressvalue >= 100:
            self.progresstimer.stop()
            self.win_disappear()


    def win_startpoint(self):
        """
        this function is used to detemine the startpoint of the notification window (showing from top right of the screen)

        Inputs: None

        Returns: None
        """
        
        frame_geo = self.frameGeometry()
        screen = self.window().screen()
        center_loc = screen.geometry().topRight()
        center_loc.setX(center_loc.x())
        frame_geo.moveCenter(center_loc)
        self.move(frame_geo.center())

        self.start_point = [frame_geo.center().x(), frame_geo.center().y() + pos_offset]

        # qtRectangle = self.frameGeometry()
        # centerPoint = QDesktopWidget().availableGeometry().topLeft()
        # centerPoint.setX
        # qtRectangle.moveCenter(centerPoint)
        # self.move(qtRectangle.topLeft())
    

    def update_current_position(self):
        frame_geo = self.frameGeometry()
        self.curront_point = [frame_geo.x(), frame_geo.y()]
        self.start_point[1] = frame_geo.y()


    def win_appear(self, use_current_pos=False):
        """
        this function is used to appear/show the notification window with an sliding animation,
        notification window will be appeared from top left of the screen in sliding way

        Inputs: None

        Returns: None
        """

        self.appear_animation = QPropertyAnimation(self, b'geometry')
        self.appear_animation.setDuration(movex_time)
        if not use_current_pos:
            self.appear_animation.setStartValue(QRect(self.start_point[0], self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.appear_animation.setEndValue(QRect(self.start_point[0]-self.frameGeometry().width()-pos_offset, self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
        else:
            print('h')
            self.appear_animation.setStartValue(QRect(self.start_point[0], self.curront_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.appear_animation.setEndValue(QRect(self.start_point[0]-self.frameGeometry().width()-pos_offset, self.curront_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
        
        self.appear_animation.setEasingCurve(QEasingCurve.InOutExpo) 
        self.appear_animation.finished.connect(self.progresstimer.start(progressbar_time)) # start progress timer
        self.appear_animation.finished.connect(self.win_move_down) # start progress timer
        self.appear_animation.start()
    

    def win_disappear(self, use_current_pos=False):
        """
        this function is used to disappear/hide the notification window with an sliding animation,
        notification window will be disappeared from top left of the screen in sliding way

        Inputs: None

        Returns: None
        """

        # update position
        self.update_current_position()

        self.disappear_animation = QPropertyAnimation(self, b'geometry')
        self.disappear_animation.setDuration(movex_time)
        if not use_current_pos:
            self.disappear_animation.setStartValue(QRect(self.start_point[0]-self.frameGeometry().width()-pos_offset, self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.disappear_animation.setEndValue(QRect(self.start_point[0], self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
        else:
            self.disappear_animation.setStartValue(QRect(self.curront_point[0], self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.disappear_animation.setEndValue(QRect(self.start_point[0], self.start_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
        
        self.disappear_animation.setEasingCurve(QEasingCurve.InOutExpo)
        self.disappear_animation.finished.connect(self.close_win)
        self.disappear_animation.start()
        
        self.is_active = False # change window flag to deactived
            
        # rearange other acitive notifications if the current window is closed by close button
        if self.close_btn_pressed:
            rearange_active_notifes()

    
    def win_move_down_run_timer(self, reverse=False):
        """
        this function is used to move notification verticaly, if a new notification is created or a previous notification is closed
        on defalt, it is used to move down the notifications, but it can be used to move up the notifications by the reverse flag

        Inputs:
            reverse: a boolean value deermining if the movement is reversly (move to top) 
        
        Returns: None
        """
        
        # update order of the notifacation, the order of notifs is increased from top to bottom of the scrren
        if not reverse:
            self.order+=1
            self.win_move_down()

        else:
            self.order-=1
            self.win_move_top()

        # self.movedownvalue = 0 # value determining the vertical position of window from startpoint
        # self.movedowntimer = sQtCore.QTimer() # timer to slide/move window vertically

        # if not reverse:
        #     self.movedowntimer.timeout.connect(self.win_move_down)
        # else:
        #     self.movedowntimer.timeout.connect(self.win_move_top)

        # self.movedowntimer.start(movey_time)
        
        
    def win_move_down(self):
        """
        this function is used to move the notification down vertically, on any new notification is created

        Inputs: None

        Returns: None
        """
        
        if self.order > 0 and not self.move_flag:

            self.move_flag = True

            # update position
            self.update_current_position()

            self.movedown_animation = QPropertyAnimation(self, b'geometry')
            self.movedown_animation.setDuration(movex_time)
            self.movedown_animation.setStartValue(QRect(self.curront_point[0], self.curront_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.movedown_animation.setEndValue(QRect(self.curront_point[0], self.curront_point[1]+self.frameGeometry().height()+y_offest, self.frameGeometry().width(), self.frameGeometry().height()))
            self.movedown_animation.setEasingCurve(QEasingCurve.InOutExpo)
            self.movedown_animation.finished.connect(self.unlock_move_flag)
            self.movedown_animation.finished.connect(self.check_appear_done)
            self.movedown_animation.start()

    
    
    def check_appear_done(self):
        self.update_current_position()
        if self.start_point[0] == self.curront_point[0]:
            self.win_appear(use_current_pos=True)


    def unlock_move_flag(self):
        self.move_flag = False
    

    def win_move_top(self):
        """
        this function is used to move the notification up vertically, if any top notification is closed

        Inputs: None

        Returns: None
        """

        if self.order >= 0 and not self.move_flag:

            if self.progressvalue >= 100:
                self.close_win()
                return

            self.move_flag = True

            # update position
            self.update_current_position()

            self.moveup_animation = QPropertyAnimation(self, b'geometry')
            self.moveup_animation.setDuration(movex_time)
            self.moveup_animation.setStartValue(QRect(self.curront_point[0], self.curront_point[1], self.frameGeometry().width(), self.frameGeometry().height()))
            self.moveup_animation.setEndValue(QRect(self.curront_point[0], self.curront_point[1]-self.frameGeometry().height()-y_offest, self.frameGeometry().width(), self.frameGeometry().height()))
            self.moveup_animation.setEasingCurve(QEasingCurve.InOutExpo)
            self.moveup_animation.finished.connect(self.unlock_move_flag)
            self.moveup_animation.start()
    

    
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

    itr = 0
    while itr < 10:
        notif_manager.create_new_notif(massage='hi', win_color='red', font_size=10, font_style='Arial')
        cv2.waitKey(1000)
        itr+=1

    #notif_manager.create_new_notif(massage='hi2', win_color='red', font_size=10, font_style='Arial')
    #notif_manager.create_new_notif(massage='hi3', win_color='red', font_size=10, font_style='Arial')
      

    #notif_manager.create_new_notif(massage='hi2')
    # notif_manager.create_new_notif(massage='hi3')
    # notif_manager.create_new_notif(massage='hi4')

    
    sys.exit(app.exec())
