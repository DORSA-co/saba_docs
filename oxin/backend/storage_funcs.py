import shutil
import os
from pathlib import Path
import subprocess
import string
from PySide6.QtGui import QStandardItem as sQStandardItem

from . import colors_pallete, mainsetting_funcs, texts



storage_check_interval = 20000 # in ms
#---------------------------------------------------------------------------------------------------------------------------


# show storage status summary on dashboard
def get_storage_status(disk_path):
    total, used, free = shutil.disk_usage(disk_path)
    # Get the current working directory
    current_working_directory = os.getcwd()[:2]
    drivename = get_drivename(current_working_directory)
    #
    total = total//(2**30)
    used = (total) - (free // (2**30))
    drive_info = {'total': total, 'used': used, 'used_perc': used/total}
    return drive_info

    
# get drive-name given drive letter 
def get_drivename(driveletter):
    return subprocess.check_output(["cmd","/c vol " + driveletter]).decode().split("\r\n")[0].split(" ").pop()


# get available drives on windows
def get_available_drives():
    available_drives = ['%s:' % d for d in string.ascii_uppercase if os.path.exists('%s:' % d)]
    return available_drives


# show available drives on ui camera live drive combo box 
def update_camera_live_drive_combo(ui_obj, available_drives):
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
    # update on db
    res = mainsetting_funcs.set_mainsetting_params_to_db(db_obj=db_obj, apperance_params=drive_infos)
    return res


#
def get_camera_live_drive_parameters_from_db(db_obj):
    # get params from db
    drive_infos = db_obj.load_general_setting_params()
    return drive_infos


def get_camera_live_drive_parameters_from_ui(ui_obj):
    # get drive params from ui
    drive_infos = {}
    drive_infos['camera_live_drive'] = ui_obj.cam_live_drive_combo.currentText()
    drive_infos['live_drive_max_used_ratio'] = ui_obj.cam_live_drive_thrs_spin.value() 
    drive_infos['live_drive_remove_stop_ratio'] = ui_obj.cam_live_drive_thrs_spin_2.value()
    # validate
    if drive_infos['live_drive_max_used_ratio'] <= drive_infos['live_drive_remove_stop_ratio']:
        ui_obj.show_mesagges(ui_obj.cam_live_drive_label, texts.WARNINGS['min_bigger_than_max'][ui_obj.language], level=1)
        return False, drive_infos

    elif ui_obj.cam_live_drive_combo.currentIndex() == 0:
        ui_obj.show_mesagges(ui_obj.cam_live_drive_label, texts.WARNINGS['default_drive_select'][ui_obj.language], level=1)
        return False, drive_infos

    return True, drive_infos


def get_files_in_path(dir_path, reverse=False):
    file_paths = sorted(Path(dir_path).iterdir(), key=os.path.getmtime, reverse=reverse)
    return file_paths

# get foldernames sor
def remove_old_files_in_directory(api_obj, ui_obj, drive_path, dir_path, start_ratio, stop_ratio, reverse=False):
    if stop_ratio > 1:
        stop_ratio /= 100
    flag = False
    itr = 0

    # get filenames
    while get_storage_status(disk_path = drive_path)['used_perc'] >= stop_ratio:
        #
        used_perc = round(get_storage_status(disk_path = drive_path)['used_perc'], 2)

        # if used_perc >= start_ratio:
        #     ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=2, clearable=False, prefix=False)
        # elif used_perc >= stop_ratio:
        #     ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=1, clearable=False, prefix=False)
        # else:
        #     ui_obj.show_mesagges(ui_obj.curr_used_space_label, str(used_perc), level=0, clearable=False, prefix=False)

        # get file pathes
        file_paths = get_files_in_path(dir_path=dir_path, reverse=reverse)
        
        if len(file_paths) == 0:
            #ui_obj.show_mesagges(ui_obj.cam_live_drive_label_2, texts.WARNINGS['drive_fulled_with_other_content'][ui_obj.language], level=2, clearable=False)
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
        #ui_obj.show_mesagges(ui_obj.cam_live_drive_label_2, texts.MESSEGES['storage_cleared'][ui_obj.language], clearable=False, level=0)
        #api_obj.notif_manager.create_new_notif(massage='Old files cleared, space available now', win_color=api_obj.win_color, font_size=api_obj.font_size, font_style=api_obj.font_style)


    