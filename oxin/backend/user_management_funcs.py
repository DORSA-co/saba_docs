from PySide6.QtWidgets import QHeaderView as sQHeaderView
from PySide6.QtWidgets import QTableWidgetItem as sQTableWidgetItem
from PySide6 import QtCore as sQtCore

from . import texts


# users table number of rows and cols
users_table_ncols = 2
users_table_nrows = 20
headers = ['Username', 'User Role']

#---------------------------------------------------------------------------------------------------------------------------


# get users from database
def get_users_from_db(db_obj):
    users_list = db_obj.load_users()
    return users_list


# remove users from database
def remove_users_from_db(db_obj, users_list):
    res = db_obj.remove_users(users_list)
    return res


# add user to database
def add_new_user_to_db(db_obj, new_user_info):
    res = db_obj.add_user(new_user_info)
    return res


# show/set user infoes to UI
def set_users_on_ui(ui_obj, users_list):
    # definr table parameters
    ui_obj.tableWidget_users.resizeColumnsToContents()
    ui_obj.tableWidget_users.setColumnCount(users_table_ncols)
    if len(users_list) != 0:
        ui_obj.tableWidget_users.setRowCount(users_table_nrows)
    else:
        ui_obj.tableWidget_users.setRowCount(0)
    ui_obj.tableWidget_users.verticalHeader().setVisible(True)
    ui_obj.tableWidget_users.horizontalHeader().setSectionResizeMode(sQHeaderView.Stretch)
    ui_obj.tableWidget_users.setHorizontalHeaderLabels(headers)
    # add users to table
    for i, user in enumerate(users_list):
        # set username
        table_item = sQTableWidgetItem(str(user['user_name']))
        table_item.setFlags(sQtCore.Qt.ItemFlag.ItemIsUserCheckable | sQtCore.Qt.ItemFlag.ItemIsEnabled)
        table_item.setCheckState(sQtCore.Qt.CheckState.Unchecked)
        ui_obj.tableWidget_users.setItem(i, 0, table_item)
        # set user-role
        table_item = sQTableWidgetItem(str(user['role']))
        ui_obj.tableWidget_users.setItem(i, 1, table_item)
    ui_obj.tableWidget_users.setRowCount(i+1)


# show users summary info on dashboard
def show_users_summary_info(ui_obj, db_obj):
    # get users-list from database
    users_list = get_users_from_db(db_obj)
    ui_obj.count_users.setText(str(len(users_list)))


# get selected users from user table in UI
def get_selected_users(ui_obj, users_list):
    list = []
    for i in range(ui_obj.tableWidget_users.rowCount()):    
        if ui_obj.tableWidget_users.item(i, 0).checkState() == sQtCore.Qt.Checked:
            list.append(i)
    selected_users = []
    for i in range (len(list)):
        selected_users.append(users_list[list[i]]['user_name'])
    return selected_users


# get new user information from window (add user)
def get_user_info_from_ui(ui_obj):
    try:
        # get user-infoes from UI
        user_info = {}
        user_info['user_name'] = ui_obj.user_id.text()
        user_info['password'] = ui_obj.user_pass.text()
        user_info['re_password'] = ui_obj.user_re_pass.text()
        user_info['role'] = ui_obj.user_role.currentText()
        return user_info
    except:
        return ('','0','1','')


# validate new user username
def new_user_info_validation(ui_obj, db_obj, user_info):
    # check fields not empty
    if user_info['password'] == '' or user_info ['re_password'] == '' or user_info['user_name'] == '':
        return texts.WARNINGS['fields_empty'][ui_obj.language]

    # check password and re-entered password be the same
    if user_info['password'] == user_info ['re_password']:
        # check username to be unique
        users_list = get_users_from_db(db_obj=db_obj)
        for user in users_list:
            if user['user_name'].lower() == user_info['user_name'].lower():
                return texts.ERRORS['username_invalid'][ui_obj.language]

        return 'True'
        #user_info = db_obj.search_user_by_user_name(user_info['user_id'])
        # if len(user_info) == 0:
        #     return 'True'
        # else:
        #     return 'Invalid/Duplicate Username'
    else:
        return texts.WARNINGS['passwords_match'][ui_obj.language]


