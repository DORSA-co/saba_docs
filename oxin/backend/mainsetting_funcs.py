import numpy as np
from PySide6.QtGui import QStandardItem as sQStandardItem
from PySide6.QtGui import QFont as sQFont
from PySide6.QtGui import QColor as sQColor


# font parameters      
font_sizes = ["{:d}".format(x) for x in np.arange(8, 12)]
font_styles = ['Arial','Times New Roman', 'Calibri', 'B Nazanin', 'B Yekan', 'B Koodak', 'B Titr', 'B Traffic']

# style (theme) and color parameters
app_styles = ['Breeze', 'Oxygen', 'QtCurve', 'Windows', 'Fusion']
app_colors = ['#144475', '#019FDC', '#96C61D', '#F5E603', '#F9BD07', '#FA3A2F', '#993BB3', '#01C099', '#2D4960', '#CFD3D5']

# language parametrs
app_languages = ['English','Persian(فارسی)']


#---------------------------------------------------------------------------------------------------------------------------

# program appearance functions in main-setting page
#---------------------------------------------------------------------------------------------------------------------------
# assign top appearance parameters to UI
def assign_appearance_existing_params_to_ui(ui_obj):
    """
    this function is used to assign default apearance params to ui (combobox contents in main-setting page)

    Args:
        ui_obj (_type_): main ui object
    
    Returns: None
    """

    # font-size
    # self.ui.setting_fontsize_comboBox.addItems(appearance.font_sizes)
    for font_size in font_sizes:
        item = sQStandardItem(font_size)
        item.setFont(sQFont('Arial', int(font_size)))
        ui_obj.setting_fontsize_comboBox.model().appendRow(item)

    # font-style
    # self.ui.setting_fontstyle_comboBox.addItems(appearance.font_style)
    for font_style in font_styles:
        item = sQStandardItem(font_style)
        item.setFont(sQFont(font_style))
        ui_obj.setting_fontstyle_comboBox.model().appendRow(item)

    # app style (theme)app_languagessetting_language_comboBox
    ui_obj.setting_style_comboBox.addItems(app_styles)

    # app color
    for app_color in app_colors:
        item = sQStandardItem(app_color)
        item.setBackground(sQColor(app_color))
        ui_obj.setting_color_comboBox.model().appendRow(item)
        
    # app language
    ui_obj.setting_language_comboBox.addItems(app_languages)


# get appearance parameters and apply them to UI
def set_appearance_params_to_ui(ui_obj, appearance_params, multitask_params=None):
    """
    this function is used to set input apearance params to ui setting page elements

    Args:
        ui_obj (_type_): main ui object
        appearance_params (_type_): in dict
        multitask_params (_type_, optional): if not none, set multtalsk params. Defaults to None.
    
    Returns: None
    """

    ui_obj.setting_fontsize_comboBox.setCurrentText(str(appearance_params['font_size']))
    ui_obj.setting_fontstyle_comboBox.setCurrentText(appearance_params['font_style'])
    ui_obj.setting_style_comboBox.setCurrentText(appearance_params['window_style'])
    ui_obj.setting_color_comboBox.setCurrentText(appearance_params['window_color'])
    ui_obj.setting_language_comboBox.setCurrentText(appearance_params['language'])
    ui_obj.large_rect_area_label.setText(str(appearance_params['large_rect_area']))
    ui_obj.small_rect_area_label.setText(str(appearance_params['small_rect_area']))
    ui_obj.rect_accuracy_label.setText(str(appearance_params['rect_accuracy']))
    split_size = appearance_params['split_size'].split(',')
    try:
        ui_obj.splitsizew_spinBox.setValue(int(split_size[0][1:]))
        ui_obj.splitsizeh_spinBox.setValue(int(split_size[-1][:-1]))
        ui_obj.defect_colors_number_spin.setValue(int(appearance_params['n_defect_colors']))
    except:
        ui_obj.splitsizew_spinBox.setValue(0)
        ui_obj.splitsizeh_spinBox.setValue(0)
        ui_obj.defect_colors_number_spin.setValue(3)

    #
    if multitask_params!=None:
        ui_obj.camthread_spinBox.setValue(int(multitask_params['camera_threads_value']))
        ui_obj.camprocess_spinBox.setValue(int(multitask_params['camera_process_value']))
        ui_obj.wrtthread_spinBox.setValue(int(multitask_params['camera_refresh_rate_value']))
        ui_obj.refrate_spinBox.setValue(int(multitask_params['writing_thread_value']))


# get appearance parameters from UI
def get_appearance_params_from_ui(ui_obj):
    """
    this function is used to get app appearance params from ui seting page

    Args:
        ui_obj (_type_): main ui object

    Returns:
        appearance params: in dict
    """
    appearance_params = {}
    appearance_params['font_size'] = ui_obj.setting_fontsize_comboBox.currentText()
    appearance_params['font_style'] = ui_obj.setting_fontstyle_comboBox.currentText()
    appearance_params['window_style'] = ui_obj.setting_style_comboBox.currentText()
    appearance_params['window_color'] = ui_obj.setting_color_comboBox.currentText()
    appearance_params['language'] = ui_obj.setting_language_comboBox.currentText()

    return appearance_params


# get the appearance parameters and apply to program
def apply_appearance_params_to_program(ui_obj, confirm_ui_obj, login_ui_object, appearance_params):
    """
    this function is used to apply apearnace params in setting page to app

    Args:
        ui_obj (_type_): main ui object
        confirm_ui_obj (_type_): _description_
        appearance_params (_type_): in dict

    Returns:
        appearance_params['window_color']: color of the app
        appearance_params['font_size']: font-size of the app
        appearance_params['font_style']: font-style of the app
    """
    # apply to UI
    ui_obj.setStyleSheet('font: %spt %s;' % (appearance_params['font_size'], appearance_params['font_style'])) # font-size and font-style
    ui_obj.leftMenuFrame.setStyleSheet('background-color: %s;' % (appearance_params['window_color'])) # window color
    ui_obj.contentTopBg.setStyleSheet('background-color: %s;' % (appearance_params['window_color'])) # window color
    ui_obj.topLogoInfo.setStyleSheet('background-color: %s;' % (appearance_params['window_color'])) # window color
    ui_obj.leftBox.setStyleSheet('background-color: %s;' % (appearance_params['window_color'])) # window color
    # confirm-ui
    confirm_ui_obj.background_frame.setStyleSheet('background-color: %s; font: %spt %s;' % (appearance_params['window_color'], appearance_params['font_size'], appearance_params['font_style'])) # confirm window color
    # login-ui
    login_ui_object.setStyleSheet('background-color: %s; font: %spt %s;' % (appearance_params['window_color'], appearance_params['font_size'], appearance_params['font_style'])) # confirm window color
    login_ui_object.label.setStyleSheet('color: white; font: %spt %s;' % (str(int(appearance_params['font_size'])+10), appearance_params['font_style'])) # confirm window color
    
    # change app language
    if appearance_params['language'] == app_languages[0]:
        ui_obj.language = 'en'

    elif appearance_params['language'] == app_languages[1]:
        ui_obj.language = 'fa'

    # ui_obj.setStyle(sQStyleFactory.create(app_style"))
    # must change : style and language should be added
    return appearance_params['window_color'], appearance_params['font_size'], appearance_params['font_style']


# update combobox visual properties
def update_combo_color(ui_obj):
    """
    this function is used to update setting page color combobox background color by current color

    Args:
        ui_obj (_type_): main ui object
    
    Returns: None
    """

    current_color = ui_obj.setting_color_comboBox.currentText()
    ui_obj.setting_color_comboBox.setStyleSheet('background: %s;' % current_color)


def update_combo_fontstyle(ui_obj):
    """
    this function is used to update setting page fontstyle-combobox font acoading to current app fontstyle

    Args:
        ui_obj (_type_): main ui object
    
    Returns: None
    """

    current_fontstyle = ui_obj.setting_fontstyle_comboBox.currentText()
    ui_obj.setting_fontstyle_comboBox.setStyleSheet('font-family: %s;' % current_fontstyle)


def update_combo_fontsize(ui_obj):
    """
    this function is used to update setting page fontsize-combobox font according to current app fontsize

    Args:
        ui_obj (_type_): main ui object

    Returns: None
    """

    current_fontsize = ui_obj.setting_fontsize_comboBox.currentText()
    ui_obj.setting_fontsize_comboBox.setStyleSheet('font: %spt;' % current_fontsize)


# calibration functions in main-setting page
#---------------------------------------------------------------------------------------------------------------------------
# get calibration parameters from UI
def get_calibration_params_from_ui(ui_obj):
    """
    this function is used to get calibration params from main-setting page

    Args:
        ui_obj (_type_): main ui object

    Returns:
        calibration_params: in dict
    """

    calibration_params = {}
    calibration_params['large_rect_area'] = ui_obj.large_rect_area_label.text()
    calibration_params['small_rect_area'] = ui_obj.small_rect_area_label.text()
    calibration_params['rect_accuracy'] = ui_obj.rect_accuracy_label.text()

    return calibration_params


# image-processing functions in main-setting page
#---------------------------------------------------------------------------------------------------------------------------
# get image processing params from UI
def get_image_procesing_params_from_ui(ui_obj):
    """
    this function is used to get image-preprocessing params from main-setting page

    Args:
        ui_obj (_type_): main ui object

    Returns:
        image_procesing_params: in dict
    """

    image_procesing_params = {}
    split_size_w = ui_obj.splitsizew_spinBox.value()
    split_size_h = ui_obj.splitsizeh_spinBox.value()
    image_procesing_params['split_size'] = '[%s,%s]' % (split_size_w, split_size_h)

    return image_procesing_params


# defects functions in main-setting page
#---------------------------------------------------------------------------------------------------------------------------
# get image processing params from UI
def get_defects_params_from_ui(ui_obj):
    """
    this function is used to get defect params from main-setting page

    Args:
        ui_obj (_type_): main ui object

    Returns:
        defects_params: in dict
    """

    defects_params = {}
    defects_params['n_defect_colors'] = int(ui_obj.defect_colors_number_spin.value())

    return defects_params


# multitasking funcs
#----------------------------------------------------------------------------------------------------------------------------
def get_multitasking_params_from_ui(ui_obj):
    """
    this function is used to get multitasking params from main-setting page

    Args:
        ui_obj (_type_): main ui object

    Returns:
        multitasking_params: in dict
    """

    multitasking_params = {}
    #
    multitasking_params['camera_threads_value'] = ui_obj.camthread_spinBox.value()
    multitasking_params['camera_process_value'] = ui_obj.camprocess_spinBox.value()
    multitasking_params['camera_refresh_rate_value'] = ui_obj.wrtthread_spinBox.value()
    multitasking_params['writing_thread_value'] = ui_obj.refrate_spinBox.value()
    #
    return multitasking_params



# other functions to get main-setting parametrs from database
#---------------------------------------------------------------------------------------------------------------------------
# load/get main-setting parameters from database
def get_mainsetting_params_from_db(db_obj, mode='all'):
    """
    this function is used to get mainsetting params from database

    Args:
        db_obj (_type_): database object
        mode (str, optional): select mode to return specific parameters from database. Defaults to 'all'.
            'all': returns
                all_params, multitasking params
            'px_calibration'
                rect_areas, rect_acc

    Returns:
        depending on mode
            'all': returns
                all_params, multitasking params
            'px_calibration'
                rect_areas, rect_acc
    """

    params = db_obj.load_general_setting_params()
    if mode == 'all':
        params_multitasking = db_obj.load_general_setting_params(is_mutitaskiing_params=True)
        return params, params_multitasking

    elif mode == 'px_calibration':
        large_rect_area = params['large_rect_area']
        small_rect_area = params['small_rect_area']
        rect_acc = params['rect_accuracy']
        rect_acc = params['rect_accuracy']
        rect_areas = [large_rect_area, large_rect_area, large_rect_area, small_rect_area, small_rect_area, small_rect_area]
        return rect_areas, rect_acc    


# set main-setting parameters to database
def set_mainsetting_params_to_db(db_obj, apperance_params, is_multitask_params=False):
    """
    this function is used to update/set mainsetting params to database

    Args:
        db_obj (_type_): daabase object
        apperance_params (_type_): params, could be appearance, calibration, image-preprocessing and ...
        is_multitask_params (bool, optional): a boolean determining wheather the input params are belonge to multitasking or not. Defaults to False.

    Returns:
        resault: resualts of updating on database
    """

    if is_multitask_params:
        res = db_obj.update_general_setting_params(apperance_params, is_mutitaskiing_params=is_multitask_params)

    else:
        res = db_obj.update_general_setting_params(apperance_params)

    return res # validation




