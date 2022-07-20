from PySide6 import QtCore as sQtCore
from functools import partial
import threading
from . import database_utils
import cv2
import os
import sys

from . import login_UI
from . import confirm_UI
from . import notif_UI
from .backend import camera_funcs, chart_funcs, colors_pallete, mainsetting_funcs, storage_funcs
from .backend import user_login_logout_funcs, user_management_funcs, pxvalue_calibration, defect_management_funcs, plc_managment, texts
from .calibrationCal.SteelSurfaceInspection import SSI
from .calibrationCal import load_recent_images
from .utils.move_on_list import moveOnList


class API:
    """
    the API class has the main functionalities of oxin setting app, it takes as input the ui object, and other ui objects like login window,
    alert window and notification windows are initialized in this class

    :param ui: the ui file of the app
    :returns: None
    """

    def __init__(self, ui):
        #------------------------------------------------------------------------------------------------------------------------
    
        # UIs of the app
        # main settings UI
        self.ui = ui # UI file
        self.initialize_flag_error = False # a flag for determining if any error occured while creating initial objects for app
        self.ui.logger.create_new_log(message=texts.MESSEGES['create_api_object']['en'])

        # login window UI and API
        try:
            self.login_ui = login_UI.UI_main_window(language=self.ui.language)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_login_ui']['en'])

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_login_ui_failed']['en'], level=5)

        # confirmation window UI
        try:
            self.confirm_ui = confirm_UI.UI_main_window(language=self.ui.language)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_confirm_ui']['en'])

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_confirm_ui_failed']['en'], level=5)

        # notif ui
        try:
            self.notif_manager = notif_UI.notification_manager()
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_notif_ui']['en'])

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_notif_ui_failed']['en'], level=5)


        #------------------------------------------------------------------------------------------------------------------------
        # APIs of the app
        try:
            self.login_api = login_UI.login_api.API(self.login_ui, logger_obj=self.ui.logger, language=self.ui.language)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_login_api']['en'])

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_login_api_failed']['en'], level=5)
        
        #------------------------------------------------------------------------------------------------------------------------
        # database module api
        try:
            self.db = database_utils.dataBaseUtils(logger_obj=self.ui.logger)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_database_object']['en'])

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_database_object_failed']['en'], level=5)
        
        #--------------------------------------------------
        # connect ui buttons
        try:
            self.button_connector()

        except Exception as e:
            self.initialize_flag_error = True
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_buttons_failed']['en'], level=5)


        # check if initializations are done correctly
        if self.initialize_flag_error:
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_objects_failed']['en'], level=4)
            self.ui.close_app_force(message=texts.ERRORS['initialize_objects_failed'][self.ui.language])
        

        #------------------------------------------------------------------------------------------------------------------------
        # define standalone params and flags
        # flag to chech whereas any user is logged in or not
        self.user_entered = False
        # waitkey
        self.waitkey = 2000
        # update picture waitkey/delay for updating camera picture in video mode
        self.update_picture_delay = 10
        # control of list of path for images or else
        self.move_on_list = moveOnList()
        # 
        self.pxcalibration_step = 0
        # defect edit flag
        self.edit_defect = False
        self.edit_defect_group = False
        # storage page
        self.force_clear = False
        self.camera_live_storage_check_thread_lock = False
        # plc page
        self.ui.set_size(self.ui.frame_121, 0, maximum=True)
        # Set Plc IP
        self.plc_connection_status=False
        # dashboard refresh interval key in startup json dict
        self.dasboard_refresh_interval_key = 'dasboard_refresh_interval' # in ms


        #------------------------------------------------------------------------------------------------------------------------
        # start-up functions
        # assign base parameters to UI
        mainsetting_funcs.assign_appearance_existing_params_to_ui(ui_obj=self.ui)
        # load and apply program appearance params
        try:
            self.load_appearance_params_on_start()
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_get_mainsettings_failed']['en'], level=5)
            self.ui.close_app_force(message=texts.ERRORS['database_get_mainsettings_failed'][self.ui.language])
        
        # create charts on ui
        try:
            chart_funcs.create_drive_barchart_on_ui(ui_obj=self.ui, frame_obj=self.ui.camera_live_storage_chart_frame)
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['create_charts_failed']['en'], level=5)
            self.ui.close_app_force(message=texts.ERRORS['create_charts_failed'][self.ui.language])

        # get available cameras and update database
        try:
            self.available_camera_serials = camera_funcs.get_available_cameras_list_serial_numbers()
            self.ui.logger.create_new_log(message=texts.MESSEGES['get_available_camera_serials']['en'], level=1)
            #
            if len(self.available_camera_serials) < camera_funcs.num_cameras:
                self.ui.logger.create_new_log(message=texts.WARNINGS['some_camera_not_connected']['en'], level=2)
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['camera_connection_api_failed']['en'], level=5)
            self.ui.close_app_force(message=texts.ERRORS['camera_connection_api_failed'][self.ui.language])
            
        #
        try:
            camera_funcs.update_available_camera_serials_on_db(db_obj=self.db, available_serials=self.available_camera_serials)
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_camera_serials_update_failed']['en'], level=5)


        #--------------------------------------------------------------------
        # threads/timers
        # real-time storage checking
        if storage_funcs.storage_check_interval_key in self.ui.start_up_settings.keys():
            self.run_storage_check_timer(storage_check_interval=self.ui.start_up_settings[storage_funcs.storage_check_interval_key])
            self.ui.cam_live_drive_interval_spin.setValue(self.ui.start_up_settings[storage_funcs.storage_check_interval_key])
            self.ui.logger.create_new_log(message=texts.MESSEGES['read_storage_check_interval_from_json']['en'], level=1)

        else:
            self.ui.logger.create_new_log(message=texts.WARNINGS['read_storage_check_interval_from_json_failed']['en'], level=2)
            self.run_storage_check_timer()
        
        # real-time dashboard refresh
        if self.dasboard_refresh_interval_key in self.ui.start_up_settings.keys():
            self.ui.logger.create_new_log(message=texts.MESSEGES['read_dashboard_refresh_interval_from_json']['en'], level=1)
            dashboard_refresh_interval = self.ui.start_up_settings[self.dasboard_refresh_interval_key]
        #
        else:
            self.ui.logger.create_new_log(message=texts.WARNINGS['read_dashboard_refresh_interval_from_json_failed']['en'], level=2)
            dashboard_refresh_interval = 10
            # update dashboard refresh nterval on app start-up json
            try:
                self.ui.start_up_settings.update({self.dasboard_refresh_interval_key: dashboard_refresh_interval})
                # save json
                with open(setting_UI.app_startup_json_path, 'w') as f:
                    json.dump(self.ui.start_up_settings, f , indent=4, sort_keys=True)
                f.close()

            except:
                pass

        #
        try:
            self.dashboard_check_timer = sQtCore.QTimer()
            self.dashboard_check_timer.timeout.connect(self.refresh_dashboard_page)
            self.dashboard_check_timer.start(dashboard_refresh_interval*1000)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_dashborad_refresh_timer']['en'] + ', interval: %s (s)' % (dashboard_refresh_interval), level=1)
        
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_dashboard_refresh_timer_failed']['en'], level=3)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['initialize_dashboard_refresh_timer_failed'][self.ui.language],
                                                win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)

        


        # create default records on database if not exist
        add_default_database_records.create_default_records(ui_obj=self.ui, api_obj=self)

    
 
    # functions
    #------------------------------------------------------------------------------------------------------------------------
    #------------------------------------------------------------------------------------------------------------------------
    # button connector for activating UI buttons functionality
    def button_connector(self):
        """
        this function is used to connect ui buttons to their functions

        :returns: None
        """

        # close nutton
        self.ui.closeButton.clicked.connect(self.on_close_operations)
        
        # login button
        self.ui.main_login_btn.clicked.connect(partial(lambda: user_login_logout_funcs.run_login_window(ui_obj=self.ui, login_ui_obj=self.login_ui, confirm_ui_obj=self.confirm_ui)))

        # camera buttons in the camera-settings section
        for cam_id in camera_funcs.all_camera_ids:
            eval('self.ui.camera%s_btn' % cam_id).clicked.connect(partial(self.load_camera_params_from_db_to_UI))

        # camera-parametrs or UI page change disconnect camera
        # disconnect camera on UI change (camera params change)
        self.ui.serial_number_combo.currentTextChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.gain_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.expo_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.width_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.height_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.offsetx_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.offsety_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.maxbuffer_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.packetdelay_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.packetsize_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.transmissiondelay_spinbox.valueChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.trigger_combo.currentTextChanged.connect(self.disconnect_camera_on_ui_change)
        self.ui.stackedWidget.currentChanged.connect(self.things_to_do_on_stackwidject_change)

        # buttons in the camera-settings section
        self.ui.camera_setting_apply_btn.clicked.connect(partial(self.save_changed_camera_params))
        self.ui.camera_setting_connect_btn.clicked.connect(partial(self.connect_dissconnect_to_camera))
        self.ui.camera_setting_getpic_btn.clicked.connect(partial(self.show_camera_picture))

        # buttons in the calibration-settings section
        self.ui.connet_camera_calibre_btn.clicked.connect(partial(lambda: self.connect_dissconnect_to_camera(calibration=True)))
        self.ui.calib_take_image.clicked.connect(partial(lambda: self.show_camera_picture(calibration=True)))
        self.ui.pixelvalue_prev_btn.clicked.connect(partial(lambda: pxvalue_calibration.apply_pxvalue_calibration(ui_obj=self.ui, api_obj=self, db_obj=self.db, image=self.ui.calibration_image.copy(), next=False)))
        self.ui.pixelvalue_next_btn.clicked.connect(partial(lambda: pxvalue_calibration.apply_pxvalue_calibration(ui_obj=self.ui, api_obj=self, db_obj=self.db, image=self.ui.calibration_image.copy(), next=True)))

        # login window and confirm window
        self.login_ui.login_btn.clicked.connect(partial(lambda: user_login_logout_funcs.authenticate_user(ui_obj=self.ui, login_ui_obj=self.login_ui, login_api_obj=self.login_api, api_obj=self)))
        self.confirm_ui.yes_btn.clicked.connect(partial(self.confirm_yes))
        self.confirm_ui.no_btn.clicked.connect(partial(self.confirm_ui.close))

        # User managment
        self.ui.users_setting_btn.clicked.connect(partial(self.refresh_users_table))
        self.ui.side_users_setting_btn.clicked.connect(partial(self.refresh_users_table))
        self.ui.remove_user_btn.clicked.connect(partial(self.remove_users))
        self.ui.create_user.clicked.connect(partial(self.add_user))

        # defects managment
        self.ui.defect_setting_btn.clicked.connect(partial(self.refresh_defects_table))
        self.ui.side_defect_setting_btn.clicked.connect(partial(self.refresh_defects_table))
        # self.ui.side_users_setting_btn.clicked.connect(partial(self.refresh_users_table))
        self.ui.remove_defect_btn.clicked.connect(partial(self.remove_defects))
        self.ui.remove_defect_group_btn.clicked.connect(partial(lambda: self.remove_defects(defect_group=True)))
        self.ui.edit_defect_btn.clicked.connect(partial(self.edit_defects))
        self.ui.edit_defect_group_btn.clicked.connect(partial(lambda: self.edit_defects(defect_group=True)))
        self.ui.show_realated_defect_btn.clicked.connect(partial(self.show_related_defects))
        self.ui.create_defect.clicked.connect(partial(self.add_defect))
        self.ui.search_defect_btn.clicked.connect(partial(self.filter_defects))
        self.ui.search_defectgroup_btn.clicked.connect(partial(lambda: self.filter_defects(defect_group=True)))
        self.ui.search_defect_clear_btn.clicked.connect(partial(lambda: self.refresh_defects_table(only_defects=True)))
        self.ui.search_defectgroup_clear_btn.clicked.connect(partial(lambda: self.refresh_defects_table(only_defect_groups=True)))
        self.ui.create_defect_group.clicked.connect(partial(self.add_defect_group))
        self.ui.defect_color_comboBox.currentTextChanged.connect(lambda: defect_management_funcs.update_combo_color(ui_obj=self.ui))
        self.ui.tableWidget_defects.horizontalHeader().sectionClicked.connect(self.tabledefects_onHeaderClicked)
        self.ui.tableWidget_defectgroups.horizontalHeader().sectionClicked.connect(self.tabledefectgroups_onHeaderClicked)

        # Calibration Page
        self.ui.load_recent_images.clicked.connect(self.select_image_procesing_directory)
        self.ui.load_recent_images_next.clicked.connect(self.next_image_precessing)
        self.ui.load_recent_images_previous.clicked.connect(self.previous_image_precessing)
        self.ui.comboBox_block_size.currentTextChanged.connect(lambda: self.image_processing_calibration(params_changed=True))
        self.ui.verticalSlider_noise.valueChanged[int].connect(lambda: self.image_processing_calibration(params_changed=True))
        self.ui.verticalSlider_defect.valueChanged[int].connect(lambda: self.image_processing_calibration(params_changed=True))
        self.ui.image_processing_save_btn.clicked.connect(partial(self.save_image_processing_parms))
        self.ui.calib_rotate_spinbox.valueChanged.connect(lambda: self.apply_calibration_on_image(self.ui.calibration_image))
        self.ui.calib_shifth_spinbox.valueChanged.connect(lambda: self.apply_calibration_on_image(self.ui.calibration_image))
        self.ui.calib_shiftw_spinbox.valueChanged.connect(lambda: self.apply_calibration_on_image(self.ui.calibration_image))
        self.ui.calib_save_params.clicked.connect(partial(self.save_changed_calibration_params))
        self.ui.calib_radio_corsshair.clicked.connect(partial(lambda: self.apply_calibration_on_image(self.ui.calibration_image)))
        self.ui.calib_radio_grid.clicked.connect(partial(lambda: self.apply_calibration_on_image(self.ui.calibration_image)))

        # general-settings
        self.ui.setting_color_comboBox.currentTextChanged.connect(lambda: mainsetting_funcs.update_combo_color(ui_obj=self.ui))
        self.ui.setting_fontstyle_comboBox.currentTextChanged.connect(lambda: mainsetting_funcs.update_combo_fontstyle(ui_obj=self.ui))
        self.ui.setting_fontsize_comboBox.currentTextChanged.connect(lambda: mainsetting_funcs.update_combo_fontsize(ui_obj=self.ui))
        self.ui.setting_appearance_apply_btn.clicked.connect(lambda: self.apply_changed_appearance_params(mode='appearance'))
        self.ui.setting_calibration_apply_btn.clicked.connect(lambda: self.apply_changed_appearance_params(mode='calibration'))
        self.ui.setting_imageprocessing_apply_btn.clicked.connect(lambda: self.apply_changed_appearance_params(mode='imageprocessing'))
        self.ui.setting_defects_apply_btn.clicked.connect(lambda: self.apply_changed_appearance_params(mode='defects'))
        self.ui.setting_multitsk_apply_btn.clicked.connect(lambda: self.apply_changed_appearance_params(mode='multitasking'))
        self.ui.side_general_setting_btn.clicked.connect(lambda: self.load_appearance_params_on_start(mainsetting_page=True))
        self.ui.general_setting_btn.clicked.connect(lambda: self.load_appearance_params_on_start(mainsetting_page=True))

        #PLC Setting
        self.ui.save_plc_ip_btn.clicked.connect(self.save_plc_ip)
        self.ui.connect_plc_btn.clicked.connect(self.connect_plc)
        self.ui.disconnect_plc_btn.clicked.connect(self.disconnect_plc)
        # self.ui.check_limitswitch_top_plc.clicked.connect(lambda: self.check_plc_parms(self.ui.check_limit_1_plc.objectName()))
        # self.ui.check_limitswitch_bottom_plc.clicked.connect(lambda: self.check_plc_parms(self.ui.check_limit_2_plc.objectName()))
        # self.ui.check_detect_sensor_plc.clicked.connect(lambda: self.check_plc_parms(self.ui.check_detect_sensor_plc.objectName()))
        self.ui.checkall_plc_btns.clicked.connect(self.check_all_plc_parms)
        self.ui.save_plc_pathes.clicked.connect(self.save_plc_parms)
        self.ui.comboBox_plc_addresses.currentTextChanged.connect(self.update_path_plc)
        self.ui.check_set_value_plc.clicked.connect(lambda: self.check_plc_parms(self.ui.check_set_value_plc.objectName()))
        self.ui.set_value_plc.clicked.connect(self.set_plc_value)
        self.ui.side_plc_setting_btn.clicked.connect(self.set_plc_ip_to_ui)
        self.ui.plc_setting_btn.clicked.connect(self.set_plc_ip_to_ui)
        
        # storage management page
        self.ui.side_storage_setting_btn.clicked.connect(self.refresh_storege_page)
        self.ui.storage_setting_btn.clicked.connect(self.refresh_storege_page)
        self.ui.cam_live_drive_apply_btn.clicked.connect(self.update_camera_live_storage_parms)
        self.ui.cam_live_drive_force_clear_btn.clicked.connect(self.force_clear_camera_live_storage)
        
        
        

    # dashboard page
    #------------------------------------------------------------------------------------------------------------------------
    # refresh summary informations on the dashboard page
    def refresh_dashboard_page(self):
        """
        this function is used to do some tasks that are related to dashboard page.
        the taks are almost the dashboard parameters 

        :returns: None
        """

        # camera summary
        camera_funcs.show_cameras_summary(ui_obj=self.ui)

        # calibration summary
        camera_funcs.show_calibration_summary(ui_obj=self.ui, db_obj=self.db)

        # plc summary
        self.update_plc_dashboard_parms()

        # storage summary
        storage_funcs.show_storage_status(ui_obj=self.ui, db_obj=self.db)

        # defects summary
        defect_management_funcs.show_defects_summary_info(ui_obj=self.ui, db_obj=self.db)

        # users summary
        user_management_funcs.show_users_summary_info(ui_obj=self.ui, db_obj=self.db)
        
    

    #------------------------------------------------------------------------------------------------------------------------   


    # camera functions in the camera setting page
    #------------------------------------------------------------------------------------------------------------------------   
    # # apply camera parameters to camera(s) (in database) on apply button click
    def save_changed_camera_params(self, apply_to_multiple=False):
        """
        save input camera parameters entered on UI camera setting page to database
        
        :param apply_to_multiple: a boolean determining wheter apply settings to multiple cameras or only current camera        
        :returns: None
        """
        
        # get camera-id and camera params from ui
        camera_id = camera_funcs.get_camera_id(self.ui.cameraname_label.text())
        camera_params = camera_funcs.get_camera_params_from_ui(ui_obj=self.ui)

        # validating camera parameters
        validate, message = camera_funcs.validate_camera_ip(ui_obj=self.ui, db_obj=self.db, camera_id=camera_id, camera_params=camera_params)
        if not validate:
            self.ui.show_mesagges(self.ui.camera_setting_message_label, message, level=1)
            return

        # set to database
        checkbox_values = camera_funcs.get_camera_checkbox_values(ui_obj=self.ui)

        # camera checkboxes are not checked, apply settings to only current camera
        if checkbox_values == 0 or apply_to_multiple: 
            res = camera_funcs.set_camera_params_to_db(db_obj=self.db, camera_id=camera_id, camera_params=camera_params, checkbox_values=checkbox_values)

            if res:
                self.ui.show_mesagges(self.ui.camera_setting_message_label, texts.MESSEGES['database_apply_camera_setting'][self.ui.language], level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_apply_camera_setting']['en'], level=1)
                self.notif_manager.create_new_notif(massage=texts.MESSEGES['database_apply_camera_setting'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            
            else:
                self.ui.show_mesagges(self.ui.camera_setting_message_label, texts.ERRORS['database_apply_camera_setting_failed'][self.ui.language], level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['database_apply_camera_setting_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_apply_camera_setting_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)

        # camera checkboxes are checked (apply settings to multiple cameras)
        # here, first a cofirm window is showned to confirm applieing to multiple cameras, if confirmed, apply them
        else: 
            if checkbox_values == 1: # apply to top cameras
                self.confirm_ui.msg_label.setText(texts.WARNINGS['camera_settings_apply_to_top'][self.ui.language])
            elif checkbox_values == 2: # apply to bottom cameras
                self.confirm_ui.msg_label.setText(texts.WARNINGS['camera_settings_apply_to_bottom'][self.ui.language])
            elif checkbox_values == 3: # apply to all cameras
                self.confirm_ui.msg_label.setText(texts.WARNINGS['camera_settings_apply_to_all'][self.ui.language])

            self.confirm_ui.show()


    # get cameras parameters from database given camera-id and apply to UI
    def load_camera_params_from_db_to_UI(self):
        """
        this function is used every time a camera is selected in camera settings page, and tries to load camera settings and
        parameters of that camera from database.
        at every camera selection, the previous camera will disconnected if it is connected

        :returns: None
        """
        
        # disconnect any camera if connected:
        if self.ui.camera_connect_flag:
            try:
                camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number='0', connect=False, current_cam_connection=self.camera_connection)
            except:
                self.ui.logger.create_new_log(message=texts.ERRORS['camera_disconnect_failed']['en'], level=5)
                return

            # update u elements on camera disconnect
            camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=False)

            if not self.ui.camera_setting_connect_btn.isEnabled():
                self.ui.camera_setting_connect_btn.setStyleSheet("background-color: {}; border: Transparent;".format(colors_pallete.disabled_btn))

        # get camera-id and get camera params from database
        camera_id = camera_funcs.get_camera_id(self.ui.cameraname_label.text())
        camera_params = camera_funcs.get_camera_params_from_db(db_obj=self.db, camera_id=camera_id)

        # set to UI
        if len(camera_params) != 0:
            self.ui.show_mesagges(self.ui.camera_setting_message_label, texts.MESSEGES['database_loade_camera_params'][self.ui.language], level=0)
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_loade_camera_params']['en'] + ' camera-id: ' + str(camera_id), level=1)
            camera_funcs.set_camera_params_to_ui(ui_obj=self.ui, db_obj=self.db, camera_params=camera_params, camera_id=camera_id, available_serials=self.available_camera_serials)

        # failed to load camera params from database  
        elif camera_id != '0':
            self.ui.logger.create_new_log(message=texts.ERRORS['database_loade_camera_params_failed']['en'] + ' camera-id: ' + str(camera_id), level=3)
            self.ui.show_mesagges(self.ui.camera_setting_message_label, texts.ERRORS['database_loade_camera_params_failed'][self.ui.language], level=2)

    
    # connect to cameras given entered serial number and camera parameters
    def connect_dissconnect_to_camera(self, calibration=False):
        """
        this functon is used to connect/disconnect to camera

        :param calibration: a boolean determining if the current page is calibration page
        :returns: None
        """
        
        # get camera parametrs on camera-settings page
        if not calibration:
            camera_serial_number = camera_funcs.get_camera_params_from_ui(ui_obj=self.ui)['serial_number']
        # get camera parametrs on calibration-settings page
        else:
            camera_id = self.ui.comboBox_cam_select_calibration.currentText()
            camera_serial_number = camera_funcs.get_camera_params_from_db(db_obj=self.db, camera_id=camera_id)['serial_number']

        # check if serial is assigned, if not, message to assign serial
        if camera_serial_number == '0':
            if not calibration:
                self.ui.show_mesagges(self.ui.camera_setting_message_label, texts.ERRORS['camera_no_serial_assigned'][self.ui.language], level=2)
            else:
                self.ui.show_mesagges(self.ui.camera_calibration_message_label, texts.ERRORS['camera_no_serial_assigned'][self.ui.language], level=2)
            
            return
        
        # serial is assigned to camera
        else:
            # connect to camera
            if not self.ui.camera_connect_flag:
                if not calibration:
                    self.camera_connection, message = camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number=camera_serial_number, connect=True, current_cam_connection=None)
                    
                    # failed to connect to camera
                    if self.camera_connection == None:
                        self.ui.show_mesagges(self.ui.camera_setting_message_label, message, level=2)
                        return
                    
                    # update ui elemnts on camera connect
                    camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=True)

                # calibration page
                else:
                    self.camera_connection, message = camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number=camera_serial_number, connect=True, current_cam_connection=None, calibration=True)
                    
                    # failed to connect to camera
                    if self.camera_connection == None:
                        self.ui.show_mesagges(self.ui.camera_setting_message_label, message, level=2)
                        return
                    
                    # update ui elemnts on camera connect
                    camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=True, calibration=True)


            # disconnect from camera
            else:
                if not calibration:
                    # dissconnect from cameras
                    camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number=camera_serial_number, connect=False, current_cam_connection=self.camera_connection)
                    # update ui elemnts on camera connect
                    camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=False)
                
                else:
                    # dissconnect from cameras
                    camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number=camera_serial_number, connect=False, current_cam_connection=self.camera_connection, calibration=True)
                    # update ui elemnts on camera connect
                    camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=False, calibration=True)


    # show cameras picture on UI
    def show_camera_picture(self, calibration=False):
        """
        this function is used to start image grabbing from camera, and update image on ui
        
        :param calibration: a boolean detrmining if current page is calibration or not
        :returns: None
        """
        
        # update ui elements
        camera_funcs.set_widjets_enable_or_disable(ui_obj=self.ui, api_obj=self, names=camera_funcs.calibration_params)
        self.pxcalibration_step = 0
        software_trig_flag = False
        #

        while True and self.ui.camera_connect_flag:
            # sotware trig mode
            if self.camera_connection.trigger == True and self.camera_connection.trigger_source == camera_funcs.TRIGGER_SOURCE[1]:
                try:
                    # soware trigg on camera
                    self.camera_connection.trigg_exec()
                    software_trig_flag = True

                except:
                    pass

            # get picture
            try:
                live_image = camera_funcs.get_picture_from_camera(self.camera_connection)

            except:
                self.ui.logger.create_new_log(message=texts.ERRORS['camera_get_picture_failed']['en'] + ' serial: ' + str(self.camera_connection.serial_number), level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['camera_get_picture_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                #
                return


            # set/show picture to UI
            if not calibration:
                camera_funcs.set_camera_picture_to_ui(ui_image_label=self.ui.camera_setting_picture_label, image=live_image)
            else:
                self.apply_calibration_on_image(live_image)
                #cameras.set_camera_picture_to_ui(ui_image_label=self.ui.calib_camera_image, image=live_image)

            cv2.waitKey(self.update_picture_delay) # must change

            # set/show picture to UI (calibration page)
            if calibration:
                self.ui.calibration_image = cv2.cvtColor(live_image, cv2.COLOR_BGR2GRAY)
                #
                if self.camera_connection.trigger == True:
                    if self.camera_connection.trigger_source == camera_funcs.TRIGGER_SOURCE[2]:
                        self.ui.calib_take_image.setEnabled(False)
                #
                    elif self.camera_connection.trigger_source == camera_funcs.TRIGGER_SOURCE[1] and not software_trig_flag:
                        self.ui.calib_take_image.setEnabled(False)
                #
                break


            # disable camera take picture botton in software or line1 trigger mode
            if self.camera_connection.trigger == True:
                if self.camera_connection.trigger_source == camera_funcs.TRIGGER_SOURCE[2]:
                    self.ui.camera_setting_getpic_btn.setEnabled(False)
                #
                elif self.camera_connection.trigger_source == camera_funcs.TRIGGER_SOURCE[1] and not software_trig_flag:
                    self.ui.camera_setting_getpic_btn.setEnabled(False)
                #
                break
        
        
    # disconnect camera on UI change
    def disconnect_camera_on_ui_change(self):
        """
        this function is used to disconnect camera if any of camera parameters in camera seting page are changed, or stackwidjet current page change

        :returns: None
        """
        
        if self.ui.camera_connect_flag:
            try:
                camera_funcs.connect_disconnect_camera(ui_obj=self.ui, db_pbj=self.db, serial_number='0', connect=False, current_cam_connection=self.camera_connection)
                camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=False)
                camera_funcs.update_ui_on_camera_connect_disconnect(ui_obj=self.ui, api_obj=self, connect=False, calibration=True)
                self.ui.camera_setting_connect_btn.setStyleSheet("background-color: {}; border:Transparent;".format(colors_pallete.disabled_btn))

            except:
                self.ui.logger.create_new_log(message=texts.ERRORS['camera_disconnect_failed']['en'], level=5)
                return
            #
            
            


    #------------------------------------------------------------------------------------------------------------------------
    

    # camera soft-calibration functions in the calibration setting page
    #------------------------------------------------------------------------------------------------------------------------
    # apply/set calibration image to UI
    def apply_calibration_on_image(self, image):
        """
        this function is used to apply soft-calibration on image and then update results on ui
        
        :param image: (_type_) input calibration image from camera
        :returns: None
        """
        try:
            # no image is available
            if image == None:
                self.ui.show_mesagges(self.ui.camera_calibration_message_label, texts.WARNINGS['camera_no_picture'][self.ui.language], level=1)
                return

        except:
            # select wheather apply or not soft-calibration to image
            camera_calibration_params = camera_funcs.get_camera_calibration_params_from_ui(ui_obj=self.ui)
            image = camera_funcs.apply_soft_calibrate_on_image(ui_obj=self.ui, image=image, camera_calibration_params=camera_calibration_params)

            # set image to UI
            if len(image.shape) == 3:
                image = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
            camera_funcs.set_camera_picture_to_ui(ui_image_label=self.ui.calib_camera_image, image=image)
        
            
    # set/save changed calibration parameters to database
    def save_changed_calibration_params(self):
        """
        this function is used to update camera calibration params to database.
        the input params are returned from ui
        
        :returns: None
        """
        # get camera-id from the camera-name lable in the camera settings section
        camera_id = camera_funcs.get_camera_id(self.ui.comboBox_cam_select_calibration.currentText())

        # get camera variable parameters from the camera settings section of the UI
        camera_params = camera_funcs.get_camera_calibration_params_from_ui(ui_obj=self.ui)

        # set to database
        res = self.db.update_cam_params(str(int(camera_id)), camera_params)

        # params updated on database
        if res:
            self.ui.show_mesagges(self.ui.camera_calibration_message_label, texts.MESSEGES['database_apply_camera_calibration_params'][self.ui.language], level=0)
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_apply_camera_calibration_params']['en'] + ' camera-id: ' + str(camera_id), level=1)
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['database_apply_camera_calibration_params'][self.ui.language],
                                                win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)

        # failed to update database
        else:
            self.ui.show_mesagges(self.ui.camera_calibration_message_label, texts.ERRORS['database_apply_camera_calibration_params_failed'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['database_apply_camera_calibration_params_failed']['en'] + ' camera-id: ' + str(camera_id), level=3)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['database_apply_camera_calibration_params_failed'][self.ui.language],
                                                win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)

    #------------------------------------------------------------------------------------------------------------------------


    # appearance parameters in the general-settings page
    #------------------------------------------------------------------------------------------------------------------------
    # apply user changed appearance parametrs in the general-setting to program and database
    def apply_changed_appearance_params(self, mode='appearance'):
        """
        this functino is used to apply returned setting parameters in setting page, to app/database
        according to mode. we can select which parameters to apply/set
        
        :param mode: (str, optional): it is used to select which parameters to apply/set. Defaults to 'appearance'.
                'appearance': apply appearance params like font, color or ...
                'calibration': apply calibration params
                'imageprocessing': apply image preprocessing parasms
                'multitasking':
                'defects':
        
        :returns: None
        """
        change_language_flag = False
        # get parameters from UI
        if mode == 'appearance':
            message_label = self.ui.general_setting_appearance_message_label
            params = mainsetting_funcs.get_appearance_params_from_ui(ui_obj=self.ui)

            # app language is changed 
            if (mainsetting_funcs.app_languages.index(params['language']) == 0 and self.ui.language != 'en') or (mainsetting_funcs.app_languages.index(params['language']) == 1 and self.ui.language != 'fa'):
                change_language_flag = True

            # apply appearance parameters to program
            self.win_color, self.font_size, self.font_style = mainsetting_funcs.apply_appearance_params_to_program(ui_obj=self.ui,
                                                                                                                    confirm_ui_obj=self.confirm_ui,
                                                                                                                    login_ui_object=self.login_ui,
                                                                                                                    appearance_params=params)
            #
        
        #
        elif mode == 'calibration':
            message_label = self.ui.general_setting_calibration_message_label
            params = mainsetting_funcs.get_calibration_params_from_ui(ui_obj=self.ui)
        #
        elif mode == 'imageprocessing':
            message_label = self.ui.setting_imageprocessing_message_label
            params = mainsetting_funcs.get_image_procesing_params_from_ui(ui_obj=self.ui)
        #
        elif mode == 'multitasking':
            message_label = self.ui.general_setting_mlttsk_message_label
            params = mainsetting_funcs.get_multitasking_params_from_ui(ui_obj=self.ui)
        #
        elif mode == 'defects':
            message_label = self.ui.setting_defect_message_label
            params = mainsetting_funcs.get_defects_params_from_ui(ui_obj=self.ui)

        # update database
        if mode == 'multitasking':
            res = mainsetting_funcs.set_mainsetting_params_to_db(db_obj=self.db, apperance_params=params, is_multitask_params=True)
        else:
            res = mainsetting_funcs.set_mainsetting_params_to_db(db_obj=self.db, apperance_params=params)

        # updated on database
        if res:
            self.ui.show_mesagges(message_label,texts.MESSEGES['mainsetting_applied'][self.ui.language], level=0)
            if mode == 'defects':
                defect_management_funcs.generate_defect_colors(db_obj=self.db)

        # failed to update dataabse
        else:
            self.ui.show_mesagges(message_label, texts.ERRORS['mainsetting_apply_failed'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['mainsetting_apply_failed']['en'], level=3)
        
        if change_language_flag:
            self.ui.translate_ui()
        

    # load appearance parameters from database on program start
    def load_appearance_params_on_start(self, mainsetting_page=False):
        """
        this function is used to load appearance params from database and apply to program on start-up or function call
        
        :param mainsetting_page: (bool, optional) a boolean determining wheather on mainsetting page or not. Defaults to False.
        :returns: None
        """

        # load from database
        try:
            apperance_params, multitask_params = mainsetting_funcs.get_mainsetting_params_from_db(db_obj=self.db)
        
        # database error
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_get_mainsettings_failed']['en'], level=5)
            return

        # apply to UI
        mainsetting_funcs.set_appearance_params_to_ui(ui_obj=self.ui, appearance_params=apperance_params, multitask_params=multitask_params)
        #
        if not mainsetting_page:
            self.win_color, self.font_size, self.font_style = mainsetting_funcs.apply_appearance_params_to_program(ui_obj=self.ui,
                                                                                                                    confirm_ui_obj=self.confirm_ui,
                                                                                                                    login_ui_object=self.login_ui,
                                                                                                                    appearance_params=apperance_params)

            defect_management_funcs.generate_defect_colors(db_obj=self.db)
        
    #------------------------------------------------------------------------------------------------------------------------


    # user Managment settings in the user management page
    #------------------------------------------------------------------------------------------------------------------------
    # get users from database and apply to users table
    def refresh_users_table(self):
        """
        this function is used to refresh users table on ui
        
        :returns: None
        """
        
        try:
            # get users list from database
            users_list = user_management_funcs.get_users_from_db(db_obj=self.db)
            # set users on ui table
            user_management_funcs.set_users_on_ui(ui_obj=self.ui, users_list=users_list)
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_laod_users_list']['en'], level=1)

        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_laod_users_list_failed']['en'], level=5)


    # remove user(s)
    def remove_users(self):
        """
        this function is used to remove selected users in ui users table, from database
        
        :returns: None
        """

        # get selected users from UI
        try:
            users_list = user_management_funcs.get_users_from_db(db_obj=self.db)
            selected_users = user_management_funcs.get_selected_users(ui_obj=self.ui, users_list=users_list)

        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_laod_users_list_failed']['en'], level=5)
            self.ui.show_mesagges(self.ui.create_user_message, texts.ERRORS['database_laod_users_list_failed'][self.ui.language], level=1)
            return

        # check not to remove admin users
        if add_default_database_records.default_username in selected_users:
            self.ui.show_mesagges(self.ui.create_user_message, texts.WARNINGS['admin_users_remove'][self.ui.language], level=2)
            return

        # check not to remove current logined user
        if self.ui.current_username_label.text() in selected_users:
            self.ui.show_mesagges(self.ui.create_user_message, texts.WARNINGS['current_user_remove'][self.ui.language], level=2)
            return

        # remove selected users from database
        try:
            res = user_management_funcs.remove_users_from_db(db_obj=self.db, users_list=selected_users)
            if not res:
                raise ValueError(texts.MESSEGES['users_removed']['en'])

            self.ui.logger.create_new_log(message=texts.MESSEGES['users_removed']['en'], level=1)
            self.ui.show_mesagges(self.ui.create_user_message, texts.MESSEGES['users_removed'][self.ui.language], level=0)
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['users_removed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)

        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['user_remove_failed']['en'], level=5)
            self.ui.show_mesagges(self.ui.create_user_message, texts.MESSEGES['user_remove_faled'][self.ui.language], level=2)

        # refresh table
        self.refresh_users_table() # must change add confirm btn and show message


    # add new user
    def add_user(self, default_user={}):
        """
        this function is used to add new user to database.
        the user info is returned from ui, and used as input to add to database

        :param default_user: (dict, optional) if not empty, this dict is use as input to add to database. if empty, new user_infoes are get
            from ui
        :returns: None
        """

        # get new user-info from UI
        try:
            if len(default_user) == 0:
                new_user_info = user_management_funcs.get_user_info_from_ui(ui_obj=self.ui)
            else:
                new_user_info = default_user

            ret, level = user_management_funcs.new_user_info_validation(db_obj=self.db, user_info=new_user_info, ui_obj=self.ui, default_user=len(default_user)>0)

        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['new_user_validate_faled']['en'], level=5)
            return

        # validation ok
        if ret == 'True':
            # add user to database
            try:
                # user added
                if user_management_funcs.add_new_user_to_db(db_obj=self.db, new_user_info=new_user_info) == 'True':
                    #
                    self.ui.show_mesagges(self.ui.create_user_message, texts.MESSEGES['new_user_created'][self.ui.language], level=0)
                    self.ui.logger.create_new_log(message=texts.MESSEGES['new_user_created']['en'], level=1)
                    self.notif_manager.create_new_notif(massage=texts.MESSEGES['new_user_created'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)

                    self.refresh_users_table()
                    #cv2.waitKey(self.waitkey) # must change
                    # move add-user window
                    #self.ui.animation_move(self.ui.frame_add_user, 300)
                    # clear new-user fields in UI
                    line_edits = [self.ui.user_id, self.ui.user_pass, self.ui.user_re_pass]
                    self.ui.clear_line_edits(line_edits)

                # failed to add user 
                else:
                    self.ui.show_mesagges(self.ui.create_user_message, texts.ERRORS['new_user_create_faled'][self.ui.language], level=3)
                    self.ui.logger.create_new_log(message=texts.ERRORS['new_user_create_faled']['en'], level=4)

            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['new_user_create_faled']['en'], level=5)

        # validation not ok
        else:
            self.ui.show_mesagges(self.ui.create_user_message, str(ret), level=level)

    #------------------------------------------------------------------------------------------------------------------------


    # other functions
    #------------------------------------------------------------------------------------------------------------------------      
    # function to connect the confirmation window yes button
    def confirm_yes(self):
        """
        this function is the event for confirm window yes button,
        accoarding to message of the confirm window, the function decides to take right action
        
        :returns: None
        """
        
        # user logout form
        if self.confirm_ui.msg_label.toPlainText() == texts.WARNINGS['logout_confirm_message'][self.ui.language]:
            # logout user
            user_login_logout_funcs.logout_user(ui_obj=self.ui, confirm_ui_obj=self.confirm_ui, login_api_obj=self.login_api)
            self.ui.current_username_label.setText(texts.WARNINGS['no_user_logged_in'][self.ui.language])
            # notif
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['user_logged_out'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)

        # apply setting to multiple cameras
        elif self.confirm_ui.msg_label.toPlainText() == texts.WARNINGS['camera_settings_apply_to_top'][self.ui.language]\
            or self.confirm_ui.msg_label.toPlainText() == texts.WARNINGS['camera_settings_apply_to_bottom'][self.ui.language]\
                or self.confirm_ui.msg_label.toPlainText() == texts.WARNINGS['camera_settings_apply_to_all'][self.ui.language]:
            #   
            self.save_changed_camera_params(apply_to_multiple=True)
            # close confirm window
            self.confirm_ui.close()

        # remove defect-group
        elif self.confirm_ui.msg_label.toPlainText() == texts.WARNINGS['remove_defect_group_containing_defects'][self.ui.language]:
            
            # remove defect-group
            res = defect_management_funcs.remove_defects_from_db(db_obj=self.db, defects_list=self.defect_group_id, defect_group=True)

            if res:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.MESSEGES['remove_defect_groups'][self.ui.language], level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['remove_defect_groups']['en'], level=1)
                self.notif_manager.create_new_notif(massage=texts.MESSEGES['remove_defect_groups'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            
            else:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['remove_defect_groups_failed'][self.ui.language], level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['remove_defect_groups_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['remove_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
            
            # remove defects with same defect-group from database
            res = defect_management_funcs.remove_defects_from_db(db_obj=self.db, defects_list=self.defect_group_id, defect_group_id=True)

            if res == True:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.MESSEGES['remove_defects'][self.ui.language], level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['remove_defects']['en'], level=1)
                self.notif_manager.create_new_notif(massage=texts.MESSEGES['remove_defects'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            
            else:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['remove_defects_failed'][self.ui.language], level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['remove_defects_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['remove_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
            
            # refresh table
            self.refresh_defects_table() # must change add confirm btn and show message
            # close confirm window
            self.confirm_ui.close()
            

    def things_to_do_on_stackwidject_change(self):
        """
        this function performs tasks needed to done on ui stackwidjet (page) change
       
        :returns: None
        """

        self.disconnect_camera_on_ui_change()
        self.edit_defect = False
        self.edit_defect_group = False

    
    def on_close_operations(self):
        """
        this function is used to check/do some functions before closing the app
        
        :returns: None
        """
        
        # dissconnect plc if it is connected
        try:
            self.disconnect_plc(on_close=True)
        except:
            pass

        # close app
        self.ui.close_win()

    #------------------------------------------------------------------------------------------------------------------------


    # Calibration Page detection alghorithm params
    #------------------------------------------------------------------------------------------------------------------------ 
    def select_image_procesing_directory(self):
        """
        this function is used to select image processing drectory contaiing images to fix image processing params with
        
        :returns: None
        """
        

        # check if live camera folder exists
        drive_info = storage_funcs.get_camera_live_drive_parameters_from_db(db_obj=self.db)
        dir_path = drive_info['camera_live_drive'] + '/' + drive_info['parent_path']

        try:
            if not os.path.exists(dir_path):
                self.ui.show_mesagges(self, self.ui.message_calibration, text=texts.WARNINGS['camera_live_folder_not_exists'][self.ui.language], level=1)
                return
            
            else:
                # open dialog to select directory contatiing images
                self.directorydialog = sQFileDialog(None, 'Select a directory containing images', dir_path)
                self.directorydialog.setFileMode(sQFileDialog.Directory)
                self.directorydialog.setOption(sQFileDialog.DontUseNativeDialog, True)
                self.directorydialog.setOption(sQFileDialog.ShowDirsOnly, False)
                selected = self.directorydialog.exec()

                #
                if selected:
                    directory_path = self.directorydialog.selectedFiles()[0]
                else:
                    directory_path = ''

                # check if any directory is selected
                if directory_path == '':
                    self.ui.show_mesagges(self.ui.message_calibration, text=texts.WARNINGS['no_directory_selected'][self.ui.language], level=1)
                    return

                # 
                self.control_list_image(input_img_path=directory_path)
                
        except:
            return
            

    def control_list_image(self, input_img_path):
        """
        this function is used to load image procesing directory contatiing images
        
        :type input_img_path: str
        :param input_img_path: inpput image directory
        :returns: None
        """

        # get images pathes
        input_img_path = load_recent_images.load_recent_images(input_img_path, image_count=10)   # load random last coil 3 images in path database
    
        # check if any image exists
        if len(input_img_path) == 0:
            # diactivate ui buttons
            self.ui.set_button_enable_or_disable(self.ui.image_processing_elements, enable=False)
            self.ui.show_mesagges(self.ui.message_calibration, texts.WARNINGS['no_picture_available_in_path'][self.ui.language], level=1)
            try:
                camera_funcs.set_camera_picture_to_ui(ui_image_label=self.ui.image_processing_image, image=cv2.imread('./images/no_image.png'))
            except:
                camera_funcs.set_camera_picture_to_ui(ui_image_label=self.ui.image_processing_image, image=np.zeros((500,500,3)).astype(np.uint8))

        else:
            self.ui.show_mesagges(self.ui.message_calibration, texts.MESSEGES['pictures_loaded_from_path'][self.ui.language], level=0)
            # active ui buttons
            self.ui.set_button_enable_or_disable(self.ui.image_processing_elements, enable=True)

            # load image processing params from database to ui
            try:
                image_procesing_params = self.db.get_image_processing_parms()
                self.ui.set_image_proccessing_parms_to_ui(image_procesing_params)
                self.ui.logger.create_new_log(message=texts.MESSEGES['load_image_processsing_params_from_database']['en'], level=1)

            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['load_image_processsing_params_from_database_failed']['en'], level=5)

            # crate image list object
            self.move_on_list.add(input_img_path, 'image_proccessing_path')
            # run image processing algo
            self.image_processing_calibration()

    
    def next_image_precessing(self):
        """
        this function is used to load next image for image processing calibration
        
        :returns: None
        """

        try:
            self.move_on_list.next_on_list('image_proccessing_path')
            self.image_processing_calibration()

        except:
            pass


    def previous_image_precessing(self):
        """
        this function is used to load prev image for image processing calibration
        
        :returns: None
        """

        try:
            self.move_on_list.next_on_list('image_proccessing_path')
            self.image_processing_calibration()

        except:
            pass

    
    def image_processing_calibration(self, params_changed=False):
        """
        this function is used to apply image processing algo on input image
        
        :param params_changed: (bool, optional) a boolean to detemine if algo params changed. Defaults to False.
        
        :returns: None
        """

        try:
            # get params from ui
            parms=self.ui.get_image_proccessing_parms()
            # get current image
            path=self.move_on_list.get_current('image_proccessing_path')
            # run algo
            output_img = SSI(path, parms['block_size'], parms['defect'], parms['noise'], parms['noise_flag'])
            # show output image on ui
            self.ui.set_image_label(self.ui.image_processing_image, output_img)

        except:
            if not params_changed:
                self.ui.show_mesagges(self.ui.message_calibration, texts.ERRORS['image_processing_algo_failed'][self.ui.language], level=2)


    def save_image_processing_parms(self):
        """
        this function is used to save image processing params from Miss.Abtahi algo to database
        
        :returns: None
        """

        parms = self.ui.get_image_proccessing_parms()
        # set on database
        res = self.db.set_image_processing_parms(parms)
        if res:
            self.ui.logger.create_new_log(message=texts.MESSEGES['update_image_processsing_params_on_database']['en'], level=1)
            self.ui.show_mesagges(self.ui.message_calibration, texts.MESSEGES['update_image_processsing_params_on_database'][self.ui.language], level=0)

        else:
            self.ui.logger.create_new_log(message=texts.ERRORS['update_image_processsing_params_on_database_failed']['en'], level=1)
            self.ui.show_mesagges(self.ui.message_calibration, texts.ERRORS['update_image_processsing_params_on_database_failed'][self.ui.language], level=2)


    #------------------------------------------------------------------------------------------------------------------------
    

    # defects Managment settings in the defect management page
    #------------------------------------------------------------------------------------------------------------------------
    # get defects from database and apply to defects table
    def refresh_defects_table(self, only_defects=False, only_defect_groups=False):
        """
        this function is used to refresh defect/defect-group tables from database to ui tables
    
        :param only_defects: a boolean determining only update defect table
        :param only_defect_groups: a boolean determining only update defect-groups table
        
        :returns: None
        """
        
        # update defects table
        if not only_defect_groups:
            try:
                defects_list = defect_management_funcs.get_defects_from_db(db_obj=self.db)

                if len(defects_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defects']['en'], level=1)

            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            # translate defect-group-ids to defect-group-name
            try:
                defects_list = defect_management_funcs.change_defect_group_id_to_name(db_obj=self.db, defects_list=defects_list)

            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['change_defect_id_to_name']['en'], level=5)

            #
            defect_management_funcs.set_defects_on_ui(ui_obj=self.ui, defects_list=defects_list)

        # update defect-groups table
        if not only_defects:
            try:
                defect_groups_list = defect_management_funcs.get_defects_from_db(db_obj=self.db, defect_groups=True)

                if len(defect_groups_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defect_groups']['en'], level=1)

            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return
            #
            defect_management_funcs.set_defect_groups_on_ui(ui_obj=self.ui, defect_groups_list=defect_groups_list)

            # set defect-groups list on defect-group combo
            defect_management_funcs.set_defect_groups_on_combo(ui_obj=self.ui, defect_groups_list=defect_groups_list)
            #
            defect_management_funcs.assign_existing_defect_colors_to_ui(ui_obj=self.ui, db_obj=self.db)

    
    # add new defect
    def add_defect(self, default_defect={}):
        """
        this function is used to add a new defect returned from ui to database.
        it is also used to add/update edited defect on dataabse
        
        :param default_defect: (dict, optional) if not empty, it is used as new defect to add to database,
            else the new defect info is returned from ui. Defaults to {}.
        :returns: None
        """

        line_edits = [self.ui.defect_name_lineedit, self.ui.defect_shortname_lineedit, self.ui.defect_id_lineedit]

        # not edited defect, a whole new defect
        if not self.edit_defect:
            # get new user-info from UI
            if len(default_defect) == 0:
                new_defect_info = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db)
            else:
                new_defect_info = default_defect

            
            if len(new_defect_info) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['ui_get_new_defect_info_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['ui_get_new_defect_info_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return
            #

            # validation
            ret = defect_management_funcs.new_defect_info_validation(ui_obj=self.ui, db_obj=self.db, defect_info=new_defect_info)
            
            # validation ok
            if ret[0] == 'True':
                # change defect-name to id
                try:
                    new_defect_info = defect_management_funcs.change_defect_group_id_to_name(db_obj=self.db, defects_list=new_defect_info, reverse=True)

                except Exception as e:
                    self.ui.logger.create_new_log(message=texts.ERRORS['change_defect_id_to_name']['en'], level=5)

                # add defect to database
                if defect_management_funcs.add_new_defect_to_db(db_obj=self.db, new_defect_info=new_defect_info) == 'True':
                    self.ui.show_mesagges(self.ui.create_defect_message, texts.MESSEGES['crate_new_defect'][self.ui.language], level=0)
                    self.ui.logger.create_new_log(message=texts.MESSEGES['crate_new_defect']['en'], level=1)
                    self.notif_manager.create_new_notif(massage=texts.MESSEGES['crate_new_defect'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                    #
                    self.refresh_defects_table()
                    cv2.waitKey(self.waitkey) # must change
                    # move add-defect window
                    #self.ui.animation_move(self.ui.frame_add_user, 300)
                    # clear new-defect fields in UI
                    self.ui.clear_line_edits(line_edits)

                # database error  
                else:
                    self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['crate_new_defect_failed'][self.ui.language], level=2)
                    self.ui.logger.create_new_log(message=texts.ERRORS['crate_new_defect_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['crate_new_defect_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    #

            # validation not ok        
            else:
                self.ui.show_mesagges(self.ui.create_defect_message, str(ret[0]), level=ret[1])


        # edit defect
        else:
            # get new user-info from UI
            new_defect_info = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db)

            if len(new_defect_info) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['ui_get_new_defect_info_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['ui_get_new_defect_info_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            #
            # validation
            ret = defect_management_funcs.new_defect_info_validation(ui_obj=self.ui, db_obj=self.db, defect_info=new_defect_info, on_edit=True)

            # vaildation ok
            if ret[0] == 'True':
                #
                
                if defect_management_funcs.update_defects_to_db(db_obj=self.db, defects_list=new_defect_info):
                    self.ui.show_mesagges(self.ui.create_defect_message, texts.MESSEGES['edit_defect'][self.ui.language], level=0) 
                    self.ui.logger.create_new_log(message=texts.MESSEGES['edit_defect']['en'], level=1)
                    self.notif_manager.create_new_notif(massage=texts.MESSEGES['edit_defect'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                
                # database error
                else:
                    self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['edit_defect_failed'][self.ui.language], level=2)
                    self.ui.logger.create_new_log(message=texts.ERRORS['edit_defect_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['edit_defect_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    #

                #
                self.edit_defect = False
                self.ui.defect_id_lineedit.setEnabled(True)
                self.ui.clear_line_edits(line_edits)
                self.refresh_defects_table()

            # validation not ok
            else:
                self.ui.show_mesagges(self.ui.create_defect_message, str(ret[0]), level=ret[1])
    

    # remove defect(s)
    def remove_defects(self, defect_group=False):
        """
        this function is used to remove selected defects/defect groups from database
        
        :param defect_group: (bool, optional) a boolean determining wheather to remove defect_groups or not. Defaults to False.
        :returns: None
        """

        # remove defects
        if not defect_group:
            # get defects from database
            try:
                defects_list = defect_management_funcs.get_defects_from_db(db_obj=self.db)

                # no defects returned from databse
                if len(defects_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                #
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defects']['en'], level=1)

            # failed to get defects from database     
            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return
            #

            # get selected defects from uI
            selected_defects = defect_management_funcs.get_selected_defects(ui_obj=self.ui, defects_list=defects_list)

            if len(selected_defects) > 1:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.WARNINGS['select_only_one_to_remove'][self.ui.language], level=1)
                return
            elif len(selected_defects) == 0:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.WARNINGS['no_selected_to_remove'][self.ui.language], level=1)
                return
            
            # default defect cant be removed, so check default defect not being in selected defects
            for s_defect in selected_defects:
                if s_defect[0] == add_default_database_records.default_defect_id:
                    self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['defect_cant_removed'][self.ui.language], level=2)
                    return

            # remove selected defects from database
            res = defect_management_funcs.remove_defects_from_db(db_obj=self.db, defects_list=selected_defects)
            
            if res == True:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.MESSEGES['remove_defects'][self.ui.language], level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['remove_defects']['en'], level=1)
                self.notif_manager.create_new_notif(massage=texts.MESSEGES['remove_defects'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            
            else:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['remove_defects_failed'][self.ui.language], level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['remove_defects_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['remove_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
            
        
        # remove defect-group
        else:
            # get defect-groups list from database
            try:
                defect_groups_list = defect_management_funcs.get_defects_from_db(db_obj=self.db, defect_groups=True)

                # no defect-groups returned from database
                if len(defect_groups_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defect_groups']['en'], level=1)
            
            # failed to get defect-groups from dataabse
            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            # get selected defect-groups from UI
            selected_defect_groups = defect_management_funcs.get_selected_defect_groups(ui_obj=self.ui, defect_groups_list=defect_groups_list)

            if len(selected_defect_groups) > 1:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['select_only_one_to_remove'][self.ui.language], level=1)
            elif len(selected_defect_groups) == 0:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['no_selected_to_remove'][self.ui.language], level=1)
            
            # default defect-group cant be removed, so check default defect-group not being in selected defect-group
            elif selected_defect_groups[0] == add_default_database_records.default_defectgroup_id:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['defect_group_cant_removed'][self.ui.language], level=2)


            else:
                # search if there is any defect with this group-id, if exists, notify user to remove the defects too
                res = defect_management_funcs.load_defects_from_db(db_obj=self.db, defect_id=selected_defect_groups, defect_group=False, defect_group_id=True)

                # confirm for delete defects related to selected defect-group
                if len(res) != 0:
                    self.defect_group_id = selected_defect_groups
                    self.confirm_ui.msg_label.setText(texts.WARNINGS['remove_defect_group_containing_defects'][self.ui.language])
                    self.confirm_ui.show()

                else:
                    # remove selected defect-group from database
                    res = defect_management_funcs.remove_defects_from_db(db_obj=self.db, defects_list=selected_defect_groups, defect_group=True)
                    
                    if res:
                        self.ui.show_mesagges(self.ui.create_defect_group_message, texts.MESSEGES['remove_defect_groups'][self.ui.language], level=0)
                        self.ui.logger.create_new_log(message=texts.MESSEGES['remove_defect_groups']['en'], level=1)
                        self.notif_manager.create_new_notif(massage=texts.MESSEGES['remove_defect_groups'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                   
                    else:
                        self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['remove_defect_groups_failed'][self.ui.language], level=2)
                        self.ui.logger.create_new_log(message=texts.ERRORS['remove_defect_groups_failed']['en'], level=3)
                        self.notif_manager.create_new_notif(massage=texts.ERRORS['remove_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    
        # refresh table
        self.refresh_defects_table() # must change add confirm btn and show message
    

    # edit defect
    def edit_defects(self, defect_group=False):
        """
        this function is used to edit selected defect/defect-group and change its parameters
        
        :param defect_group: (bool, optional) a boolean determining whather to edit defect-group. Defaults to False.
        :returns: None
        """

        # edit defect
        if not defect_group:
            # get defects list from database
            try:
                defects_list = defect_management_funcs.get_defects_from_db(db_obj=self.db)
                # failed to load defects from dataabse
                if len(defects_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defects']['en'], level=1)

            # failed to load defects from dataabse
            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            # get selected defects from ui defects table
            selected_defects = defect_management_funcs.get_selected_defects(ui_obj=self.ui, defects_list=defects_list)

            if len(selected_defects) > 1:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.WARNINGS['select_only_one_to_edit'][self.ui.language], level=1)
            elif len(selected_defects) == 0:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.WARNINGS['no_selected_to_edit'][self.ui.language], level=1)
            
            # cant edit default defect
            elif selected_defects[0] == add_default_database_records.default_defect_id:
                self.ui.show_mesagges(self.ui.create_defect_message, texts.ERRORS['defect_cant_edit'][self.ui.language], level=2)

            else:
                # load selected defect info from database
                defect_info = defect_management_funcs.load_defects_from_db(db_obj=self.db, defect_id=selected_defects)
                # database error
                if len(defect_info) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return

                # set defect info to UI for edit
                defect_management_funcs.set_defect_info_on_ui(ui_obj=self.ui, db_obj=self.db, defect_info=defect_info)

                # flag
                self.edit_defect = True
                self.ui.defect_id_lineedit.setEnabled(False)
                self.ui.logger.create_new_log(message=texts.MESSEGES['defect_on_edit']['en'], level=1)

        # edit defect-group
        else:
            # get defect-groups list from database
            defect_groups_list = defect_management_funcs.get_defects_from_db(db_obj=self.db, defect_groups=True)
            # database errro
            if len(defect_groups_list) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            # get selected defect groups from ui defect-groups table
            selected_defect_groups = defect_management_funcs.get_selected_defect_groups(ui_obj=self.ui, defect_groups_list=defect_groups_list)

            if len(selected_defect_groups) > 1:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['select_only_one_to_edit'][self.ui.language], level=1)
            elif len(selected_defect_groups) == 0:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['no_selected_to_edit'][self.ui.language], level=1)

            # cant edit default defect-group-id
            elif selected_defect_groups[0] == add_default_database_records.default_defectgroup_id:
                self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['defect_group_cant_edit'][self.ui.language], level=2)
                
            else:
                # load selected defect info from database
                defect_group_info = defect_management_funcs.load_defects_from_db(db_obj=self.db, defect_id=selected_defect_groups, defect_group=True)

                # database error
                if len(defect_group_info) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return

                # set to UI for edit
                defect_management_funcs.set_defect_group_info_on_ui(ui_obj=self.ui, defect_group_info=defect_group_info)

                # flag
                self.edit_defect_group = True
                self.ui.defect_group_id_lineedit.setEnabled(False)
                self.ui.logger.create_new_log(message=texts.MESSEGES['defect_group_on_edit']['en'], level=1)
    

    # edit defect
    def show_related_defects(self):
        """
        this function is used to show related defects to a selected defect-group
        
        
        :returns: None
        """

        # get defects-groups from database
        try:
            defect_groups_list = defect_management_funcs.get_defects_from_db(db_obj=self.db, defect_groups=True)

            # database error
            if len(defect_groups_list) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=4)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defect_groups']['en'], level=1)

        # database error
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=5)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
            return

        # get selected defect-groups from database
        selected_defect_groups = defect_management_funcs.get_selected_defect_groups(ui_obj=self.ui, defect_groups_list=defect_groups_list)
        
        if len(selected_defect_groups) > 1:
            self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['select_only_one_to_remove'][self.ui.language], level=1)
        elif len(selected_defect_groups) == 0:
            self.ui.show_mesagges(self.ui.create_defect_group_message, texts.WARNINGS['no_selected_to_remove'][self.ui.language], level=1)

        else:
            # load selected defect group-id from database
            defect_group_info = defect_management_funcs.load_defects_from_db(db_obj=self.db, defect_id=selected_defect_groups, defect_group=True)['defect_group_name']

            # database error
            if len(defect_group_info) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defect_groups_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defect_groups_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            # get defects from db
            try:
                defects_list = defect_management_funcs.get_defects_from_db(db_obj=self.db)

                # database error
                if len(defects_list) == 0:
                    self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=4)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    return
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_load_defects']['en'], level=1)
            
            # database error
            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['database_load_defects_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_load_defects_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            try:
                defects_list = defect_management_funcs.change_defect_group_id_to_name(db_obj=self.db, defects_list=defects_list)
            except Exception as e:
                self.ui.logger.create_new_log(message=texts.ERRORS['change_defect_id_to_name']['en'], level=5)
            #

            # set defects on defect table in UI, while highlighting defects related to selected defect-group
            defect_management_funcs.set_defects_on_ui(ui_obj=self.ui, defects_list=defects_list, defect_group_name=defect_group_info)
    

    def filter_defects(self, defect_group=False):
        """
        this function is used to filter/search in defect table
        
        :param defect_group: (bool, optional) a boolean determining whather to search in defect-groups. Defaults to False.
        :returns: None
        """

        # search/filter defects
        if not defect_group:
            filter_params = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db, is_filter=True)
            res = defect_management_funcs.get_filtered_defects_from_db(db_obj=self.db, filter_params=filter_params)

            if res[0] == 'all':
                self.refresh_defects_table(only_defects=True)
                
            else:
                defects_list = defect_management_funcs.change_defect_group_id_to_name(db_obj=self.db, defects_list=res[1])
                defect_management_funcs.set_defects_on_ui(ui_obj=self.ui, defects_list=defects_list)

        # search/filter defect-group
        else:
            filter_params = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db, is_filter=True, defect_group=True)
            res = defect_management_funcs.get_filtered_defects_from_db(db_obj=self.db, filter_params=filter_params, defect_groups=True)

            if res[0] == 'all':
                self.refresh_defects_table(only_defect_groups=True)
            else:
                #print(res)
                defect_management_funcs.set_defect_groups_on_ui(ui_obj=self.ui, defect_groups_list=res[1])

    
    # sort defect table by column
    def tabledefects_onHeaderClicked(self, logicalIndex):
        """
        this function is used to sort items accoading to one column, if clicked on that column
        
        :param logicalIndex: (_type_) _description_
        :returns: None
        """
        if logicalIndex != 6:
            self.ui.tableWidget_defects.sortItems(logicalIndex, sQtCore.Qt.AscendingOrder)
            

    # sort defect-group table by column   
    def tabledefectgroups_onHeaderClicked(self, logicalIndex):
        """
        this function is used to sort items accoading to one column, if clicked on that column
        
        :param logicalIndex: (_type_) _description_
        :returns: None
        """

        self.ui.tableWidget_defectgroups.sortItems(logicalIndex, sQtCore.Qt.AscendingOrder)

    #------------------------------------------------------------------------------------------------------------------------


    # defect-groups Managment settings in the defect management page
    #------------------------------------------------------------------------------------------------------------------------    
    # add new defect-group
    def add_defect_group(self, default_defectgroup={}):
        """
        this function is used to add a defect group returned from ui/user to database. 
        
        :param default_defectgroup: (dict, optional) if not empty, it is used as input to add to database
            if not, the info returned from ui is used. Defaults to {}.
        
        :returns: None
        """

        line_edits = [self.ui.defect_group_name_lineedit, self.ui.defect_group_id_lineedit]

        # not in edit/mode, add a whole new record
        if not self.edit_defect_group:

            # get new user-info from UI
            if len(default_defectgroup) == 0:
                new_defect_group_info = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db, defect_group=True)
            else:
                new_defect_group_info = default_defectgroup

            if len(new_defect_group_info) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['ui_get_new_defect_group_info_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['ui_get_new_defect_group_info_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return
            #

            # validation
            ret = defect_management_funcs.new_defect_info_validation(ui_obj=self.ui, db_obj=self.db, defect_info=new_defect_group_info, defect_group=True)

            # validation ok
            if ret[0] == 'True':
                # add defect to database
                if defect_management_funcs.add_new_defect_to_db(db_obj=self.db, new_defect_info=new_defect_group_info, defect_group=True) == 'True':
                    self.ui.show_mesagges(self.ui.create_defect_group_message, texts.MESSEGES['crate_new_defect_group'][self.ui.language], level=0)
                    self.ui.logger.create_new_log(message=texts.MESSEGES['crate_new_defect_group']['en'], level=1)
                    self.notif_manager.create_new_notif(massage=texts.MESSEGES['crate_new_defect_group'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                    #
                    self.refresh_defects_table()
                    cv2.waitKey(self.waitkey) # must change
                    # move add-defect window
                    #self.ui.animation_move(self.ui.frame_add_user, 300)
                    # clear new-defect fields in UI
                    self.ui.clear_line_edits(line_edits)

                # database error   
                else:
                    self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['crate_new_defect_group_failed'][self.ui.language], level=2)
                    self.ui.logger.create_new_log(message=texts.ERRORS['crate_new_defect_group_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['crate_new_defect_group_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    #

            # validation not ok   
            else:
                self.ui.show_mesagges(self.ui.create_defect_group_message, str(ret[0]), level=ret[1])


        # edit an existing defect-group
        else:
            # get new user-info from UI
            new_defect_group_info = defect_management_funcs.get_defect_info_from_ui(ui_obj=self.ui, db_obj=self.db, defect_group=True)

            if len(new_defect_group_info) == 0:
                self.ui.logger.create_new_log(message=texts.ERRORS['ui_get_new_defect_group_info_failed']['en'], level=5)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['ui_get_new_defect_group_info_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

            #
            # validation
            ret = defect_management_funcs.new_defect_info_validation(ui_obj=self.ui, db_obj=self.db, defect_info=new_defect_group_info, on_edit=True, defect_group=True)

            # validation ok
            if ret[0] == 'True':
                #
                if defect_management_funcs.update_defects_to_db(db_obj=self.db, defects_list=new_defect_group_info, defect_group=True):
                    self.ui.show_mesagges(self.ui.create_defect_group_message, texts.MESSEGES['edit_defect_group'][self.ui.language], level=0) 
                    self.ui.logger.create_new_log(message=texts.MESSEGES['edit_defect_group']['en'], level=1)
                    self.notif_manager.create_new_notif(massage=texts.MESSEGES['edit_defect_group'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                    #

                # failed to update on database  
                else:
                    self.ui.show_mesagges(self.ui.create_defect_group_message, texts.ERRORS['edit_defect_group_failed'][self.ui.language], level=2)
                    self.ui.logger.create_new_log(message=texts.ERRORS['edit_defect_group_failed']['en'], level=3)
                    self.notif_manager.create_new_notif(massage=texts.ERRORS['edit_defect_group_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                    #

                self.edit_defect_group = False
                self.ui.defect_group_id_lineedit.setEnabled(True)
                self.ui.clear_line_edits(line_edits)
                self.refresh_defects_table()

            else:
                self.ui.show_mesagges(self.ui.create_defect_group_message, str(ret[0]), level=ret[1])


    
    # storage management page
    #_______________________________________________________________________________________________________________
    def run_storage_check_timer(self, storage_check_interval=60, stop=False):
        """
        this function is used to initailize and run timer for checking storage statues
        
        :param storage_check_interval: (int, optional) check interval (in seconds). Defaults to 60.
        :param stop: (bool, optional) a boolean determining to stop the timer. Defaults to False.
        :returns: None
        """

        # stop timer if exists
        if stop:
            try:
                self.camera_live_storage_check_timer.stop()
                self.ui.logger.create_new_log(message=texts.MESSEGES['stop_storage_check_timer']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['stop_storage_check_timer'][self.ui.language],
                                                win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            #  
            except:
                pass
            #
            return

        # intialize timer by check interval
        # stop last timer first (if exists), then start timer with new nterval
        try:
            self.camera_live_storage_check_timer.stop()
        except:
            pass
        #
        try:
            self.camera_live_storage_check_timer = sQtCore.QTimer()
            self.camera_live_storage_check_timer.timeout.connect(self.check_storage_status)
            self.camera_live_storage_check_timer.start(storage_check_interval*1000)
            self.ui.logger.create_new_log(message=texts.MESSEGES['initialize_storage_check_timer']['en'] + ', interval: %s (s)' % (storage_check_interval), level=1)
            
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['initialize_storage_check_timer_failed']['en'], level=3)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['initialize_storage_check_timer_failed'][self.ui.language],
                                                win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)


    def refresh_storege_page(self, only_chart=False):
        """
        this function is used to refresh storage page
        
        :param only_chart: (bool, optional) if true, only the storage chart is updated. Defaults to False.
        """
        if not only_chart:
            storage_funcs.update_camera_live_drive_combo(ui_obj=self.ui, available_drives=None)

        # get current drive for saving camera lives from db
        drive_infos = storage_funcs.get_camera_live_drive_parameters_from_db(db_obj=self.db)

        if not only_chart:
            # set to ui combo
            self.ui.cam_live_drive_combo.setCurrentText(drive_infos['camera_live_drive'] if drive_infos['camera_live_drive']!='NULL' else 'No Drive')
            self.ui.cam_live_drive_thrs_spin.setValue(drive_infos['live_drive_max_used_ratio'])
            self.ui.cam_live_drive_thrs_spin_2.setValue(drive_infos['live_drive_remove_stop_ratio'])

        # update bar chart for drive status
        drives_info = []
        for drive_path in storage_funcs.get_available_drives():
            drives_info.append(storage_funcs.get_storage_status(disk_path=drive_path))
        #
        chart_funcs.update_drive_barchart(ui_obj=self.ui, drives_info=drives_info, storage_thrs=drive_infos['live_drive_max_used_ratio'], warn_storage_thrs=drive_infos['live_drive_remove_stop_ratio'])

    
    #
    def update_camera_live_storage_parms(self):
        """
        this function is used to update/set defalt storage params returned from ui, to database
        
        :returns: None
        """

        # get drive params from ui
        res, drive_infos, storage_check_interval = storage_funcs.get_camera_live_drive_parameters_from_ui(ui_obj=self.ui)

        if res:
            # update database
            res = storage_funcs.set_camera_live_drive_parameters_to_db(db_obj=self.db, drive_infos=drive_infos)

            #
            if res:
                self.ui.show_mesagges(self.ui.cam_live_drive_label, texts.MESSEGES['camera_live_drive_params_applied'][self.ui.language], level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['camera_live_drive_params_applied']['en'], level=1)

                #
                try:
                    # update storage check nterval on app start-up json
                    self.ui.start_up_settings.update({storage_funcs.storage_check_interval_key: storage_check_interval})
                    # save json
                    with open(setting_UI.app_startup_json_path, 'w') as f:
                        json.dump(self.ui.start_up_settings, f , indent=4, sort_keys=True)
                    f.close()

                    # re-run storage check timer (maybe time interval be changed)
                    self.run_storage_check_timer(storage_check_interval=storage_check_interval)
                    self.ui.logger.create_new_log(message=texts.MESSEGES['storage_check_interval_changed']['en'] + 'to: %s (s)' % (str(storage_check_interval)), level=1)

                # failed to re-run stirage check
                except:
                    self.ui.logger.create_new_log(message=texts.WARNINGS['storage_check_interval_change_failed']['en'], level=2)
                #
                
            # database error
            else:
                self.ui.show_mesagges(self.ui.cam_live_drive_label, texts.ERRORS['database_camera_live_drive_params_appliy_failed'][self.ui.language], level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['database_camera_live_drive_params_appliy_failed']['en'], level=3)
            #

            self.refresh_storege_page()
            
            # create folder to save camera live images
            drive_info = storage_funcs.get_camera_live_drive_parameters_from_db(db_obj=self.db)
            dir_path = drive_info['camera_live_drive'] + '/' + drive_info['parent_path']
            try:
                if not os.path.exists(dir_path):
                    os.mkdir(dir_path)

            except:
                pass


    # check storage
    def check_storage_status(self):
        """
        this function is used to check storage statues
        
        :returns: None
        """

        # get current drive infoes
        try:
            drive_info = storage_funcs.get_camera_live_drive_parameters_from_db(db_obj=self.db)

            # database erro
            if len(drive_info) == 0:
                self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.ERRORS['database_get_drive_infoes_failed']['en'], level=2, clearable=False)
                self.ui.logger.create_new_log(message=texts.ERRORS['database_get_drive_infoes_failed']['en'], level=3)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_get_drive_infoes_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                return

        # database erro
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_get_drive_infoes_failed']['en'], level=5)
            return

        if drive_info['live_drive_max_used_ratio'] > 1:
            drive_info['live_drive_max_used_ratio'] /= 100
        if drive_info['live_drive_remove_stop_ratio']:
            drive_info['live_drive_remove_stop_ratio'] /= 100

        try:
            if drive_info['camera_live_drive'] in storage_funcs.get_available_drives():
                # drive space
                drive_space_info = storage_funcs.get_storage_status(disk_path=drive_info['camera_live_drive'])

                # live images directory path
                dir_path = drive_info['camera_live_drive'] + '/' + drive_info['parent_path']

                # remove old files if needed
                if drive_space_info['used_perc'] >= drive_info['live_drive_max_used_ratio']:
                    self.ui.show_mesagges(self.ui.curr_used_space_label, str(int(drive_space_info['used_perc']*100)), level=2, clearable=False, prefix=False)

                elif drive_space_info['used_perc'] > (drive_info['live_drive_remove_stop_ratio']+drive_info['live_drive_max_used_ratio'])/2:
                    self.ui.show_mesagges(self.ui.curr_used_space_label, str(int(drive_space_info['used_perc']*100)), level=1, clearable=False, prefix=False)

                else:
                    self.ui.show_mesagges(self.ui.curr_used_space_label, str(int(drive_space_info['used_perc']*100)), level=0, clearable=False, prefix=False)


                # clear storage if usage higher than threshold, or force clear button is pressed on ui
                if (drive_space_info['used_perc'] > drive_info['live_drive_max_used_ratio'] or self.force_clear) and not self.camera_live_storage_check_thread_lock:
                    #
                    self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.WARNINGS['clear_storage'][self.ui.language], level=1, clearable=False)

                    # notification
                    if len(storage_funcs.get_files_in_path(dir_path=dir_path, reverse=False)) > 0:

                        self.notif_manager.create_new_notif(massage=texts.WARNINGS['clear_storage'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=1)
                        self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.WARNINGS['clear_storage'][self.ui.language], level=1, clearable=False)
                        self.ui.logger.create_new_log(message=texts.WARNINGS['clear_storage']['en'], level=2)
                        #
                        # lock the thread for clearing storage until finish clearing storage, this is for preventing to
                        # run more than one thread 
                        self.camera_live_storage_check_thread_lock = True
                        self.camera_live_storage_check_thread = threading.Thread(target=storage_funcs.remove_old_files_in_directory, args=(self,
                                                                                                                                            self.ui,
                                                                                                                                            drive_info['camera_live_drive'],
                                                                                                                                            dir_path,
                                                                                                                                            drive_info['live_drive_max_used_ratio'],
                                                                                                                                            drive_info['live_drive_remove_stop_ratio'],False,))
                        self.camera_live_storage_check_thread.start()

                    # drive fulled with other files rather than camera images
                    else:
                        self.notif_manager.create_new_notif(massage=texts.WARNINGS['drive_fulled_with_other_content'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                        self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.WARNINGS['drive_fulled_with_other_content'][self.ui.language], level=2, clearable=False)
                        self.ui.logger.create_new_log(message=texts.WARNINGS['drive_fulled_with_other_content']['en'], level=3)
                        

                # storage statues ok   
                elif not self.camera_live_storage_check_thread_lock:
                    self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.MESSEGES['storage_ok'][self.ui.language], clearable=False, level=0)
                    # notification
                    try:
                        if self.camera_live_storage_clear_flag:
                            self.notif_manager.create_new_notif(massage=texts.MESSEGES['storage_cleared'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                            self.ui.logger.create_new_log(message=texts.MESSEGES['storage_cleared']['en'], level=1)
                            self.camera_live_storage_clear_flag = False
                    except:
                        pass
        
        # failed to check storage statues
        except:
            self.ui.logger.create_new_log(message=texts.ERRORS['storage_clear_check_failed']['en'], level=5)
            self.ui.show_mesagges(self.ui.cam_live_drive_label_2, texts.ERRORS['storage_clear_check_failed']['en'], level=2, clearable=False)

        self.force_clear = False
        if self.ui.stackedWidget.currentWidget() == self.ui.page_storage:
            self.refresh_storege_page(only_chart=True)
        

    #
    def force_clear_camera_live_storage(self):
        """
        this function is used to makes True the flag for force clearing storage
        
        :returns: None
        """

        self.force_clear = True
        
        
        
    # -----------------------------------------------------PLC setting -------------------------------------------------------

    def connect_plc(self):
        """
        this function is used to connect to plc
        
        :returns: None
        """

        # get plc ip
        ip = self.ui.get_plc_ip()

        # connect to plc
        self.my_plc = plc_managment.management(ip, ui_obj=self.ui)
        self.connection_status = self.my_plc.connection()

        #
        if self.connection_status:
            res = self.load_plc_parms()
            if not res:
                self.ui.show_mesagges(self.ui.plc_warnings, texts.ERRORS['database_get_plc_params_failed'][self.ui.language], level=2)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['database_get_plc_params_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['database_get_plc_params_failed']['en'], level=3)
                return
            else:
                self.ui.show_mesagges(self.ui.plc_warnings, texts.MESSEGES['database_get_plc_params'][self.ui.language], level=0)
                self.notif_manager.create_new_notif(massage=texts.MESSEGES['database_get_plc_params'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
                self.ui.logger.create_new_log(message=texts.MESSEGES['database_get_plc_params']['en'], level=1)
            #
            self.ui.set_size(self.ui.frame_121, 800,maximum=True)
            self.ui.show_mesagges(self.ui.plc_warnings, texts.MESSEGES['plc_connection_apply'][self.ui.language], level=0)
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['plc_connection_apply'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            self.ui.logger.create_new_log(message=texts.MESSEGES['plc_connection_apply']['en'], level=1)
            self.plc_connection_status=True
            self.ui.disconnect_plc_btn.setEnabled(True)
            self.ui.connect_plc_btn.setEnabled(False)

            # timer to update plc params
            self.timer_write_plc= sQtCore.QTimer()
            self.timer_write_plc.timeout.connect(self.write_parms)
            self.timer_write_plc.start(5000)

        else:
            self.ui.set_size(self.ui.frame_121, 0,maximum=True)
            self.ui.show_mesagges(self.ui.plc_warnings, texts.ERRORS['plc_connection_apply_failed'][self.ui.language], level=2)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['plc_connection_apply_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['plc_connection_apply_failed']['en'], level=4)
        
        

    
    def disconnect_plc(self, on_close=False):
        """
        this function is used to disconnect from plc 
        
        :param on_close: (bool, optional) a boolean deermining if function is called on app close. Defaults to False.
        """

        try:
            self.my_plc.disconnect()
            self.timer_write_plc.stop()
            self.plc_connection_status = False
            del self.my_plc
            #
            self.ui.show_mesagges(self.ui.plc_warnings, texts.MESSEGES['plc_disconnected'][self.ui.language], level=0)
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['plc_disconnected'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)
            self.ui.logger.create_new_log(message=texts.MESSEGES['plc_disconnected']['en'], level=1)
            #
            self.ui.disconnect_plc_btn.setEnabled(False)
            self.ui.connect_plc_btn.setEnabled(True)

        # failed to disconnect plc
        except:
            if not on_close:
                self.ui.show_mesagges(self.ui.plc_warnings, texts.ERRORS['plc_disconnected_failed'][self.ui.language], level=2)
                self.notif_manager.create_new_notif(massage=texts.ERRORS['plc_disconnected_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)
                self.ui.logger.create_new_log(message=texts.ERRORS['plc_disconnected_failed']['en'], level=3)
        
        #
        self.ui.set_size(self.ui.frame_121, 0,maximum=True)
        
    
    def check_all_plc_parms(self):
        """
        this function is used to check all plc logic pathes values
        
        :returns: values: a dict of plc values
        """
        values={}

        #
        for btn in self.ui.PLC_btns:
            value = self.check_plc_parms(btn)
            values.update({btn:value})

        return values


    def check_plc_parms(self, name):
        """
        this function is used to check/get value of a path on plc
        
        :param name: (_type_) check botton name of the path
        :returns: value: value stored in path
        """
        # path_list={'check_limit_1_btn':self.ui.line_limit1_plc,'check_limit_2_btn':self.ui.line_limit2_plc,\
        #     'check_top_motor_btn':self.ui.line_top_motor_plc,'check_down_motor_btn':self.ui.line_down_motor_plc,\
        #         'line_detect_sensor_plc':self.ui.line_detect_sensor_plc}

        name = name.split('_', 1)[1]
        path = eval('self.ui.line_{}.text()'.format(name))
        # print('path',path)
        value=self.my_plc.get_value(path)
        # print('value',value)
        value_label_name = eval('self.ui.label_{}'.format(name))
        datavalue_label_name = eval('self.ui.label_{}_2'.format(name))


        if value[0] != '-':
            self.ui.show_mesagges(value_label_name, str(value[0]), level=0, clearable=False)
            self.ui.show_mesagges(datavalue_label_name, str(value[1]), level=0, clearable=False)

        # failed to get value
        else:
            self.ui.show_mesagges(value_label_name, 'None', level=2, clearable=False, prefix=False)
            self.ui.show_mesagges(datavalue_label_name, str(value[1]), level=2, clearable=False)

        return value[0]


    def load_plc_parms(self):
        """
        this function is used to load plc params from database, and set to ui plc page
        
        :returns: resault: a boolean determining if params loaded from database
        """

        parms=self.db.load_plc_parms()

        if parms == None:
            return False

        combo_list=[]
        for parm in parms:
            try:
                
                line = eval('self.ui.line_{}'.format(parm['name']))
                line.setText(parm['path'])

                # set values
                try:
                    eval('self.ui.value0_{}'.format(parm['name'])).setText(str(parm['min_or_off_value']))
                    eval('self.ui.value1_{}'.format(parm['name'])).setText(str(parm['max_or_on_value']))
                except:
                    pass

                combo_list.append(parm['name'])

            #
            except:
                return False
        #
        self.parms = parms
        # update combo
        self.ui.comboBox_plc_addresses.clear()
        self.ui.comboBox_plc_addresses.addItems(combo_list)
        
        return True
        

    def update_path_plc(self):
        """
        this function is used to get value of a path on plc, everytime pathes-combobox has changed
        
        :returns: None
        """

        try:
            text=self.ui.comboBox_plc_addresses.currentText()
            value=eval('self.ui.line_{}.text()'.format(text))
            self.ui.line_set_value_plc.setText(value)

        except:
            pass


    def save_plc_parms(self):
        """
        this function is used to save plc params to database
        
        :returns: None
        """

        plc_parms = self.ui.get_plc_parms()
        #print(plc_parms)
        #
        res = self.db.update_plc_parms(plc_parms)

        if not res:
            self.ui.logger.create_new_log(message=texts.ERRORS['database_update_plc_params_failed']['en'], level=3)
            self.ui.show_mesagges(self.ui.plc_statues_label, texts.ERRORS['database_update_plc_params_failed'][self.ui.language], level=2)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['database_update_plc_params_failed'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)  # For big Change in plc we show a notif

        # database error
        else:
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_update_plc_params']['en'], level=1)
            self.ui.show_mesagges(self.ui.plc_statues_label, texts.MESSEGES['database_update_plc_params'][self.ui.language], level=0)
            self.notif_manager.create_new_notif(massage=texts.MESSEGES['database_update_plc_params'][self.ui.language], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=0)  # For big Change in plc we show a notif


    def set_plc_value(self):
        """
        this function is used to update/set a path calue on plc
        
        :returns: None
        """

        # print('set')
        path=self.ui.line_set_value_plc.text()
        value=self.ui.line_value_set_value_plc.text()
        message = ', path:' + str(path) + ', value:' + str(value)

        try:
            self.my_plc.set_value(path, value)
            self.ui.logger.create_new_log(message=texts.MESSEGES['plc_set_value']['en'] + message, level=1)
            self.ui.show_mesagges(self.ui.label_set_value_plc_res, texts.MESSEGES['plc_set_value'][self.ui.language] + message, level=0)
            
        # failed to set value
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.ERRORS['plc_set_value_failed']['en'] + message, level=5)
            self.ui.show_mesagges(self.ui.label_set_value_plc_res, texts.ERRORS['plc_set_value_failed'][self.ui.language] + message, level=2)


    def save_plc_ip(self):
        """
        this function is used to get plc ip from ui and update on database
        
        :returns: None
        """

        ip = self.ui.get_plc_ip()
        #
        res = self.db.update_plc_ip(ip)

        if not res:
            self.ui.show_mesagges(self.ui.plc_warnings, texts.ERRORS['database_set_plc_ip_failed'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['database_set_plc_ip_failed']['en'], level=4)
        
        # database error
        else:
            self.ui.show_mesagges(self.ui.plc_warnings, texts.MESSEGES['database_set_plc_ip'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_set_plc_ip']['en'], level=4)
            

    def set_plc_ip_to_ui(self):
        """
        this function is used to get plc ip from database and set to ui
        
        :returns: None
        """

        ip = self.db.load_plc_ip()

        # failed to get ip from database
        if not ip:
            #self.ui.show_mesagges(self.ui.plc_warnings, texts.ERRORS['database_get_plc_ip_failed'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['database_get_plc_ip_failed']['en'], level=4)
            return
        #
        else:
            self.ui.logger.create_new_log(message=texts.MESSEGES['database_get_plc_ip']['en'], level=1)
            self.ui.set_plc_ip(ip)


    def update_plc_dashboard_parms(self):
        """
        this function is used to update plc summary satues on dashboard
        
        :returns: None
        """

        try:
            # pass
            if self.plc_connection_status:
                # text=
                self.ui.show_mesagges(self.ui.plc_status_dashboard, text=texts.Titles['Connected'][self.ui.language], level=0, clearable=False, prefix=False)

            else:
                self.ui.show_mesagges(self.ui.plc_status_dashboard, text=texts.Titles['Disconnected'][self.ui.language], level=2, clearable=False, prefix=False)
            # self.ui.plc_status_dashboard
        
        except Exception as e:
            self.ui.logger.create_new_log(message=texts.WARNINGS['plc_summary_failed']['en'], level=5)
            return
    

    def write_parms(self):
        """
        ============================description===========================

        :returns: None
        """

        parms_dict = self.check_all_plc_parms()
        # self.notif_manager.create_new_notif(massage='Write Changes PLC', win_color=self.win_color, font_size=self.font_size, font_style=self.font_style)  # For big Change in plc we show a notif
        try:
            self.my_plc.write(parms_dict)
        #
        except Exception as e:
            self.ui.show_mesagges(self.ui.plc_statues_label, texts.ERRORS['plc_write_json_failed'][self.ui.language], level=2)
            self.ui.logger.create_new_log(message=texts.ERRORS['plc_write_json_failed']['en'], level=5)
            self.notif_manager.create_new_notif(massage=texts.ERRORS['plc_write_json_failed'][self.ui.langage], win_color=self.win_color, font_size=self.font_size, font_style=self.font_style, level=2)  # For big Change in plc we show a notif