from PySide6.QtGui import QPixmap as sQPixmap
from PySide6.QtGui import QImage as sQImage

from . import texts


# logged-out icon
loggedout_icon = 'images/login_white.png'
loggedin_icon = 'images/logout_white.png'


#---------------------------------------------------------------------------------------------------------------------------


# function for changing UI buttons enabled or disabled given the user login/logout
def set_app_buttons_enable_or_disable(names, enable=True):
    """
    this function is used to enable/disable ui elements, by taking input elements as list of names

    Inputs:
        names: ui element names (list of strings)
        enable: a boolean determining wheather to enable/disable the elements
    
    :returns: None
    """
    
    for name in names:
        name.setEnabled(enable)


# logout user
def logout_user(ui_obj, confirm_ui_obj, login_api_obj):
    """
    this function is used to logout user from the app, and disable/lock ui after logout

    Inputs:
        ui_obj: main ui object
        confirm_ui_obj:
        login_api_obj:
    
    :returns: None
    """
    
    #
    ui_obj.logger.create_new_log(message='User logged-out with username: %s.' % (login_api_obj.username), level=1)
    ui_obj.logger.set_current_user(current_username=None) # set logger user to default (root)

    # disabling all buttons (sections) in the UI
    set_app_buttons_enable_or_disable(ui_obj.dash_buttons, False)
    set_app_buttons_enable_or_disable(ui_obj.side_buttons, False)

    # flag to determine user is loggedin or not
    ui_obj.login_flag = False

    # change login/logout icon
    try:
        ui_obj.main_login_btn.setIcon(sQPixmap.fromImage(sQImage(loggedout_icon)))
    except Exception as e:
        ui_obj.logger.create_new_log(message=texts.WARNINGS['change_login_button_icon_failed']['en'], level=2)

    # go to dashboard section to restrict access
    ui_obj.stackedWidget.setCurrentWidget(ui_obj.page_dashboard)
    
    # close confirmation window
    confirm_ui_obj.close()


# authenticating the user on login
def authenticate_user(ui_obj, login_ui_obj, login_api_obj, api_obj):
    """
    this function is used to authenticate the user,
    it takes the autintication results from login API, and if user be autenticated, enables/unlocks ui for user to work with

    Inputs:
        ui_obj: main ui object
        login_ui_obj:
        login_api_obj:
        api_obj: main API object
    
    :returns: None
    """
    
    # authenticate user
    try:
        allowed, user_info = login_api_obj.login()
    except Exception as e:
        ui_obj.logger.create_new_log(message=texts.ERRORS['database_login_failed']['en'], level=5)

    # user authenticated given username and password
    if allowed:
        # set current user as logger user
        ui_obj.logger.set_current_user(current_username=login_api_obj.username)
        ui_obj.logger.create_new_log(message='User logined with username: %s.' % (user_info['user_name']), level=1)

        # close login window
        login_ui_obj.close()

        # flag to determine user is loggedin or not
        ui_obj.login_flag = True
        ui_obj.current_username_label.setText(str(user_info['user_name']))

        # enabling all buttons (sections) in the UI
        set_app_buttons_enable_or_disable(ui_obj.dash_buttons, True)
        set_app_buttons_enable_or_disable(ui_obj.side_buttons, True)

        # change login/logout icon
        try:
            ui_obj.main_login_btn.setIcon(sQPixmap.fromImage(sQImage(loggedin_icon)))
        except Exception as e:
            ui_obj.logger.create_new_log(message=texts.WARNINGS['change_login_button_icon_failed']['en'], level=2)
        
        # user login message
        api_obj.notif_manager.create_new_notif(massage=texts.MESSEGES['user_logged_in'][ui_obj.language], win_color=api_obj.win_color, font_size=api_obj.font_size, font_style=api_obj.font_style, level=0)



# running and showing user login window
def run_login_window(ui_obj, login_ui_obj, confirm_ui_obj):
    """
    this function is used to run/show login window for user login

    Inputs:
        ui_obj: the main ui object
        login_ui_obj:
        confirm_ui_obj:
    
    :returns: None
    """
    
    # chcek whereas user is logged in or not
    if not ui_obj.login_flag:
        login_ui_obj.show()

    # user is logged in, so the logout confirm ui most be shown/run
    else: 
        confirm_ui_obj.msg_label.setText(texts.WARNINGS['logout_confirm_message'][ui_obj.language])
        # load conformation window to confirm logging out
        confirm_ui_obj.show()
    



