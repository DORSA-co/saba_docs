from PySide6.QtWidgets import QHeaderView as sQHeaderView
from PySide6.QtWidgets import QTableWidgetItem as sQTableWidgetItem
from PySide6 import QtCore as sQtCore

from .backend import texts, date_funcs


# users table number of rows and cols
users_table_ncols = 2
users_table_nrows = 20
user_name_max_len = 10
user_name_min_len = 4
headers = ['Username', 'User Role']
#
default_user_roles = ["DORSA", "Admin", "Operator"]

#---------------------------------------------------------------------------------------------------------------------------
# get users from database
def get_users_from_db(db_obj):
    """
    this function is used to get users list from database

    Inputs: None

    Returns:
        users_list: list of users (in dict)
    """
    
    users_list = db_obj.load_users()
    return users_list


# remove users from database
def remove_users_from_db(db_obj, users_list):
    """
    this function is used to remove input users from database

    Args:
        db_obj (_type_): database object
        users_list (_type_): list of user_names

    Returns:
        results: a boolean determining if the removing is ok
    """

    res = db_obj.remove_users(users_list)
    return res


# add user to database
def add_new_user_to_db(db_obj, new_user_info):
    """
    this function is used to add a new user to database

    Args:
        db_obj (_type_): database object
        new_user_info (_type_): in dict

    Returns:
        resault: a boolean determining if the user is added to database
    """
    
    res = db_obj.add_user(new_user_info)
    return res


# show/set user infoes to UI
def set_users_on_ui(ui_obj, users_list):
    """
    this function is used to set input users list to ui users table

    Inputs:
        ui_obj: main ui object
        users_list: list of users (in dict)
    
    Returns: None
    """
    
    # definr table parameters
    ui_obj.tableWidget_users.resizeColumnsToContents()
    ui_obj.tableWidget_users.setColumnCount(users_table_ncols)
    if len(users_list) != 0:
        ui_obj.tableWidget_users.setRowCount(users_table_nrows)
    else:
        ui_obj.tableWidget_users.setRowCount(0)
    ui_obj.tableWidget_users.verticalHeader().setVisible(True)
    ui_obj.tableWidget_users.horizontalHeader().setSectionResizeMode(sQHeaderView.Stretch)
    ui_obj.tableWidget_users.setHorizontalHeaderLabels(ui_obj.translate_headers_list(header_list=headers))

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
    """
    this function is used to show user infoes summary on dashboard

    Args:
        ui_obj (_type_): main ui object
        db_obj (_type_): database object
    """

    try:

        # get users-list from database
        users_list = get_users_from_db(db_obj)
        ui_obj.show_mesagges(ui_obj.count_users, text=str(len(users_list)), level=0, clearable=False, prefix=False)
    
    except:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['users_summary_failed']['en'], level=5)
        return


# get selected users from user table in UI
def get_selected_users(ui_obj, users_list):
    """
    this function is used to get selected users from users table in ui

    Args:
        ui_obj (_type_): main ui object
        users_list (_type_): list of users (in dict)

    Returns:
        selected_users: list of selected users user_names
    """

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
    """
    this funcion is used to get user info from ui add user fileds

    Args:
        ui_obj (_type_): main ui object

    Returns:
        user_info: in dict

    """
    try:
        # get user-infoes from UI
        user_info = {}
        user_info['user_name'] = ui_obj.user_id.text()
        user_info['password'] = ui_obj.user_pass.text()
        user_info['re_password'] = ui_obj.user_re_pass.text()
        user_info['role'] = ui_obj.user_role.currentText()
        user_info['date_created'] = date_funcs.get_date()

        return user_info

    except:

        return ('','0','1','')


# validate new user username
def new_user_info_validation(ui_obj, db_obj, user_info, default_user=False):
    """
    this function is used to validate new user info, to be in right format and be unique

    Args:
        ui_obj (_type_): main ui object
        db_obj (_type_): database object
        user_info (_type_): input user_info (in dict)
        default_user (bool, optional): a boolean to determine if input user info is for default admin user. Defaults to False.

    Returns:
        message: the text message of validating user_info
        message_level: an int value in range [0, 2] determioning the level of messege
    """

    # check fields not empty
    if user_info['password'] == '' or user_info ['re_password'] == '' or user_info['user_name'] == '':
        return texts.WARNINGS['fields_empty'][ui_obj.language], 1

    # check password and re-entered password be the same
    if user_info['password'] == user_info ['re_password']:

        # check username and password length
        if (len(user_info['user_name']) > user_name_max_len or len(user_info['user_name']) < user_name_min_len) and not default_user:
            return texts.WARNINGS['username_len'][ui_obj.language] + ' (%s, %s)' % (user_name_min_len, user_name_max_len), 1
        #
        if (len(user_info['password']) > user_name_max_len or len(user_info['password']) < user_name_min_len) and not default_user:
            return texts.WARNINGS['password_len'][ui_obj.language] + ' (%s, %s)' % (user_name_min_len, user_name_max_len), 1

        # check username to be unique
        users_list = get_users_from_db(db_obj=db_obj)
        for user in users_list:
            if user['user_name'].lower() == user_info['user_name'].lower():
                return texts.ERRORS['username_invalid'][ui_obj.language], 2
            

        return 'True', 0
        #user_info = db_obj.search_user_by_user_name(user_info['user_id'])
        # if len(user_info) == 0:
        #     return 'True'
        # else:
        #     return 'Invalid/Duplicate Username'
    else:

        return texts.WARNINGS['passwords_match'][ui_obj.language], 2


