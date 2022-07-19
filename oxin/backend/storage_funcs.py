import shutil
import os
from pathlib import Path
import subprocess
import string
from PySide6.QtGui import QStandardItem as sQStandardItem

from .backend import mainsetting_funcs, texts, storage_funcs


# stirage check interval key in startup json dict
storage_check_interval_key = 'storage_check_interval' # in ms

#---------------------------------------------------------------------------------------------------------------------------


# show storage status summary on dashboard
def get_storage_status(disk_path):
    """
    this function is used to get storage statues of one drive

    Args:
        disk_path (_type_): drive path (in string)

    Returns:
        drive_info: in dict
    """
    total, used, free = shutil.disk_usage(disk_path)
    # Get the current working directory
    current_working_directory = os.getcwd()[:2]
    drivename = get_drivename(current_working_directory)
    #
    total = total//(2**30)
    free = free//(2**30)
    used = total - free
    drive_info = {'total': total, 'used': used, 'used_perc': used/total, 'free': free}

    return drive_info

    
# get drive-name given drive letter 
def get_drivename(driveletter):
    """
    this function is used to get drive name using its letter

    Args:
        driveletter (_type_): in string

    Returns:
        drive_name: in string
    """

    return subprocess.check_output(["cmd","/c vol " + driveletter]).decode().split("\r\n")[0].split(" ").pop()


# get available drives on windows
def get_available_drives():
    """
    this function is used to get system available drives list

    Args: None

    Returns:
        available_drives: in list
    """

    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    return available_drives


# show available drives on ui camera live drive combo box 
def update_camera_live_drive_combo(ui_obj, available_drives):
    """
    this function is used to update existing drives combobox on storage setting age

    Args:
        ui_obj (_type_): main ui object
        available_drives (_type_): list of available drives
    """

    available_drives = get_available_drives()
    ui_obj.cam_live_drive_combo.clear()
    #
    item = sQStandardItem('No Drive')
    ui_obj.cam_live_drive_combo.model().appendRow(item)

    #
    for drive_name in available_drives:
        item = sQStandardItem(drive_name)
        ui_obj.cam_live_drive_combo.model().appendRow(item)


#
def set_camera_live_drive_parameters_to_db(db_obj, drive_infos):
    """
    this function is used to set/update drive setting params on database

    Args:
        db_obj (_type_): database object
        drive_infos (_type_): in dict

    Returns:
        resault: boolean deermining whather set to database is ok
    """

    # update on db
    res = mainsetting_funcs.set_mainsetting_params_to_db(db_obj=db_obj, apperance_params=drive_infos)

    return res


#
def get_camera_live_drive_parameters_from_db(db_obj):
    """
    this function is used to get camera live drive parameters from database

    Args:
        db_obj (_type_): database object

    Returns:
        drive_infoes: app general parameters (in dict)
    """
    # get params from db
    drive_infos = db_obj.load_general_setting_params()

    return drive_infos


def get_camera_live_drive_parameters_from_ui(ui_obj):
    """
    this function is used to get defeault storage setting params from ui

    Args:
        ui_obj (_type_): main ui object

    Returns:
        resaule: a boolean determining if the parameters are validated or not
    """
    # get drive params from ui
    drive_infos = {}
    drive_infos['camera_live_drive'] = ui_obj.cam_live_drive_combo.currentText()
    drive_infos['live_drive_max_used_ratio'] = ui_obj.cam_live_drive_thrs_spin.value() 
    drive_infos['live_drive_remove_stop_ratio'] = ui_obj.cam_live_drive_thrs_spin_2.value()
    #
    # time nterval to check storage statues
    storage_check_interval = ui_obj.cam_live_drive_interval_spin.value()

    # validation drive thresholds
    if drive_infos['live_drive_max_used_ratio'] <= drive_infos['live_drive_remove_stop_ratio']:
        ui_obj.show_mesagges(ui_obj.cam_live_drive_label, texts.WARNINGS['min_bigger_than_max'][ui_obj.language], level=1)
        return False, drive_infos, storage_check_interval

    # validation selected drive
    elif ui_obj.cam_live_drive_combo.currentIndex() == 0:
        ui_obj.show_mesagges(ui_obj.cam_live_drive_label, texts.WARNINGS['default_drive_select'][ui_obj.language], level=1)
        return False, drive_infos, storage_check_interval

    return True, drive_infos, storage_check_interval


def get_files_in_path(dir_path, reverse=False):
    """
    this function is used to get all files in a path, sorted by date (old to new)

    Args:
        dir_path (_type_): _description_
        reverse (bool, optional): a boolean to reverse sorting to new to old. Defaults to False.

    Returns:
        file_paths: list of file pathes
    """

    file_paths = sorted(Path(dir_path).iterdir(), key=os.path.getmtime, reverse=reverse)
    return file_paths


# get foldernames sor
def remove_old_files_in_directory(api_obj, ui_obj, drive_path, dir_path, start_ratio, stop_ratio, reverse=False):
    """
    this function is used to remove old files in a directory

    Args:
        api_obj (_type_): _description_
        ui_obj (_type_): main ui object
        drive_path (_type_): _description_
        dir_path (_type_): directory of the folder in drive
        start_ratio (_type_): _description_
        stop_ratio (_type_): drive usage threshold to stop removing files
        reverse (bool, optional): boolean to reverse sorting files in directory. Defaults to False.

    Returns: None
    """

    if stop_ratio < 1:
        stop_ratio *= 100
    #
    if start_ratio < 1:
        start_ratio *= 100
    #
    flag = False
    itr = 0


    # remove files until storage statues gets ok
    while int(get_storage_status(disk_path = drive_path)['used_perc']*100) >= stop_ratio:
        #
        used_perc = int(get_storage_status(disk_path = drive_path)['used_perc']*100)

        if used_perc >= start_ratio and itr%20==0:
            ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=2, clearable=False, prefix=False)

        elif used_perc >= (stop_ratio+start_ratio)/2 and itr%20==0:
            ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=1, clearable=False, prefix=False)

        elif itr%20==0:
            ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=0, clearable=False, prefix=False)

        # get file pathes
        file_paths = get_files_in_path(dir_path=dir_path, reverse=reverse)
        
        # no files in input directory (folder)
        if len(file_paths) == 0:
            ui_obj.show_mesagges(ui_obj.cam_live_drive_label_2, texts.WARNINGS['drive_fulled_with_other_content'][ui_obj.language], level=2, clearable=False)
            # make a flag true to warn the user that drive is fulled with other contents rather than camera images
            flag = True
            break

        # remove the oldest one
        #print('removing:', file_paths[0])
        try:
            shutil.rmtree(file_paths[0])
        except:
            try:
                os.remove(file_paths[0])
            except:
                pass

        itr+=1
        if ui_obj.stackedWidget.currentWidget() == ui_obj.page_storage and itr%20==0:
            api_obj.refresh_storege_page(only_chart=True)

    api_obj.camera_live_storage_check_thread_lock = False
    api_obj.camera_live_storage_clear_flag = True

    if not flag:
        pass
        ui_obj.show_mesagges(ui_obj.cam_live_drive_label_2, texts.MESSEGES['storage_cleared'][ui_obj.language], clearable=False, level=0)
        #api_obj.notif_manager.create_new_notif(massage='Old files cleared, space available now', win_color=api_obj.win_color, font_size=api_obj.font_size, font_style=api_obj.font_style)


def show_storage_status(ui_obj, db_obj):
    """
    this functionis used tp update storage info summary on dashboard

    Args:
        ui_obj (_type_): main ui object
        db_obj (_type_): database object
    
    Returns: None
    """

    try:

        # get current drive for saving camera lives from db
        drive_info = get_camera_live_drive_parameters_from_db(db_obj=db_obj)

        # update current drive
        if drive_info['camera_live_drive'] == 'NULL':
            ui_obj.show_mesagges(ui_obj.dash_selected_drive_label, text=texts.ERRORS['drive_not_selected'][ui_obj.language], level=2, clearable=False, prefix=False)
            # clear fields
            ui_obj.show_mesagges(ui_obj.dash_storage_total_label, text='', level=0, clearable=False, prefix=False)
            ui_obj.show_mesagges(ui_obj.dash_storage_used_label, text='', level=0, clearable=False, prefix=False)
            ui_obj.show_mesagges(ui_obj.dash_storage_free_label, text='', level=0, clearable=False, prefix=False)

            return

        else:
            ui_obj.show_mesagges(ui_obj.dash_selected_drive_label, text=drive_info['camera_live_drive'], level=0, clearable=False, prefix=False)

            # update space stautes
            drive_statues = get_storage_status(disk_path=drive_info['camera_live_drive'])
            # total
            ui_obj.show_mesagges(ui_obj.dash_storage_total_label, text=str(drive_statues['total']), level=0, clearable=False, prefix=False)

            # used and free
            if drive_statues['used_perc'] >= drive_info['live_drive_max_used_ratio']:
                ui_obj.show_mesagges(ui_obj.dash_storage_used_label, text=str(drive_statues['used']), level=2, clearable=False, prefix=False)
                ui_obj.show_mesagges(ui_obj.dash_storage_free_label, text=str(drive_statues['free']), level=2, clearable=False, prefix=False)

            elif drive_statues['used_perc'] >= (drive_info['live_drive_max_used_ratio']+drive_info['live_drive_remove_stop_ratio'])/2:
                ui_obj.show_mesagges(ui_obj.dash_storage_used_label, text=str(drive_statues['used']), level=1, clearable=False, prefix=False)
                ui_obj.show_mesagges(ui_obj.dash_storage_free_label, text=str(drive_statues['free']), level=1, clearable=False, prefix=False)
            
            else:
                ui_obj.show_mesagges(ui_obj.dash_storage_used_label, text=str(drive_statues['used']), level=0, clearable=False, prefix=False)
                ui_obj.show_mesagges(ui_obj.dash_storage_free_label, text=str(drive_statues['free']), level=0, clearable=False, prefix=False)

    
    except:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['storage_summary_failed']['en'], level=5)
        return
            





    