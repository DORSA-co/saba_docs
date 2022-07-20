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

NO_SERIAL = 'No Serial'
TRIGGER_SOURCE = ['Off', 'Software', 'Line1']

global ZOOM_SCALE
ZOOM_SCALE = 200
ZOOM_MIN = 200
ZOOM_MAX = 1000
ZOOM_STEP = 100

# camer calibration  elements names in ui
calibration_params = ['calib_rotate_spinbox', 'calib_shiftw_spinbox', 'calib_radio_corsshair', 'calib_radio_grid', 'calib_shifth_spinbox'\
                        ,'calib_take_image', 'pixelvalue_next_btn', 'pixelvalue_prev_btn', 'calib_minarea_spinbox', 'calib_maxarea_spinbox', 'calib_maxarea_spinbox'\
                        , 'calib_thrs_spinbox', 'calibration_zoomin', 'calibration_zoomout', 'zoomin_label', 'zoomout_label']

#---------------------------------------------------------------------------------------------------------------------------

    
# get camera id by camera name label in the UI
def get_camera_id(camera_name_label):
    """
    this function is used to get camera id, using camera name label in ui camera settings page

    :param camera_name_label: in string
    :returns: camera_id: in string
    """
    
    try:
        return str(int(camera_name_label[-2:]))
    except:
        return '0'


# camera parametrs in camera setting section
#---------------------------------------------------------------------------------------------------------------------------
# get camera parameters from UI
def get_camera_params_from_ui(ui_obj):
    """
    this function is used to get camera parameters from ui (camera settings page)

    :param ui_obj: main ui object
    :returns: camera_params
    """
    
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
    # serial number
    camera_params['serial_number'] = '0' if ui_obj.serial_number_combo.currentText()==NO_SERIAL else ui_obj.serial_number_combo.currentText()

    return camera_params


# set/show current camera parameters on UI
def set_camera_params_to_ui(ui_obj, db_obj, camera_params, camera_id, available_serials):
    """
    this function is used to set input camera params to ui (camera settings page)

    :param ui_obj: main ui object
    :param db_obj: main database object
    :param camera_params: input camera parameters (in dict)
    :param camera_id: input camera id (in string)
    :param available_serials: available camera serials (list of strings)
    :returns: None
    """
    
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
    """
    this function takes as input a camera serial and update the serial combobox current value

    :param ui_obj: main ui object
    :param assigned_serial: camera serial (in string)
    :returns: None

    """
    # no serial is asigned to current camera
    if assigned_serial == '0':
        ui_obj.serial_number_combo.setCurrentText(NO_SERIAL)

    # serial asigned to current camera
    else:
        ui_obj.serial_number_combo.setCurrentText(assigned_serial)
        

# 
def assign_existing_serials_to_ui(ui_obj, db_obj, camera_id, available_serials):
    """
    this function is called on every camera selection on camera settngs page,
    it takes as input available camera serials list, and current camera id, and those serial that not assigned to any camera, and the current camera serial
    are added to serial combobox on ui

    :param ui_obj: main ui object
    :param db_obj: database object
    :param camera_id: current camera id
    :param available_serials: list of available camera serals (list of strings)
    :returns: None
    """
    
    # clear all items in combo
    ui_obj.serial_number_combo.clear()

    # assign no serial label
    item = sQStandardItem(NO_SERIAL)
    ui_obj.serial_number_combo.model().appendRow(item)

    for serial in available_serials:
        # validating serial to be not used by another camera
        serial_info = db_obj.search_camera_by_serial(serial)

        # add serial to combo, if not assigned to any camera, or is assigned to current camera
        if len(serial_info) == 0 or (len(serial_info) != 0 and serial_info['id'] == int(camera_id)):
            item = sQStandardItem(serial)
            ui_obj.serial_number_combo.model().appendRow(item)


# set cameras parameters to database given single camera-id (or for multiple cameras given multiple cameras-ids)
def set_camera_params_to_db(db_obj, camera_id, camera_params, checkbox_values):
    """
    this function is used to update camera params on database, given camera id(s)

    :param db_obj: database object
    :param camera_id: current camera id (in string)
    :param camera_params: dict of camera params
    :param checkbox_values: value of camera select checkboxes determing wheareas apply setting to current camera only or to multiple cameras
    
    :returns: result: a boolean value determining if the settings are applied to database or not
    """
    
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
        #
        elif checkbox_values == 2: # apply to bottom cameras
            camera_ids = bottom_camera_ids
        #
        elif checkbox_values == 3: # apply to all cameras
            camera_ids = all_camera_ids
        #
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
    """
    this function is used to get camera params from database, using camera id

    :param db_obj: database object
    :param camera_id: id of the camera (in string)
    
    :returns: camera_params: a dict containing camera parameters
    """
    
    if camera_id != '0':
        camera_params = db_obj.load_cam_params(camera_id)
        return camera_params

    else:
        return []


# validating camera ip address
def validate_camera_ip(ui_obj, db_obj, camera_id, camera_params): # must change to validate ip range
    """
    this function is used to validate camera ip to be valid and not used by oter cameras

    :param ui_obj: main ui object
    :param db_obj: database object
    :param camera_id: current camera ip
    :param camera_params: camera parameters (dict)

    :returns: result: a boolean determining ip validation is ok or not
    :returns: message: the error message of ip validation not ok
    """
    
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
    """
    this function is used to validate ip to be in right format

    :param ui_obj: main ui object
    :param ip_address: input ip address (in string)
    
    :returns: message: a text message determining if the ip validation is ok or not,
            'True' for validation ok
    """
    
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
    """
    this function returns a value determining wheareas to apply camera settings/params to only current camera, or multiple cameras
    in ui, there are two checkboxes for bottom and top cameras. enabling each of them means to apply current settings to all of the cameras on top/bottom

    :param ui_obj: main ui object
    
    :returns: a number in range [0, 3], determining wheareas to apply camera settings/params to only current camera, or multiple cameras
            0: apply to current camera only
            1: apply to top cameras
            2: apply to bottom cameras
            3: apply to all cameras
    """
    
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
    """
    this function returns the camera sot calibration params from ui

    :param ui_obj: main ui object
    :returns: camera_calibration_params: in dict
    """
    
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
    """
    this functino is used to set camera calibration params returned from dataabse, to ui

    :param ui_obj: (_type_) main ui object
    :param camera_calibration_params: (_type_) in dict
    :returns: None
    """

    ui_obj.calib_rotate_spinbox.setValue(camera_calibration_params['rotation_value'])
    ui_obj.calib_shifth_spinbox.setValue(camera_calibration_params['shifth_value'])
    ui_obj.calib_shiftw_spinbox.setValue(camera_calibration_params['shiftw_value'])


# set calibration parameters of the camera to database 
def set_camera_calibration_params_to_db(db_obj, camera_id, camera_calibration_params):
    """
    this function is used to set camera calibration params to database

    :param db_obj: (_type_) database object
    :param camera_id: (_type_) _description_
    :param camera_calibration_params: (_type_) in dict

    :returns: resault: boolean determining update ok
    """

    res = db_obj.update_cam_params(str(int(camera_id)), camera_calibration_params)
    return res # validation


# get/load calibration parameters of the camera from database 
def get_camera_calibration_params_from_db(db_obj, camera_id):
    """
    this function is used to get camera calibration params from database, given camera id

    :param db_obj: (_type_) database object
    :param camera_id: (_type_) _description_

    :returns: camera_calibration_params: in dict
    """

    camera_calibration_params = db_obj.load_cam_params(str(int(camera_id)))
    return camera_calibration_params


# soft calibration functions
def shift_calibration_image(image, shifth, shiftw):
    """
    this function is used to shift image along y or x (vertical or horizintal)

    :param image: input image
    :param shifth: value to shift image horiintaly
    :param shiftw: value to shift image vertically
    
    :returns: shifted_image:
    """
    
    row, col = image.shape[:2]
    translation_matrix = np.float32([[1, 0, shiftw], [0, 1, shifth]])   
    shifted_image = cv2.warpAffine(image, translation_matrix, (col, row))

    return shifted_image


def rotate_calibration_image(image, angle):
    """
    this function is used to rotate image along center by input angle

    :param image: input image
    :param angle: input angle to rotate image (in degree)
    :returns: rotated_image:
    """
    
    row, col = image.shape[:2]
    center = (col / 2, row / 2)
    rot_matrix = cv2.getRotationMatrix2D(center, angle, 1.0)
    rotated_image = cv2.warpAffine(image, rot_matrix, (col, row))

    return rotated_image


# draw guidance grid on the calibration image
def draw_grid(image, crosshair=True):
    """
    this function is used to draw align grids on input image

    :param image: (_type_) _description_
    :param crosshair: (bool, optional) a boolean determining wheather draw cross-hair or grid. Defaults to True.

    :returns: image: image with grid
    """
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
def apply_soft_calibrate_on_image(ui_obj, image, camera_calibration_params, pxcalibration=False):
    """
    this function is used to apply soft calibration params to camera image

    :param ui_obj: main ui object
    :param image: input camera image
    :param camera_calibration_params: input camera calibration params (as a dict)
    :param pxcalibration: a boolean determining wheater in pixel calibration step or not
    :returns: image: result image that is soft calibrated
    """
    
    # rotating and calibrating image
    image = rotate_calibration_image(image, camera_calibration_params['rotation_value'])
    image = shift_calibration_image(image, camera_calibration_params['shifth_value'], camera_calibration_params['shiftw_value'])

    # check to show/not show guidance grid on image, if on pixel value calibration step
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
    """
    this function is used to converte a cv2 image to qt format image

    :param image: (_type_) image in cv2 format
    :returns: qt_image: image in qt format
    """

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
    """
    this function is used to get available camera serials that are connected to network

    :returns: serial_list: list of available camera serials (in string)
    """
    # camera collector object
    collector = camera_connection.Collector(serial_number='0', list_devices_mode=True)
    # get serial number of available cameras
    serial_list = collector.serialnumber()
    #
    del collector

    return serial_list


def update_available_camera_serials_on_db(db_obj, available_serials):
    """
    this function is used to update available camera serials on database,
    it takes as input available camera serial, and checks the database,
    for each camera, if serial in database not in available cameras, assign 0 as its serial

    :param db_obj: (_type_) database object
    :param available_serials: (_type_) list of available camera serials (in string)

    :returns: None
    """

    for camera_id in all_camera_ids:
        # get camera serials
        serial_number = get_camera_params_from_db(db_obj, str(int(camera_id)))['serial_number']
        if serial_number not in available_serials and serial_number!='0':
            res = db_obj.update_cam_params(str(int(camera_id)), {'serial_number':'0'})


# connect to cameras given entered serial number and camera parameters
def connect_disconnect_camera(ui_obj, db_pbj, serial_number, connect=True, current_cam_connection=None, calibration=False):
    """
    this functions is used to connect/disconnect from camera.
    in connect mode, a connection to camera with input serial number is returned,
    while in dissconnect mode, the input camera connection is closed

    :param ui_obj: main ui object
    :param db_pbj: database object
    :param serial_number: camera serial number (in string)
    :param connect: a boolean determning wheter to create a new connection to camer, or disconnect from current camera
    :param current_cam_connection: current camera connection object
    :param calibration: a boolean determining if camera connection is for camera calibration page
    
    :returns: on conect:
                camera_connection: the stablished camera connection, if faled, return None
                message: a meesage determinig the error occured while connecting to camera
    :returns: on desconnect: None
    """
    
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
            trigger_source = TRIGGER_SOURCE[0]
        elif int(camera_params['trigger_mode']) == 1:
            trigger_source = TRIGGER_SOURCE[1]
        elif int(camera_params['trigger_mode']) == 2:
            trigger_source = TRIGGER_SOURCE[2]

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
        
        # failed to connect to camera
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
        # set no image picture on ui on camera image label
        try:
            if not calibration:
                set_camera_picture_to_ui(ui_image_label=ui_obj.camera_setting_picture_label, image=cv2.imread('./images/no_image.png'))
            else:
                set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=cv2.imread('./images/no_image.png'), with_zoom=True, zoom_min=True)
        except:
            if not calibration:
                set_camera_picture_to_ui(ui_image_label=ui_obj.camera_setting_picture_label, image=np.zeros((500,500,3)).astype(np.uint8))
            else:
                set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=np.zeros((500,500,3)).astype(np.uint8), with_zoom=True, zoom_min=True)



# get live image from camera using camera-collector function
def get_picture_from_camera(camera_connection):
    """
    this function is used to get picture from camera, using its camera connection

    :param camera_connection: (_type_) _description_
    :returns:
        live_image: image
    """

    # get live frame
    res, live_image = camera_connection.getPictures()
    return res, live_image


# set camera picture to ui
def set_camera_picture_to_ui(ui_image_label, image, with_zoom=False, zoom_min=False):
    """
    this function is used to set an image to ui label

    :param ui_image_label: (_type_) ui lable name
    :param image: (_type_) input image
    :param with_zoom: (_type_) boolean determining wheather to zoom image

    :returns: None
    """

    # converting cv2 image to Qt format
    converted_image = convert_cv2_to_qt_image(image=image)

    pixmap_image = sQPixmap.fromImage(converted_image)
    # zoom in/out
    if with_zoom:
        pixmap_image = pixmap_image.scaledToHeight(ZOOM_SCALE if not zoom_min else ZOOM_MIN)

    # set image to UI
    ui_image_label.setPixmap(pixmap_image)


def zoom_in_calibration_image(ui_obj):
    """
    this function is used to zoom in calibration image on button click

    :param ui_obj: (_type_) main ui object
    :returns: None
    """

    global ZOOM_SCALE
    if ZOOM_SCALE >= ZOOM_MAX:
        return
    ZOOM_SCALE += ZOOM_STEP

    try:
        set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=ui_obj.calibration_image, with_zoom=True)
    except:
        ZOOM_SCALE -= ZOOM_STEP


def zoom_out_calibration_image(ui_obj):
    """
    this function is used to zoom out calibration image on button click

    :param ui_obj: (_type_) main ui object
    :returns: None
    """

    global ZOOM_SCALE
    if ZOOM_SCALE <= ZOOM_MIN:
        return
    ZOOM_SCALE -= ZOOM_STEP
    
    try:
        set_camera_picture_to_ui(ui_image_label=ui_obj.calib_camera_image, image=ui_obj.calibration_image, with_zoom=True)
    except:
        ZOOM_SCALE += ZOOM_STEP


# update UI parametrs on camera connect or disconnect
def update_ui_on_camera_connect_disconnect(ui_obj, api_obj, connect=True, calibration=False):
    """
    this function is used to update ui buttons on camera setting and calibration pages, on camera connect/dissconnect
    on every camera connect, camera take picture button must be enable, while camera connect button must be changed to disconnect
    on camera disconnect, camera take picture button must set to disable, while camera connect button must be changed to connect

    :param ui_obj: main ui object
    :param api_obj: main api object
    :param connect: a boolean determinnig if camera is connected or disconnected
    :param calibration: a boolean determining if current page on ui is calibration page

    :returns: None
    """
    
    if connect:
        ui_obj.camera_connect_flag = True
        
        if not calibration:
            ui_obj.show_mesagges(ui_obj.camera_setting_message_label, texts.MESSEGES['camera_connect'][ui_obj.language], level=0)
            # make get picture button available
            ui_obj.camera_setting_getpic_btn.setEnabled(True)
            # change camera-connect button text and color
            ui_obj.camera_setting_connect_btn.setText('Disconnect')
            ui_obj.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.failed_red))

        else:
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['camera_connect'][ui_obj.language], level=0)
            # make get picture button available
            set_widjets_enable_or_disable(ui_obj=ui_obj, api_obj=api_obj, names=['calib_take_image'])
            # pixel value calibration next button enable on calibration page
            ui_obj.pixelvalue_next_btn.setEnabled(False)
            # change camera-connect button text and color
            ui_obj.connet_camera_calibre_btn.setText('Disconnect')
            ui_obj.connet_camera_calibre_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.failed_red))

    # disconnect       
    else:
        ui_obj.camera_connect_flag = False

        if not calibration:
            ui_obj.show_mesagges(ui_obj.camera_setting_message_label, texts.MESSEGES['camera_disconnect'][ui_obj.language], level=0)
            #ui_obj.logger.create_new_log(message=texts.MESSEGES['camera_disconnect']['en'], level=5)

            # make get picture button unavailable
            ui_obj.camera_setting_getpic_btn.setEnabled(False)
            # change camera-connect button text and color
            ui_obj.camera_setting_connect_btn.setText('Connect')
            ui_obj.camera_setting_connect_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.successfull_green))

        else:
            ui_obj.show_mesagges(ui_obj.camera_calibration_message_label, texts.MESSEGES['camera_disconnect'][ui_obj.language], level=0)
            # make get picture button as wwll as other elements unavailable
            set_widjets_enable_or_disable(ui_obj=ui_obj, api_obj=api_obj, names=calibration_params, enable=False)
            # change camera-connect button text and text
            ui_obj.connet_camera_calibre_btn.setText('Connect')
            ui_obj.connet_camera_calibre_btn.setStyleSheet("background-color:{}; border:Transparent".format(colors_pallete.successfull_green))


# set UI objects enable or disable 
def set_widjets_enable_or_disable(ui_obj, api_obj, names, enable=True):
    """
    this function is used to get ui element names in a list, and enable/disable them

    :param ui_obj: main ui object
    :param api_obj: main api object
    :param names: ui element names (list of strings)
    :param enable: a boolean determinnig whereas enable or disable ui elements
    
    :returns: None
    """
    
    for name in names:
        eval('ui_obj.%s' % name).setEnabled(enable)

    if enable and api_obj.pxcalibration_step == 0:
        ui_obj.pixelvalue_prev_btn.setEnabled(False)


def show_cameras_summary(ui_obj):
    """
    this function is used to set/update cameras summary params on ui dashboard page

    :param ui_obj: (_type_) main ui object
    
    :returns: None
    """

    try:

        # n available cameras
        n_available_camera = len(get_available_cameras_list_serial_numbers())
        if n_available_camera == num_cameras:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=0, clearable=False, prefix=False)
        
        elif n_available_camera > 0:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=1, clearable=False, prefix=False)
        
        else:
            ui_obj.show_mesagges(ui_obj.available_cameras, text=str(n_available_camera), level=2, clearable=False, prefix=False)

        # cameras trigger mode
        ui_obj.show_mesagges(ui_obj.dash_trigger_mode, text=TRIGGER_SOURCE[2], level=0, clearable=False, prefix=False)
    
    except Exception as e:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['camera_summary_failed']['en'], level=5)
        return


def show_calibration_summary(ui_obj, db_obj):
    """
    this function is used to set/update calibration summary params on ui dashboard page

    :param ui_obj: (_type_) main ui object
    
    :returns: None
    """

    try:

        # determine which cameras are not calibrated
        n_not_calibrated = 0
        for camera_id in range(1, num_cameras+1):
            camera_calibration_params = get_camera_calibration_params_from_db(db_obj, camera_id)

            # check if px-value params not zero
            if int(camera_calibration_params['pxvalue_a'])==0 and int(camera_calibration_params['pxvalue_b'])==0 and int(camera_calibration_params['pxvalue_c'])==0:
                n_not_calibrated += 1

        if n_not_calibrated == 0:
            ui_obj.show_mesagges(ui_obj.dash_width_gauge, text=texts.MESSEGES['all_cameras_calibrated'][ui_obj.language], level=0, clearable=False, prefix=False)
        
        elif n_not_calibrated < num_cameras:
            ui_obj.show_mesagges(ui_obj.dash_width_gauge, text=texts.WARNINGS['some_cameras_not_calibrated'][ui_obj.language], level=1, clearable=False, prefix=False)
        
        else:
            ui_obj.show_mesagges(ui_obj.dash_width_gauge, text=texts.ERRORS['all_cameras_not_calibrated'][ui_obj.language], level=2, clearable=False, prefix=False)
        

        # determine image processing calibration applied, check if params not zero
        image_procesing_params = db_obj.get_image_processing_parms()
        if int(image_procesing_params['defect']==0) and int(image_procesing_params['noise']==0) and int(image_procesing_params['noise_flag']==0):
            ui_obj.show_mesagges(ui_obj.dash_image_processing, text=texts.ERRORS['all_cameras_not_calibrated'][ui_obj.language], level=2, clearable=False, prefix=False)
        else:
            ui_obj.show_mesagges(ui_obj.dash_image_processing, text=texts.MESSEGES['all_cameras_calibrated'][ui_obj.language], level=0, clearable=False, prefix=False)

    
    except Exception as e:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['calibration_summary_failed']['en'], level=5)
        return








    




    


    





    
    





    


    
        