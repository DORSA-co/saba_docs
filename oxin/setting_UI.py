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

from backend import camera_funcs, colors_pallete, logging_funcs
import setting_api
from app_settings import Settings


ui, _ = loadUiType("main_window_Copy.ui")


os.environ["QT_FONT_DPI"] = "96" # FIX Problem for High DPI and Scale above 100%
class UI_main_window(QMainWindow, ui):
    global widgets
    widgets = ui

    def __init__(self):
        super(UI_main_window, self).__init__()

        # window setup
        self.setupUi(self)
        flags = Qt.WindowFlags(Qt.FramelessWindowHint)
        self.pos_ = self.pos()
        self.setWindowFlags(flags)
        self.app_close_flag = False
        self.activate_()
        # title
        title = "SABA - Settings App"
        self.setWindowTitle(title)
        self._old_pos = None
        # SET LANGUAGE
        self.language = 'en'


        # logger object
        self.logger = logging_funcs.app_logger(name='saba_setting-app_logger', log_mainfolderpath='./app_logs', console_log=True)
        self.logger.create_new_log(message='UI object for setting app created.')


        # flag parameters
        self.cam_num_old=1
        self.camera_connect_flag = False
        self.calibration_image = None
        self.login_flag = False

        # plc
        self.plc_connect = False
        

        # dashboard button ids
        self.dash_buttons = [self.camera_setting_btn,self.calibration_setting_btn, self.plc_setting_btn\
                            , self.defect_setting_btn, self.users_setting_btn, self.level2_setting_btn\
                            ,self.general_setting_btn, self.storage_setting_btn]
        # side-bar button ids
        self.side_buttons = [self.side_camera_setting_btn, self.side_calibration_setting_btn, self.side_plc_setting_btn\
                            , self.side_defect_setting_btn, self.side_users_setting_btn, self.side_level2_setting_btn\
                            ,self.side_general_setting_btn, self.side_storage_setting_btn, self.side_dashboard_btn]

        # camera variable parameters ids in the camera-settings section of the UI 
        self.camera_params = [self.gain_spinbox, self.expo_spinbox, self.width_spinbox\
                            , self.height_spinbox, self.offsetx_spinbox, self.offsety_spinbox\
                            ,self.trigger_combo, self.maxbuffer_spinbox, self.packetdelay_spinbox\
                                , self.packetsize_spinbox, self.transmissiondelay_spinbox, self.ip_lineedit, self.serial_number_combo, self.camera_setting_connect_btn]
        
        # PLC check buttons
        self.PLC_btns = ['check_thermometer_min_plc', 'check_thermometer_max_plc', 'check_cooler_uptime_plc',
                         'check_system_operating_plc', 'check_air_valve_plc', 'check_camera_limit_plc', 'check_projector_limit_plc',
                         'check_detect_sensor_plc', 'check_limitswitch_top_plc', 'check_limitswitch_bottom_plc']


        # others
        self.main_login_btn.setIcon(sQPixmap.fromImage(sQImage('images/login_white.png')))
        self.set_combo_boxes()
        self.set_sliders()
        self.set_checkboxes()
        self.stackedWidget.currentChanged.connect(self.disable_camera_settings)
        self.stackedWidget.setCurrentWidget(self.page_dashboard)

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
        self.app_close_flag = True
        self.logger.create_new_log(message='Setting app closed.')
        self.close()
        sys.exit()


    def close_app_force(self, message='An Error occured while runnung the app'):
        self.app_close_flag = True
        self.logger.create_new_log(message='Setting app closed by force, there may an error/exception occured.', level=4)
        # alert message
        alert_window = sQMessageBox(sQMessageBox.Warning, 'SABA - Settings App Error', message)
        alert_window.setStandardButtons(sQMessageBox.Ok)
        icon = sQIcon()
        icon.addPixmap(sQPixmap("images/alert.png"), sQIcon.Normal)
        alert_window.setWindowIcon(icon)
        alert_window.exec()
        #
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
        self.logger.create_new_log(message='Setting app minimized to taskbar.')
        self.showMinimized()


    def maxmize_minimize(self):
        if self.isMaximized():
            self.showNormal()
            # self.sheet_view_down=data_grabber.sheetOverView(h=129,w=1084,nh=12,nw=30)
        else:
            self.showMaximized()
        self.logger.create_new_log(message='Setting app minimized/maximized.')


    def leftmenu(self):
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
        #self.closeButton.clicked.connect(self.close_win)
        self.miniButton.clicked.connect(self.minimize_win)
        self.maxiButton.clicked.connect(self.maxmize_minimize)
        #
        self.toogle_btn_1.clicked.connect(partial(self.leftmenu))
        self.toogle_btn_2.clicked.connect(partial(self.leftmenu))
        # dashboard page
        self.camera_setting_btn.clicked.connect(self.buttonClick)
        self.side_camera_setting_btn.clicked.connect(self.buttonClick)
        self.side_dashboard_btn.clicked.connect(self.buttonClick)
        self.calibration_setting_btn.clicked.connect(self.buttonClick)
        self.side_calibration_setting_btn.clicked.connect(self.buttonClick)
        self.general_setting_btn.clicked.connect(self.buttonClick)
        self.side_general_setting_btn.clicked.connect(self.buttonClick)
        self.plc_setting_btn.clicked.connect(self.buttonClick)
        self.side_plc_setting_btn.clicked.connect(self.buttonClick)
        self.defect_setting_btn.clicked.connect(self.buttonClick)
        self.side_defect_setting_btn.clicked.connect(self.buttonClick)
        self.side_storage_setting_btn.clicked.connect(self.buttonClick)
        self.storage_setting_btn.clicked.connect(self.buttonClick)
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
        self.add_user_btn.clicked.connect(self.buttonClick)

    
    # button click connctor
    def buttonClick(self):
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
        
        if btnName =='add_user_btn' :
            self.animation_move(self.frame_add_user,300)

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

        if btnName[:6] == 'camera' and btnName != 'camera_setting_btn':
            camera_id = btnName[6:8]
            #
            if not self.camera_setting_apply_btn.isEnabled() or (self.cameraname_label.text()!='No Camera Selected' and self.cameraname_label.text()[-2:]!=camera_id):
                self.cameraname_label.setText('Cam%s' % camera_id)
                #self.change_camera_btn_icon(camera_id, active=True)
                self.camera_setting_apply_btn.setEnabled(True)
                self.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.successfull_green))
                self.set_button_enable_or_disable(self.camera_params, enable=True)
            #
            else:
                self.disable_camera_settings()
                #self.change_camera_btn_icon(camera_id, active=False)


    def set_combo_boxes(self):
        x=["Operator", "Admin", "DORSA"]
        self.user_role.addItems(x)
        #
        x=['Small','Medium','Large']
        self.block_image_proccessing={'Small':100,'Medium':200,'Large':300}
        self.comboBox_block_size.addItems(x)
        self.comboBox_block_size.currentTextChanged.connect(self.combo_image_preccess)
        #
        cam_nums=[]
        #
        for i in range(1,25):
            cam_nums.append(str(i))
        #
        self.comboBox_cam_select_calibration.addItems(cam_nums)
        self.comboBox_cam_select_calibration.currentTextChanged.connect(self.selected_camera)


    def set_sliders(self):
        self.verticalSlider_noise.valueChanged[int].connect(self.show_value)
        self.verticalSlider_defect.valueChanged[int].connect(self.show_value)


    def set_checkboxes(self):
        # self.checkBox_noise.stateChanged.connect(lambda:self.btnstate(self.b1))
        self.checkBox_noise.setChecked(True)
        self.checkBox_noise.stateChanged.connect(lambda:self.check_box_state(self.checkBox_noise))


    def check_box_state(self,b):
            if b.isChecked() == True:
                b.setText('Enable')
            else:
                b.setText('Disable')
                    
            
    def show_value(self,value):
        print(value)
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


    def selected_camera(self,s):
        for i in range(1,25):
            if i<13:
                eval('self.camera%s_btn_2'%i).setIcon(QIcon('images/camtop.png'))
            else:
                eval('self.camera%s_btn_2'%i).setIcon(QIcon('images/cambtm.png'))
        #
        cam_num=s
        #
        if int(s)<13:
            eval('self.camera%s_btn_2'%cam_num).setIcon(QIcon('images/camtop_actived.png'))
        else :
            eval('self.camera%s_btn_2'%cam_num).setIcon(QIcon('images/cambtm_actived.png'))


    # User Managment page --------------------------------
    def get_user_pass(self):
        self.user_name_value=self.user_name.text()
        self.password_value=self.password.text()
        return self.user_name_value, self.password_value


    def set_login_message(self,text,color):
        self.login_message.setText(text)
        self.login_message.setStyleSheet("color:#{}".format(color))


    
    def show_mesagges(self, label_name, text='', level=0, clearable=True, prefix=True):
        if text != '':
            if level == 0:
                label_name.setText(text)
                label_name.setStyleSheet('background-color:%s ; color:white' % (colors_pallete.successfull_green))

            if level == 1:
                if prefix:
                    label_name.setText('Warning: ' + text)
                else:
                    label_name.setText(text)
                label_name.setStyleSheet('background-color:%s ; color:black' % (colors_pallete.warning_yellow))

            if level >= 2:
                if prefix:
                    label_name.setText('ERROR : ' + text)
                else:
                    label_name.setText(text)
                label_name.setStyleSheet('background-color:%s ; color:white' % (colors_pallete.failed_red))
            
            if clearable:
                threading.Timer(2, self.show_mesagges, args=(label_name,)).start()

        else:
            label_name.setText('')
            label_name.setStyleSheet('')



    def clear_line_edits(self,line_edits):
        for i in range(len(line_edits)):
            line_edits[i].setText('')


    # Calibration Page-----------------------
    def get_image_proccessing_parms(self):
        combo=self.comboBox_block_size.currentText()
        defect=self.verticalSlider_defect.value()
        noise=self.verticalSlider_noise.value()
        noise_flag=self.checkBox_noise.isChecked()
        return {'block_size':combo,'defect':defect/10,'noise':noise,'noise_flag':noise_flag}


    def get_width_guage_parms(self):
        combo=self.comboBox_cam_select_calibration.currentText()
        return combo


    def disable_camera_settings(self):
        self.cameraname_label.setText('No Camera Selected')
        self.camera_setting_apply_btn.setEnabled(False)
        self.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.disabled_btn))
        self.set_button_enable_or_disable(self.camera_params, enable=False)
        

    def set_button_enable_or_disable(self, names, enable=True):
        for name in names:
            name.setEnabled(enable)


    def set_label(self,label_name,msg, color='black'):
        label_name.setText(msg)
        if color:
            label_name.setStyleSheet("color:{}".format(color))
 

    def get_label(self,label_name):
        return label_name.text()


    def set_image_label(self,label_name, img):
        h, w, ch = img.shape
        bytes_per_line = ch * w
        convert_to_Qt_format = sQImage(img.data, w, h, bytes_per_line, sQImage.Format_RGB888)
        label_name.setPixmap(sQPixmap.fromImage(convert_to_Qt_format))


    def change_camera_btn_icon(self, camera_id, active=False):
        image_active_id = 'images/cambtm_actived.png' if int(camera_id)>12 else 'images/camtop_actived.png'    
        #
        for cam_id in camera_funcs.all_camera_ids:
            image_deactive_id = 'images/cambtm.png' if int(cam_id)>12 else 'images/camtop.png'
            eval('self.camera%s_btn' % cam_id).setIcon(QIcon(image_deactive_id))
        #
        if active:    
            eval('self.camera%s_btn' % camera_id).setIcon(QIcon(image_active_id))

    
    def set_size(self,frame_name,size,minimum=False,maximum=False):
        if maximum:
            frame_name.setMaximumHeight(size)
        if minimum:
            frame_name.setMinimumHeight(size)
        else:
            frame_name.setMaximumHeight(size)
            frame_name.setMinimumHeight(size)


    def get_plc_ip(self):
        return self.plc_ip_line.text()
    

    def set_plc_ip(self,text):
        self.plc_ip_line.setText(text)


    def get_plc_parms(self):
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
                'projector_limit_plc':[projector_limit_plc_path, -1, -1],
                'detect_sensor_plc':[detect_sensor_plc_path, -1, -1]}

    

if __name__ == "__main__":
    app = QApplication()
    win = UI_main_window()
    # apply_stylesheet(app,theme='dark_cyan.xml')
    api = setting_api.API(win)
    win.show()
    sys.exit(app.exec())
    