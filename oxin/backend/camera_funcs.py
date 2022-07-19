import numpy as np
import cv2
from PySide6.QtGui import QImage as sQImage
from PySide6.QtGui import QStandardItem as sQStandardItem
from PySide6.QtGui import QPixmap as sQPixmap

from . import camera_connection, colors_pallete, texts


# number of cameras
num_cameras = 24

# camera ids
all_camera_ids = ["{:02d}".format(x) for x in np.arange(1, num_cameras+1)]
top_camera_ids = ["{:02d}".format(x) for x in np.arange(1, num_cameras//2+1)]
bottom_camera_ids = ["{:02d}".format(x) for x in np.arange(num_cameras//2+1, num_cameras+1)]

# guidance grids for camera calibration
grid_shape = [20, 30]
crosshair_shape = [2 ,2]
grid_color = (255 ,0 , 0)
grid_thickness = 1

# camer calibration params
calibration_params = ['calib_rotate_spinbox', 'calib_shiftw_spinbox', 'calib_radio_corsshair', 'calib_radio_grid', 'calib_shifth_spinbox'\
                        ,'calib_take_image', 'pixelvalue_next_btn', 'pixelvalue_prev_btn', 'calib_minarea_spinbox', 'calib_maxarea_spinbox', 'calib_maxarea_spinbox'\
                        , 'calib_thrs_spinbox']

#---------------------------------------------------------------------------------------------------------------------------

    
# get camera id by camera name label in the UI
def get_camera_id(camera_name_label):
    try:
        return str(int(camera_name_label[-2:]))
    except:
        return '0'


# camera parametrs in camera setting section
#---------------------------------------------------------------------------------------------------------------------------
# get camera parameters from UI
def get_camera_params_from_ui(ui_obj):
    camera_params = {}
    camera_params['gain_value'] = ui_obj.gain_spinbox.value()
    camera_params['expo_value'] = ui_obj.expo_spinbox.value()
    camera_params['width'] = ui_obj.width_spinbox.value()
    camera_params['height'] = ui_obj.height_spinbox.value()
    camera_params['offsetx_value'] = ui_obj.offsetx_spinbox.value()
    camera_params['offsety_value'] = ui_obj.offsety_spinbox.value()
    camera_params['max_buffer'] = ui_obj.maxbuffer_spinbox.value()
    camera_params['interpacket_delay'] = ui_obj.packetdelay_spinbox.value()
    camera_params['packet_size'] = ui_obj.packetsize_spinbox.value()
    camera_params['transmission_delay'] = ui_obj.transmissiondelay_spinbox.value()
    camera_params['ip_address'] = ui_obj.ip_lineedit.text()

    # trigger mode
    camera_params['trigger_mode'] = str(ui_obj.trigger_combo.currentIndex())
    
    camera_params['serial_number'] = '0' if ui_obj.serial_number_combo.currentText()=='No Serial' else ui_obj.serial_number_combo.currentText()
    return camera_params


# set/show current camera parameters on UI
def set_camera_params_to_ui(ui_obj, db_obj, camera_params, camera_id, available_serials):
    ui_obj.gain_spinbox.setValue(camera_params['gain_value'])
    ui_obj.expo_spinbox.setValue(camera_params['expo_value'])
    ui_obj.width_spinbox.setValue(camera_params['width'])
    ui_obj.height_spinbox.setValue(camera_params['height'])
    ui_obj.offsetx_spinbox.setValue(camera_params['offsetx_value'])
    ui_obj.offsety_spinbox.setValue(camera_params['offsety_value'])
    ui_obj.maxbuffer_spinbox.setValue(camera_params['max_buffer'])
    ui_obj.packetdelay_spinbox.setValue(camera_params['interpacket_delay'])
    ui_obj.packetsize_spinbox.setValue(camera_params['packet_size'])
    ui_obj.transmissiondelay_spinbox.setValue(camera_params['transmission_delay'])
    ui_obj.ip_lineedit.setText(camera_params['ip_address'])

    # trigger mode
    ui_obj.trigger_combo.setCurrentIndex(int(camera_params['trigger_mode']))

    # serial
    assign_existing_serials_to_ui(ui_obj, db_obj, camera_id, available_serials)
    set_camera_serial_to_ui(ui_obj, camera_params['serial_number'])


def set_camera_serial_to_ui(ui_obj, assigned_serial):
    # no serial is asigned to current camera
    if assigned_serial == '0':
        ui_obj.serial_number_combo.setCurrentText('No Serial')
    # serial asigned to current camera
    else:
        ui_obj.serial_number_combo.setCurrentText(assigned_serial)
        

# assign top appearance parameters to UI
def assign_existing_serials_to_ui(ui_obj, db_obj, camera_id, available_serials):
    # clear all items in combo
    ui_obj.serial_number_combo.clear()
    # assign no serial label
    item = sQStandardItem('No Serial')
    ui_obj.serial_number_combo.model().appendRow(item)

    for serial in available_serials:
        # validating serial to be not used by another camera
        serial_info = db_obj.search_camera_by_serial(serial)
        if len(serial_info) == 0 or (len(serial_info) != 0 and serial_info['id'] == int(camera_id)):
            item = sQStandardItem(serial)
            ui_obj.serial_number_combo.model().appendRow(item)


# set cameras parameters to database given single camera-id (or for multiple cameras given multiple cameras-ids)
def set_camera_params_to_db(db_obj, camera_id, camera_params, checkbox_values):
    # apply settings to single current camera
    if checkbox_values == 0: 
        res = db_obj.update_cam_params(camera_id, camera_params)

    # apply current camera settings to multiple cameras
    else: 
        res = db_obj.update_cam_params(camera_id, camera_params)
        # pop camera ip address and serial number to prevent applying to all cameras
        camera_params.pop('ip_address', None)
        camera_params.pop('serial_number', None)
        if checkbox_values == 1: # apply to top cameras
            camera_ids = top_camera_ids
        elif checkbox_values == 2: # apply to bottom cameras
            camera_ids = bottom_camera_ids
        elif checkbox_values == 3: # apply to all cameras
            camera_ids = all_camera_ids
        # set to dataset
        for camera_id in camera_ids:
            res = db_obj.update_cam_params(str(int(camera_id)), camera_params)
            # validation
            if not res:
                return res
    # validation
    return res


# get cameras parameters from database given camera-id
def get_camera_params_from_db(db_obj, camera_id):
    if camera_id != '0':
        camera_params = db_obj.load_cam_params(camera_id)
        return camera_params
    else:
        return []


# validating camera ip address
def validate_camera_ip(ui_obj, db_obj, camera_id, camera_params): # must change to validate ip range
    # validating ip address to be in correct form
    ip_validate = ip_validation(ui_obj, camera_params['ip_address'])
    if ip_validate != 'True':
        return False, ip_validate

    # validating ip address to be not used by another camera
    ip_info = db_obj.search_camera_by_ip(camera_params['ip_address'])

    if len(ip_info) != 0 and ip_info['id'] != int(camera_id):
        return False, texts.ERRORS['ip_in_used'][ui_obj.language]

    return True, 'True'


def ip_validation(ui_obj, ip_address):
    octets = ip_address.split(".")
    size = len(octets)
    # check to have 4 sections
    if size != 4:
        return texts.WARNINGS['ip_invalid'][ui_obj.language]

    # check each section to be in range 0-256
    for octet in octets:
        try:
            number = int(octet)
            if number < 0 or number > 255:
                return texts.WARNINGS['ip_out_of_range'][ui_obj.language]
        except:
            return texts.WARNINGS['ip_contain_letters'][ui_obj.language]

    return 'True'


# get the value of checkboxes in the camera setting page for multi-camera save settings
def get_camera_checkbox_values(ui_obj):
    checkbox_top = ui_obj.checkBox_top.isChecked()
    checkbox_bottom = ui_obj.checkBox_bottom.isChecked()
    # check
    if not checkbox_top and not checkbox_bottom: # checkboxes are not checked
        return 0
    elif checkbox_top and not checkbox_bottom: # top cameras are checked
        return 1
    elif not checkbox_top and checkbox_bottom: # bottom cameras are checked
        return 2
    elif checkbox_top and checkbox_bottom: # all cameras are checked
        return 3


# soft-calibration in calibration settings page
#---------------------------------------------------------------------------------------------------------------------------
# get camera calibration parameters from UI
def get_camera_calibration_params_from_ui(ui_obj):
    camera_calibration_params = {}
    camera_calibration_params['rotation_value'] = ui_obj.calib_rotate_spinbox.value()
    camera_calibration_params['shifth_value'] = ui_obj.calib_shifth_spinbox.value()
    camera_calibration_params['shiftw_value'] = ui_obj.calib_shiftw_spinbox.value()
    camera_calibration_params['calib_minarea'] = ui_obj.calib_minarea_spinbox.value()
    camera_calibration_params['calib_maxarea'] = ui_obj.calib_maxarea_spinbox.value()
    camera_calibration_params['calib_thrs'] = ui_obj.calib_thrs_spinbox.value()
    camera_calibration_params['pxvalue_a'] = ui_obj.pxvaluea_label.text()
    camera_calibration_params['pxvalue_b'] = ui_obj.pxvalueb_label.text()
    camera_calibration_params['pxvalue_c'] = ui_obj.pxvaluec_label.text()
    return camera_calibration_params


# set camera calibration parameters to UI
def set_camera_calibration_params_to_ui(ui_obj, camera_calibration_params):
    ui_obj.calib_rotate_spinbox.setValue(camera_calibration_params['rotation_value'])
    ui_obj.calib_shifth_spinbox.setValue(camera_calibration_params['shifth_value'])
    ui_obj.calib_shiftw_spinbox.setValue(camera_calibration_params['shiftw_value'])


# set calibration parameters of the camera to database 
def set_camera_calibration_params_to_db(db_obj, camera_id, camera_calibration_params):
    res = db_obj.update_cam_params(str(int(camera_id)), camera_calibration_params)
    return res # validation


# get/load calibration parameters of the camera from database 
def get_camera_calibration_params_from_db(db_obj, camera_id):
    camera_calibration_params = db_obj.load_cam_params(str(int(camera_id)))
    return camera_calibration_params


# soft calibration functions
def shift_calibration_image(image, shifth, shiftw):
    row, col = image.shape[:2]
    translation_matrix = np.float32([[1, 0, shiftw], [0, 1, shifth]])   
    shifted_image = cv2.warpAffine(image, translation_matrix, (col, row))
    return shifted_image

def rotate_calibration_image(image, angle):
    row, col = image.shape[:2]
    center = (col / 2, row / 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rot_matrix, (col, row))
    return rotated_image


# draw guidance grid on the calibration image
def draw_grid(image, crosshair=True):
    row, col = image.shape[:2]
    rows, cols = crosshair_shape if crosshair else grid_shape
    dy, dx = row / rows, col / cols
    # draw vertical lines
    for x in np.linspace(start=dx, stop=col-dx, num=cols-1):
        x = int(round(x))
        cv2.line(image, (x, 0), (x, row), color=grid_color, thickness=grid_thickness)
    # draw horizontal lines
    for y in np.linspace(start=dy, stop=row-dy, num=rows-1):
        y = int(round(y))
        cv2.line(image, (0, y), (col, y), color=grid_color, thickness=grid_thickness)
    return image


# apply soft-calibration parameters on input image
def apply_soft_calibrate_on_image(ui_obj, image, camera_calibration_params, pxcalibration = False):
    image = rotate_calibration_image(image, camera_calibration_params['rotation_value'])
    image = shift_calibration_image(image, camera_calibration_params['shifth_value'], camera_calibration_params['shiftw_value'])
    # check to show/not show guidance grid on image
    if not pxcalibration:
        if ui_obj.calib_radio_corsshair.isChecked():
            image = draw_grid(image, crosshair=True)
        elif ui_obj.calib_radio_grid.isChecked():
            image = draw_grid(image, crosshair=False)
    return image


# functions for connecting to camera, get picture and show on UI
#---------------------------------------------------------------------------------------------------------------------------
# convert cv2 image to Qt format to show in UI
def convert_cv2_to_qt_image(image):
    # convert cv2 image to Qt format image
    if len(image.shape) == 3:
        row, col, channel = image.shape
    else:
        image = cv2.cvtColor(image, cv2.COLOR_GRAY2RGB)
        row, col, channel = image.shape
    bytes_per_line = channel * col
    converted_image = sQImage(image.data, col, row, bytes_per_line, sQImage.Format_RGB888)
    return converted_image


def get_available_cameras_list_serial_numbers():
    # camera collector object
    collector = camera_connection.Collector(serial_number='0', list_devices_mode=True)
    # get serial number of available cameras
    serial_list = collector.serialnumber()
    #
    del collector
    return serial_list


def update_available_camera_serials_on_db(db_obj, available_serials):
    for camera_id in all_camera_ids:
        # get camera serials
        serial_number = get_camera_params_from_db(db_obj, str(int(camera_id)))['serial_number']
        if serial_number not in available_serials and serial_number!='0':
            res = db_obj.update_cam_params(str(int(camera_id)), {'serial_number':'0'})


# connect to cameras given entered serial number and camera parameters
def connect_disconnect_camera(ui_obj, db_pbj, serial_number, connect=True, current_cam_connection=None, calibration=False):
    # connect
    if connect:
        # get camera parameters from UI
        if not calibration:
            camera_params = get_camera_params_from_ui(ui_obj)
        else:
            camera_id = ui_obj.comboBox_cam_select_calibration.currentText()
            camera_params = get_camera_params_from_db(db_obj=db_pbj, camera_id=camera_id)
        
        # trigger source
        if int(camera_params['trigger_mode']) == 0:
            trigger_source = 'Off'
        elif int(camera_params['trigger_mode']) == 1:
            trigger_source = 'Software'
        elif int(camera_params['trigger_mode']) == 2:
            trigger_source = 'Line1'

        # make connection
        try:
            cam_connection = camera_connection.Collector(serial_number=serial_number,
                                                        exposure=int(camera_params['expo_value']),
                                                        gain=int(camera_params['gain_value']),
                                                        trigger=0 if int(camera_params['trigger_mode'])==0 else 1,
                                                        trigger_source=trigger_source,
                                                        delay_packet=int(camera_params['interpacket_delay']),
                                                        packet_size=int(camera_params['packet_size']),
                                                        frame_transmission_delay=int(camera_params['transmission_delay']),
                                                        height=int(camera_params['height']),
                                                        width=int(camera_params['width']),
                                                        offet_x=int(camera_params['offsetx_value']),
                                                        offset_y=int(camera_params['offsety_value']),
                                                        manual=True,
                                                        list_devices_mode=False)
            # start grabbing                                     
            res, message = cam_connection.start_grabbing()
            if not res:
                ui_obj.logger.create_new_log(message=message, level=3)
                return None, message

            try:
                ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_connect']['en'] + ', serial: ' + str(cam_connection.serial_number), level=1)
            except:
                ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_connect']['en'], level=1)

            return cam_connection, ''
        
        except Exception as e:
            ui_obj.logger.create_new_log(message=texts.ERRORS['camera_connect_failed']['en'], level=5)
            return None, texts.ERRORS['camera_connect_failed'][ui_obj.language]


    # disconnect
    else:
        try:
            ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_disconnect']['en'] + ', serial: ' + str(current_cam_connection.serial_number), level=1)
        except:
            ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_disconnect']['en'], level=1)
        current_cam_connection.stop_grabbing()
        #
        try:
            if not calibration:
                set_camera_picture_to_ui(ui_image_label=ui_obj.camera_setting_picture_label, image=cv2.imread('./images/no_image.png'))
            else:
                set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=cv2.imread('./images/no_image.png'))
        except:
            if not calibration:
                set_camera_picture_to_ui(ui_image_label=ui_obj.camera_setting_picture_label, image=np.zeros((500,500,3)).astype(np.uint8))
            else:
                set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=np.zeros((500,500,3)).astype(np.uint8))



# get live image from camera using camera-collector function
def get_picture_from_camera(camera_connection):
    # get live frame
    live_image = camera_connection.getPictures()
    return live_image


# set camera picture to ui
def set_camera_picture_to_ui(ui_image_label, image):
    # converting cv2 image to Qt format
    converted_image = convert_cv2_to_qt_image(image=image)
    # set image to UI
    ui_image_label.setPixmap(sQPixmap.fromImage(converted_image))


# update UI parametrs on camera connect or disconnect
def update_ui_on_camera_connect_disconnect(ui_obj, api_obj, connect=True, calibration=False):
    if connect:
        ui_obj.camera_connect_flag = True
        if not calibration:
            ui_obj.show_mesagges(ui_obj.camera_setting_message_label, texts.MESSEGES['camera_connect'][ui_obj.language], level=0)
            # make get picture button available
            ui_obj.camera_setting_getpic_btn.setEnabled(True)
            # change camera-connect button text
            ui_obj.camera_setting_connect_btn.setText('Disconnect')
            ui_obj.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.failed_red))

        else:
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['camera_connect'][ui_obj.language], level=0)
            # make get picture button available
            #ui_obj.calib_take_image.setEnabled(True)
            set_widjets_enable_or_disable(ui_obj=ui_obj, api_obj=api_obj, names=['calib_take_image'])
            ui_obj.pixelvalue_next_btn.setEnabled(False)
            # change camera-connect button text
            ui_obj.connet_camera_calibre_btn.setText('Disconnect')
            ui_obj.connet_camera_calibre_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.failed_red))
            
    else:
        ui_obj.camera_connect_flag = False
        if not calibration:
            ui_obj.show_mesagges(ui_obj.camera_setting_message_label, texts.MESSEGES['camera_disconnect'][ui_obj.language], level=0)
            #ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_disconnect']['en'], level=5)

            # make get picture button unavailable
            ui_obj.camera_setting_getpic_btn.setEnabled(False)
            # change camera-connect button text
            ui_obj.camera_setting_connect_btn.setText('Connect')
            ui_obj.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.successfull_green))

        else:
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['camera_disconnect'][ui_obj.language], level=0)
            # make get picture button unavailable
            #ui_obj.calib_take_image.setEnabled(False)
            set_widjets_enable_or_disable(ui_obj=ui_obj, api_obj=api_obj, names=calibration_params, enable=False)
            # change camera-connect button text
            ui_obj.connet_camera_calibre_btn.setText('Connect')
            ui_obj.connet_camera_calibre_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.successfull_green))


# set UI objects enable or disable 
def set_widjets_enable_or_disable(ui_obj, api_obj, names, enable=True):
    for name in names:
        eval('ui_obj.%s' % name).setEnabled(enable)
    if enable and api_obj.pxcalibration_step == 0:
        ui_obj.pixelvalue_prev_btn.setEnabled(False)



    




    


    





    
    





    


    
        