import sys
from PyQt5 import QtCore
from PyQt5.QtWidgets import * 
from PyQt5.QtGui import * 
from pyqt5_plugins import *
from PyQt5.QtGui import QPainter
from PySide6.QtCharts import *
from PySide6.QtCore import *
from PySide6.QtUiTools import loadUiType
from PySide6.QtWidgets import *
from PySide6.QtGui import QImage as sQImage    # should change
from PySide6.QtGui import QPixmap as sQPixmap   # should change
from PySide6.QtWidgets import QMessageBox as sQMessageBox
from PySide6.QtGui import QIcon as sQIcon
import threading
import os
from functools import partial
import xml.etree.ElementTree as ET
import json

from .backend import camera_funcs, colors_pallete, logging_funcs, mainsetting_funcs, texts, user_management_funcs
from . import setting_api
from .app_settings import Settings
from . import translate_ui


# ui file pathes
ui_file_path_en = 'main_window.ui'
ui_file_path_fa = 'main_window_fa.ui'
# startup json file, containing some startup parameters for program
app_startup_json_path = 'start_up.json'

# translate ui to available languages, this will generate multiple ui files each for one language
try:
    translate_ui.translate_ui(language='fa', ui_file_path_en=ui_file_path_en, ui_file_path_fa=ui_file_path_fa)
except:
    pass


# load english (default) ui file if satartup json file doesnt exist
if not os.path.exists(app_startup_json_path):
    ui_file = ui_file_path_en

else:
    # try to load app language from startup json file
    try:
        with open(app_startup_json_path) as json_file:
            start_up_settings = json.load(json_file)
        json_file.close()

        # load persin ui file
        if start_up_settings['language'] == 'fa':
            ui_file = ui_file_path_fa
    
    except:
        # load defult english ui file
        ui_file = ui_file_path_en


# load ui file
try:
    ui, _ = loadUiType(ui_file)
except:
    ui, _ = loadUiType(ui_file_path_en)


os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%


# ui class
class UI_main_window(QMainWindow, ui):
    global widgets
    widgets = ui

    def __init__(self):
        super(UI_main_window, self).__init__()

        # window setup
        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint) # remove the windows frame of ui
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        # app title
        title = "SABA - Settings App"
        self.setWindowTitle(title)
        self._old_pos = None
        self.app_close_flag = False # flag to determine whetere app is running or closed
        
        # activating ui buttons
        self.activate_()

        
        # loading app startup json if exists
        try:
            self.start_up_settings = start_up_settings
        except:
            self.start_up_settings = {}

        
        # SET app LANGUAGE (this will be used for showing messages and pop-ups in the program)
        try:
            self.language = self.start_up_settings['language']
        except:
            self.language = 'en'


        # logger object to get log from everything is happening in the program
        self.logger = logging_funcs.app_logger(name='saba_setting-app_logger', log_mainfolderpath='./app_logs', console_log=True)
        self.logger.create_new_log(message='UI object for setting app created.')


        # flag parameters
        self.cam_num_old = 1 # ?
        self.camera_connect_flag = False # flag ot determine if there is a camera connected to app (for camera setting and calibration pages)
        self.calibration_image = None # camera image used for calibrating
        self.login_flag = False # flag to determine if a user is logged-in to program
        self.plc_connect = False # flag to determnine if program is connected to PLC
        self.show_mesagges_thread_lock = False # flag to dont run another thread until one is available
        

        # dashboard button ids, this list is used to enable or disable all buttons
        self.dash_buttons = [self.camera_setting_btn,self.calibration_setting_btn, self.plc_setting_btn\
                            , self.defect_setting_btn, self.users_setting_btn, #self.level2_setting_btn\
                            self.general_setting_btn, self.storage_setting_btn]

        # side-bar button ids, this list is used to enable or disable all buttons
        self.side_buttons = [self.side_camera_setting_btn, self.side_calibration_setting_btn, self.side_plc_setting_btn\
                            , self.side_defect_setting_btn, self.side_users_setting_btn, #self.side_level2_setting_btn\
                            self.side_general_setting_btn, self.side_storage_setting_btn, self.side_dashboard_btn]

        # camera variable parameters ids in the camera-settings section of the UI, this list is used to enable or disable all elements in ui
        self.camera_params = [self.gain_spinbox, self.expo_spinbox, self.width_spinbox\
                            , self.height_spinbox, self.offsetx_spinbox, self.offsety_spinbox\
                            ,self.trigger_combo, self.maxbuffer_spinbox, self.packetdelay_spinbox\
                                , self.packetsize_spinbox, self.transmissiondelay_spinbox, self.ip_lineedit, self.serial_number_combo, self.camera_setting_connect_btn]
        
        # PLC check buttons
        self.PLC_btns = ['check_thermometer_min_plc', 'check_thermometer_max_plc', 'check_cooler_uptime_plc',
                         'check_system_operating_plc', 'check_air_valve_plc', 'check_camera_limit_plc', 'check_camera_frate_plc', 'check_projector_limit_plc',
                         'check_detect_sensor_plc', 'check_limitswitch_top_plc', 'check_limitswitch_bottom_plc']


        # others
        self.main_login_btn.setIcon(sQPixmap.fromImage(sQImage('images/login_white.png'))) # main login button set icon
        #
        # set contents of combo boxes in the app
        self.set_combo_boxes() 

        # connect sliders in ui to their functions
        self.set_sliders()

        # connect checkboxes in ui to their functions
        self.set_checkboxes()

        #
        self.stackedWidget.currentChanged.connect(self.disable_camera_settings) # disable camera setting page emelents on stackwidjet change
        self.stackedWidget.setCurrentWidget(self.page_dashboard) # set stackwidjet to dashboard on program start

        #
        self.logger.create_new_log(message='UI object initialized and setting app loaded.')
        
        
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

    
    def close_win(self):
        """
        this function closes the app

        Inputs: None

        Returns: None
        """
        
        self.app_close_flag = True
        self.logger.create_new_log(message='Setting app closed.')

        # close app window and exit the program
        self.close()
        sys.exit()


    def close_app_force(self, message='An Error occured while runnung the app', change_language=False):
        """
        this function closes the app in force situations (app errors or excetions), also a log will be written determining the cause
        for closing the app, and an alert window will be appeared to warn the app closing

        Inputs:
            message: message to log on app close (in string)
            change_language: a boolean determines if the app close is for changing the app language
        
        Retuens: None
        """
        
        self.app_close_flag = True
        # log
        if not change_language:
            self.logger.create_new_log(message=texts.ERRORS['setting_app_closed_force']['en'], level=4)
        elif change_language:
            self.logger.create_new_log(message=texts.MESSEGES['app_close_change_language']['en'], level=1)
            
        # alert message
        alert_window = sQMessageBox(sQMessageBox.Warning, texts.WARNINGS['app_warning'][self.language], message)
        alert_window.setStandardButtons(sQMessageBox.Ok)
        icon = sQIcon()
        icon.addPixmap(sQPixmap("images/alert.png"), sQIcon.Normal)
        alert_window.setWindowIcon(icon)
        alert_window.exec()

        # close app window and exit the program
        self.close()
        sys.exit()


    # def closeEvent(self, event):
    #     if self.camera_connect_flag:
    #         alert_window = sQMessageBox(sQMessageBox.Warning, 'Alert', 'Please disconnect camera(s) before exit')
    #         alert_window.setStandardButtons(sQMessageBox.Ok)
    #         icon = sQIcon()
    #         icon.addPixmap(sQPixmap("icons/alert.png"), sQIcon.Normal)
    #         alert_window.setWindowIcon(icon)
    #         alert_window.exec()
    #         event.ignore()
    #     else:
    #         event.accept()



    def minimize_win(self):
        """
        this function minimizes the app to taskbar

        Inputs: None

        Returns: None
        """
        
        self.logger.create_new_log(message='Setting app minimized to taskbar.')
        self.showMinimized()


    def maxmize_minimize(self):
        """
        this function chages the window size of app

        Inputs: None

        Returns: None
        """

        if self.isMaximized():
            self.showNormal()
            # self.sheet_view_down=data_grabber.sheetOverView(h=129,w=1084,nh=12,nw=30)
        else:
            self.showMaximized()

        self.logger.create_new_log(message='Setting app minimized/maximized.')


    def leftmenu(self):
        """
        this function s used to show/hide the left side bar with an sliding effect

        Inputs: None

        Returns: None
        """
        
        width=self.leftMenuBg.width()
        # self.stackedWidget_defect.setCurrentWidget(self.page_no)
        # self.stackedWidget_defect.setMaximumHeight(60)
        # x=self.stackedWidget_defect.height()
        #print('height',height)
        if width ==0:
            #
            self.left_box = QPropertyAnimation(self.topMenu, b"maximumHeight")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(0)
            self.left_box.setEndValue(11111)
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_2 = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
            self.left_box_2.setDuration(Settings.TIME_ANIMATION)
            self.left_box_2.setStartValue(0)
            self.left_box_2.setEndValue(60)
            self.left_box_2.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_5 = QPropertyAnimation(self.leftMenuBg, b"maximumWidth")
            self.left_box_5.setDuration(Settings.TIME_ANIMATION)
            self.left_box_5.setStartValue(0)
            self.left_box_5.setEndValue(60)
            self.left_box_5.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_3 = QPropertyAnimation(self.toogle_btn_1, b"minimumWidth")
            self.left_box_3.setDuration(Settings.TIME_ANIMATION)
            self.left_box_3.setStartValue(0)
            self.left_box_3.setEndValue(34)
            self.left_box_3.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_4 = QPropertyAnimation(self.toogle_btn_2, b"minimumWidth")
            self.left_box_4.setDuration(Settings.TIME_ANIMATION)
            self.left_box_4.setStartValue(34)
            self.left_box_4.setEndValue(0)
            self.left_box_4.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.left_box)
            self.group.addAnimation(self.left_box_2)
            self.group.addAnimation(self.left_box_3)
            self.group.addAnimation(self.left_box_4)
            self.group.addAnimation(self.left_box_5)
            # self.group.addAnimation(self.right_box)
            self.group.start()    

        else:
            #
            self.left_box = QPropertyAnimation(self.topMenu, b"maximumHeight")
            self.left_box.setDuration(Settings.TIME_ANIMATION)
            self.left_box.setStartValue(width)
            self.left_box.setEndValue(0)
            self.left_box.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_2 = QPropertyAnimation(self.leftMenuBg, b"minimumWidth")
            self.left_box_2.setDuration(Settings.TIME_ANIMATION)
            self.left_box_2.setStartValue(60)
            self.left_box_2.setEndValue(0)
            self.left_box_2.setEasingCurve(QEasingCurve.InOutQuart)
            #
            self.left_box_5 = QPropertyAnimation(self.leftMenuBg, b"maximumWidth")
            self.left_box_5.setDuration(Settings.TIME_ANIMATION)
            self.left_box_5.setStartValue(60)
            self.left_box_5.setEndValue(0)
            self.left_box_5.setEasingCurve(QEasingCurve.InOutQuart)            
            #
            self.left_box_3 = QPropertyAnimation(self.toogle_btn_1, b"minimumWidth")
            self.left_box_3.setDuration(Settings.TIME_ANIMATION)
            self.left_box_3.setStartValue(34)
            self.left_box_3.setEndValue(0)
            self.left_box_3.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.left_box_4 = QPropertyAnimation(self.toogle_btn_2, b"minimumWidth")
            self.left_box_4.setDuration(Settings.TIME_ANIMATION)
            self.left_box_4.setStartValue(0)
            self.left_box_4.setEndValue(34)
            self.left_box_4.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.left_box)
            self.group.addAnimation(self.left_box_2)
            self.group.addAnimation(self.left_box_3)
            self.group.addAnimation(self.left_box_4)
            self.group.addAnimation(self.left_box_5)
            # self.group.addAnimation(self.right_box)
            self.group.start()    
 

    def animation_move(self,label_name,lenght):
        """
        this function is used to shiw/hide an element (frame) with an sliding effect

        Inputs: None

        Returns: None
        """

        width=label_name.width()
        # self.stackedWidget_defect.setCurrentWidget(self.page_no)
        # self.stackedWidget_defect.setMaximumHeight(60)
        # x=self.stackedWidget_defect.height()
        #print('height',height)
        if width ==0:
            #
            self.animation_box = QPropertyAnimation(label_name, b"minimumWidth")
            self.animation_box.setDuration(Settings.TIME_ANIMATION)
            self.animation_box.setStartValue(0)
            self.animation_box.setEndValue(lenght)
            self.animation_box.setEasingCurve(QEasingCurve.InOutQuart) 
            #
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.animation_box)
            self.group.start() 

        else:
            #
            self.animation_box = QPropertyAnimation(label_name, b"minimumWidth")
            self.animation_box.setDuration(Settings.TIME_ANIMATION)
            self.animation_box.setStartValue(lenght)
            self.animation_box.setEndValue(0)
            self.animation_box.setEasingCurve(QEasingCurve.InOutQuart)
            #
            self.group = QParallelAnimationGroup()
            self.group.addAnimation(self.animation_box)
            self.group.start() 


    def activate_(self):
        """
        This function will activate ui operating buttons and connect theme to their functions

        Inputs: None

        Returns: None
        """

        # top left buttons
        #self.closeButton.clicked.connect(self.close_win)
        self.miniButton.clicked.connect(self.minimize_win)
        self.maxiButton.clicked.connect(self.maxmize_minimize)

        # side menu show/hide button
        self.toogle_btn_1.clicked.connect(partial(self.leftmenu))
        self.toogle_btn_2.clicked.connect(partial(self.leftmenu))

        # dashboard page buttons and side menu buttons
        #
        self.side_dashboard_btn.clicked.connect(self.buttonClick)
        #
        self.camera_setting_btn.clicked.connect(self.buttonClick)
        self.side_camera_setting_btn.clicked.connect(self.buttonClick)
        #
        self.calibration_setting_btn.clicked.connect(self.buttonClick)
        self.side_calibration_setting_btn.clicked.connect(self.buttonClick)
        #
        self.general_setting_btn.clicked.connect(self.buttonClick)
        self.side_general_setting_btn.clicked.connect(self.buttonClick)
        #
        self.plc_setting_btn.clicked.connect(self.buttonClick)
        self.side_plc_setting_btn.clicked.connect(self.buttonClick)
        #
        self.defect_setting_btn.clicked.connect(self.buttonClick)
        self.side_defect_setting_btn.clicked.connect(self.buttonClick)
        #
        self.side_storage_setting_btn.clicked.connect(self.buttonClick)
        self.storage_setting_btn.clicked.connect(self.buttonClick)
        #
        self.side_users_setting_btn.clicked.connect(self.buttonClick)
        self.users_setting_btn.clicked.connect(self.buttonClick)

        # camera setting page buttons
        self.camera01_btn.clicked.connect(self.buttonClick)
        self.camera02_btn.clicked.connect(self.buttonClick)
        self.camera03_btn.clicked.connect(self.buttonClick)
        self.camera04_btn.clicked.connect(self.buttonClick)
        self.camera05_btn.clicked.connect(self.buttonClick)
        self.camera06_btn.clicked.connect(self.buttonClick)
        self.camera07_btn.clicked.connect(self.buttonClick)
        self.camera08_btn.clicked.connect(self.buttonClick)
        self.camera09_btn.clicked.connect(self.buttonClick)
        self.camera10_btn.clicked.connect(self.buttonClick)
        self.camera11_btn.clicked.connect(self.buttonClick)
        self.camera12_btn.clicked.connect(self.buttonClick)
        self.camera13_btn.clicked.connect(self.buttonClick)
        self.camera14_btn.clicked.connect(self.buttonClick)
        self.camera15_btn.clicked.connect(self.buttonClick)
        self.camera16_btn.clicked.connect(self.buttonClick)
        self.camera17_btn.clicked.connect(self.buttonClick)
        self.camera18_btn.clicked.connect(self.buttonClick)
        self.camera19_btn.clicked.connect(self.buttonClick)
        self.camera20_btn.clicked.connect(self.buttonClick)
        self.camera21_btn.clicked.connect(self.buttonClick)
        self.camera22_btn.clicked.connect(self.buttonClick)
        self.camera23_btn.clicked.connect(self.buttonClick)
        self.camera24_btn.clicked.connect(self.buttonClick)
        self.checkBox_top.clicked.connect(self.buttonClick)
        self.checkBox_bottom.clicked.connect(self.buttonClick)

        # user page
        #self.add_user_btn.clicked.connect(self.buttonClick)

    
    # button click connctor
    def buttonClick(self):
        """
        this funcion will connect each button in ui to its function

        Inputs: None

        Returns: None
        """
        
        # GET BUTTON CLICKED
        btn = self.sender()
        btnName = btn.objectName()
        
        if btnName =='camera_setting_btn' and self.stackedWidget.currentWidget()!=self.page_camera_setting:
            self.stackedWidget.setCurrentWidget(self.page_camera_setting)
         
        if btnName =='side_camera_setting_btn' and self.stackedWidget.currentWidget()!=self.page_camera_setting:
            self.stackedWidget.setCurrentWidget(self.page_camera_setting)
        
        if btnName =='side_dashboard_btn' and self.stackedWidget.currentWidget()!=self.page_dashboard:
            self.stackedWidget.setCurrentWidget(self.page_dashboard)
        
        if btnName =='users_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_users_setting)
        
        if btnName =='side_users_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_users_setting)
        
        # if btnName =='add_user_btn' :
        #     self.animation_move(self.frame_add_user,300)

        if btnName =='defect_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_defects)
        
        if btnName =='side_defect_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_defects)

        if btnName =='calibration_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_calibration_setting)

        if btnName =='side_calibration_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_calibration_setting)
        
        if btnName =='general_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_settings)

        if btnName =='side_general_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_settings)

        if btnName =='plc_setting_btn' :
            self.stackedWidget.setCurrentWidget(self.page_plc_setting)

        if btnName =='side_plc_setting_btn':
            self.stackedWidget.setCurrentWidget(self.page_plc_setting)

        if btnName == 'side_storage_setting_btn':
            self.stackedWidget.setCurrentWidget(self.page_storage)

        if btnName == 'storage_setting_btn':
            self.stackedWidget.setCurrentWidget(self.page_storage)

        # camera buttons in camera setting page
        if btnName[:6] == 'camera' and btnName != 'camera_setting_btn':
            camera_id = btnName[6:8]
            #
            if not self.camera_setting_apply_btn.isEnabled() or (self.cameraname_label.text()!='No Camera Selected' and self.cameraname_label.text()[-2:]!=camera_id):
                self.cameraname_label.setText('Cam%s' % camera_id)
                self.change_camera_btn_icon(camera_id, active=True)
                self.camera_setting_apply_btn.setEnabled(True)
                self.camera_setting_connect_btn.setStyleSheet("background-color: {}; border: Transparent;".format(colors_pallete.successfull_green))
                self.set_button_enable_or_disable(self.camera_params, enable=True)
            #
            else:
                self.disable_camera_settings()
                self.change_camera_btn_icon(camera_id, active=False)


    def set_combo_boxes(self):
        """
        this function is used to set the content of comboboxes in ui

        Inputs: None

        Outputs: None
        """
        
        # user rules combo box in user management page
        x = user_management_funcs.default_user_roles
        self.user_role.addItems(x)

        # blocksize combo in calibration page (Miss.Abtahi algo)
        x=['Small','Medium','Large']
        self.block_image_proccessing={'Small':100,'Medium':200,'Large':300}
        self.comboBox_block_size.addItems(x)
        self.comboBox_block_size.currentTextChanged.connect(self.combo_image_preccess)

        # camera select combo in calibration page
        cam_nums=[]
        #
        for i in range(1, camera_funcs.num_cameras+1):
            cam_nums.append(str(i))
        #
        self.comboBox_cam_select_calibration.addItems(cam_nums)
        self.comboBox_cam_select_calibration.currentTextChanged.connect(self.selected_camera)


    def set_sliders(self):
        """
        this function is used to connect siders in ui to their functions

        Inputs: None

        Outputs: None
        """
        
        # sliders in calibration page (Miss.Abtahi algo)
        self.verticalSlider_noise.valueChanged[int].connect(self.show_value)
        self.verticalSlider_defect.valueChanged[int].connect(self.show_value)


    def set_checkboxes(self):
        """
        this function is used to connect checkboxes in ui to their functions

        Inputs: None

        Outputs: None
        """
        
        # checkboxes in calibration page (Miss.Abtahi algo)
        # self.checkBox_noise.stateChanged.connect(lambda:self.btnstate(self.b1))
        self.checkBox_noise.setChecked(True)
        self.checkBox_noise.stateChanged.connect(lambda:self.check_box_state(self.checkBox_noise))


    def check_box_state(self, b):
        """
        this function is used to change checkbox text to enable/disable by checkbox state

        Inputs:
            b: checkbox element

        Outputs: None
        """

        if b.isChecked() == True:
            b.setText('Enable')
        else:
            b.setText('Disable')
                    
            
    def show_value(self, value):
        """
        this function is used to show slider value in an label/textbox

        Inputs:
            value: value of the slider (in int)

        Outputs: None
        """
        
        btn = self.sender()
        btnName = btn.objectName()
        if btnName=='verticalSlider_noise':
            self.remaining_noise.setText(str(value))
        elif btnName=='verticalSlider_defect':
            self.remaining_defect.setText(str(value))


    def combo_image_preccess(self,s):
        # self.block_image_proccessi
        self.remaining_p_value.setText(str(self.block_image_proccessing[s]))
        self.set_default_image_proccess(s)


    def set_default_image_proccess(self,value):
        if value=='Small':
            self.verticalSlider_defect.setValue(1.5)
            self.verticalSlider_noise.setValue(42)
        #
        if value=='Medium':
            self.verticalSlider_defect.setValue(3)
            self.verticalSlider_noise.setValue(35)
        #
        if value=='Large':
            self.verticalSlider_defect.setValue(2)
            self.verticalSlider_noise.setValue(40)


    def selected_camera(self, s):
        """
        this function is used to change the camrea icon in calibration page

        Inputs:
            s: id of camera (in int)

        Outputs: None
        """
        
        # set default off icon for all cameras
        for i in range(1, camera_funcs.num_cameras):
            if i<13:
                eval('self.camera%s_btn_2'%i).setIcon(QIcon('images/camtop.png'))
            else:
                eval('self.camera%s_btn_2'%i).setIcon(QIcon('images/cambtm.png'))

        # set on icon for selected camera
        cam_num = s
        #
        if int(s)<13:
            eval('self.camera%s_btn_2'%cam_num).setIcon(QIcon('images/camtop_actived.png'))
        else :
            eval('self.camera%s_btn_2'%cam_num).setIcon(QIcon('images/cambtm_actived.png'))


    # User Managment page --------------------------------
    def get_user_pass(self):
        """
        this function is used to get and return entered username and password from login window

        Inputs: None

        Returns:
            username: in string
            password: in string
        """
        
        self.user_name_value=self.user_name.text()
        self.password_value=self.password.text()
        #
        return self.user_name_value, self.password_value


    def set_login_message(self, text, color):
        """
        this function is used to set login message on login window 

        Inputs:
            text: message to show (in string)
            color: color of the message text (in string, html code without #, or color name)

        Outputs: None
        """
        
        self.login_message.setText(text)
        self.login_message.setStyleSheet("color: #{};".format(color))


    
    def show_mesagges(self, label_name, text='', level=0, clearable=True, prefix=True):
        """
        this function is used to show input message in input label, also there is a message level determining the color of label, and a timer to clear meesage after a while

        Inputs:
            label_name: label element name to show the message in
            text: input message to show (in string)
            level: level of the message (in int), its a value betweem [0, 2] determining the bakground color of message label
            clearable: a boolean value determining whater to clear the message after timeout or not
            prefix: a boolean value determinign wheater to show the message prefix or not
        
        Returns: None
        """
        
        if text != '':
            if level == 0:
                label_name.setText(text)
                label_name.setStyleSheet('background-color: %s; color:white;' % (colors_pallete.successfull_green))
            #
            if level == 1:
                if prefix:
                    label_name.setText(text)
                else:
                    label_name.setText(text)
                label_name.setStyleSheet('background-color: %s; color:white;' % (colors_pallete.warning_yellow))
            #
            if level >= 2:
                if prefix:
                    label_name.setText(text)
                else:
                    label_name.setText(text)
                label_name.setStyleSheet('background-color: %s; color:white;' % (colors_pallete.failed_red))

            #
            if clearable and not self.show_mesagges_thread_lock:
                self.show_mesagges_thread_lock = True
                # timer to clear the message
                threading.Timer(2, self.show_mesagges, args=(label_name,)).start()


        # clear the message after timeout
        else:
            label_name.setText('')
            label_name.setStyleSheet('')
            # unlock thread
            self.show_mesagges_thread_lock = False



    def clear_line_edits(self,line_edits):
        """
        this function is used to clear the lineedit texts

        Inputs: None

        Rrturns: None
        """
        
        for i in range(len(line_edits)):
            line_edits[i].setText('')


    # Calibration Page-----------------------
    def get_image_proccessing_parms(self):
        """
        this function is used to take and return entered image calibration parms of Miss.Abtahi algo from ui

        Inputs: None

        Outputs:
            dict{block_size, defect, noise, noise_flag}
        """
        
        combo=self.comboBox_block_size.currentText()
        defect=self.verticalSlider_defect.value()
        noise=self.verticalSlider_noise.value()
        noise_flag=self.checkBox_noise.isChecked()
        #
        return {'block_size':combo,'defect':defect/10,'noise':noise,'noise_flag':noise_flag}


    def get_width_guage_parms(self):
        """
        this function will returns the user slected camera in calibration page

        Inputs: None

        Return: camrera id (in string)
        """
        
        combo=self.comboBox_cam_select_calibration.currentText()
        return combo


    def disable_camera_settings(self):
        """
        this function will disable all camera params fileds in camera setting page, on camera disable/change or stackwidjet change

        Inputs: None

        Returns: None
        """
        
        self.cameraname_label.setText('No Camera Selected')
        self.camera_setting_apply_btn.setEnabled(False)
        self.camera_setting_connect_btn.setStyleSheet("background-color: {}; border:Transparent;".format(colors_pallete.disabled_btn))
        # disable camera params fields
        self.set_button_enable_or_disable(self.camera_params, enable=False)
        

    def set_button_enable_or_disable(self, names, enable=True):
        """
        this function will enable or disble all the ui elements in the input list

        Inputs:
            names: ui elements (in list)
            enable: a boolean value determining wheather to enable/diable the elements
        """
        
        for name in names:
            name.setEnabled(enable)


    def set_label(self, label_name, msg, color='black'):
        """
        this funcion will set a text message to a label element, with text color

        Inputs:
            label_name: label element name
            msg: input message (in string)
            color: message/text color (in string, html code or color name)
        
        Returns: None
        """
        
        label_name.setText(msg)
        if color:
            label_name.setStyleSheet("color: {};".format(color))
 

    def get_label(self, label_name):
        """
        this function is used to take and return the text content of a label elemnt

        Inputs:
            label_name: name of label element
        
        Returns: None
        """
        
        return label_name.text()


    def set_image_label(self, label_name, img):
        """
        this function is used to set/fit an image to a label element

        Inputs:
            label_name: name of the label element
            img: input image to fit/set to label
        
        Returns: None
        """
        
        h, w, ch = img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = sQImage(img.data, w, h, bytes_per_line, sQImage.Format_RGB888)
        #
        label_name.setPixmap(sQPixmap.fromImage(convert_to_Qt_format))


    def change_camera_btn_icon(self, camera_id, active=False):
        """
        this function is used to change the current camera icon in camera settings page

        Inputs:
            camera_id: id of the cameras (in string)
            active: a boolean value determinging wheater the camera is selected or deselected

        Outputs: None
        """
        
        image_active_id = 'images/cambtm_actived.png' if int(camera_id)>12 else 'images/camtop_actived.png' 

        # deactive
        for cam_id in camera_funcs.all_camera_ids:
            image_deactive_id = 'images/cambtm.png' if int(cam_id)>12 else 'images/camtop.png'
            eval('self.camera%s_btn' % cam_id).setIcon(QIcon(image_deactive_id))

        # active
        if active:    
            eval('self.camera%s_btn' % camera_id).setIcon(QIcon(image_active_id))

    
    def set_size(self, frame_name, size, minimum=False, maximum=False):
        """
        this function is used to set maximum or minimum height for an element (frame)in ui 

        Inputs:
            frame_name: name of frame element
            size: height/size of elemen
            minimum: a boolean value determning wheater the input height/size is minimumheight or not
            maximum: a boolean value determning wheater the input height/size is maximumheight or not
                if both minimum and maximum be False, the size will be applied as both minimumheight and maximumheight
        
        Returns: None
        """
        
        if maximum:
            frame_name.setMaximumHeight(size)

        if minimum:
            frame_name.setMinimumHeight(size)

        else:
            frame_name.setMaximumHeight(size)
            frame_name.setMinimumHeight(size)


    def get_plc_ip(self):
        """
        this function takes anf returns input PLC IP from ui

        Inputs: None

        Returns:
            PLC ip: (in string)
        """
        
        return self.plc_ip_line.text()
    

    def set_plc_ip(self, text):
        """
        this function will set input PLC IP from database to ui field

        Inputs:
            text: PLC ip (in string)

        Returns: None
        """

        self.plc_ip_line.setText(text)


    def get_plc_parms(self):
        """
        this function will take and returns the input PLC parameters and addreses from ui

        Inputs: None

        Outputs:
            dict: {limitswitch_top_plc, limitswitch_bottom_plc, thermometer_min_plc, thermometer_max_plc,
                    cooler_uptime_plc, system_operating_plc, air_valve_plc, camera_limit_plc':[camera_limit_path, -1, -1],
                    camera_frate_plc, projector_limit_plc, detect_sensor_plc
        """
        
        # limit switches
        limitswitch_top_path = self.line_limitswitch_top_plc.text()
        limitswitch_top_offvalue = self.value0_limitswitch_top_plc.text()
        limitswitch_top_onvalue = self.value1_limitswitch_top_plc.text()
        #
        limitswitch_bottom_path = self.line_limitswitch_bottom_plc.text()
        limitswitch_bottom_offvalue = self.value0_limitswitch_bottom_plc.text()
        limitswitch_bottom_onvalue = self.value1_limitswitch_bottom_plc.text()

        # thermometers
        thermometer_min_path = self.line_thermometer_min_plc.text()
        thermometer_min_value = self.value0_thermometer_min_plc.text()
        #
        thermometer_max_path = self.line_thermometer_max_plc.text()
        thermometer_max_value = self.value0_thermometer_max_plc.text()

        # cooler uptime
        cooler_uptime_path = self.line_cooler_uptime_plc.text()
        cooler_uptime_value = self.value0_cooler_uptime_plc.text()

        # system operating
        system_operating_path = self.line_system_operating_plc.text()

        # air valve
        air_valve_path = self.line_air_valve_plc.text()

        # camera limit (n camera)
        camera_limit_path = self.line_camera_limit_plc.text()

        # camera frame rate
        camera_frate_path = self.line_camera_frate_plc.text()
        camera_frate_value = self.value0_camera_frate_plc.text()

        # projector limit (n projector)
        projector_limit_plc_path = self.line_projector_limit_plc.text()

        # coil detect sensor
        detect_sensor_plc_path = self.line_detect_sensor_plc.text()
        
        return {'limitswitch_top_plc':[limitswitch_top_path, limitswitch_top_offvalue, limitswitch_top_onvalue],
                'limitswitch_bottom_plc':[limitswitch_bottom_path, limitswitch_bottom_offvalue, limitswitch_bottom_onvalue],
                'thermometer_min_plc':[thermometer_min_path, thermometer_min_value, -1],
                'thermometer_max_plc':[thermometer_max_path, thermometer_max_value, -1],
                'cooler_uptime_plc':[cooler_uptime_path, cooler_uptime_value, -1],
                'system_operating_plc':[system_operating_path, -1, -1],
                'air_valve_plc':[air_valve_path, -1, -1],
                'camera_limit_plc':[camera_limit_path, -1, -1],
                'camera_frate_plc':[camera_frate_path, camera_frate_value, -1],
                'projector_limit_plc':[projector_limit_plc_path, -1, -1],
                'detect_sensor_plc':[detect_sensor_plc_path, -1, -1]}

    
    # translate ui
    def translate_ui(self):
        """
        This function translate ui to selected language in settings page

        Inputs: None

        Returns: None
        """

        # persian
        if self.setting_language_comboBox.currentText() == mainsetting_funcs.app_languages[1]:
            change_language_flag = False

            try:
            # load ui file in qml format
                qml_tree = ET.ElementTree(file=ui_file_path_en)

                # get string tags in file (containing titles in ui)
                all_name_elements = qml_tree.findall('.//string')

                # replace english titles with persian
                for element in all_name_elements:
                    if element.text in texts.Titles.keys():
                        element.text = texts.Titles[element.text]['fa']
                
                # save the new file
                qml_tree.write(ui_file_path_fa)
                self.start_up_settings.update({"language": "fa"})
                with open(app_startup_json_path, 'w') as f:
                    json.dump(self.start_up_settings, f , indent=4, sort_keys=True)
                f.close()

                # log
                self.logger.create_new_log(message=texts.MESSEGES['translate_ui_to_persian']['en'], level=1)
                change_language_flag = True

            except Exception as e:
                self.logger.create_new_log(message=texts.ERRORS['failed_to_translate_ui_to_persian']['en'], level=5)

        # english
        elif self.setting_language_comboBox.currentText() == mainsetting_funcs.app_languages[0]:
            try:
                self.start_up_settings.update({"language": "en"})
                with open(app_startup_json_path, 'w') as f:
                    json.dump(self.start_up_settings, f , indent=4, sort_keys=True)
                f.close()

                # log
                self.logger.create_new_log(message=texts.MESSEGES['translate_ui_to_english']['en'], level=1)
                change_language_flag = True

            except Exception as e:
                self.logger.create_new_log(message=texts.ERRORS['failed_to_translate_ui_to_english']['en'], level=5)

        if change_language_flag:
            self.close_app_force(message=texts.MESSEGES['app_close_change_language'][self.language], change_language=True)

    
    def translate_headers_list(self, header_list):
        """
        this function is used to translate table headers or generally, all texts in and list, to ui default language

        Inputs:
            header_list: a list of texts that will be translated

        Outputs:
            header_list: translated list of texts
        """
        
        if self.language != 'en':
            for i in range(len(header_list)):
                try:
                    # translate each text by the texts dict file
                    header_list[i] = texts.Titles[header_list[i]][self.language]
                except:
                    pass
        
        return header_list

        


if __name__ == "__main__":
    app = QApplication()
    win = UI_main_window()
    # apply_stylesheet(app,theme='dark_cyan.xml')
    api = setting_api.API(win)
    win.show()
    sys.exit(app.exec())
    