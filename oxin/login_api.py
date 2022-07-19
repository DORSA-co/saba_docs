# from backend import add_remove_label
from functools import partial
import cv2
from . import database_utils


from .backend import texts, colors_pallete


class API:
    """
    this class is used as the API for login window, to take login infoes from user and authenticate the user

    Inputs:
        ui: login ui object
        logger_obj: logger object to take logs of user authenticating and logging in
        language: the langage to show notifacations of the login

    Outputs: None
    """
    
    def __init__(self, ui, logger_obj=None, language='en'):
        self.ui = ui

        self.logger_obj = logger_obj # logger object
        self.language = language # language
        # username and password
        self.username = '' 
        self.password = ''
        
        # create database object to get user info from database and authenticate user
        self.db = database_utils.dataBaseUtils(logger_obj=logger_obj)

    #----------------------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------------------- 
    def button_connector(self):
        """
        function to connect buttons to their functions
        """
        
        # login button
        self.ui.login_btn.clicked.connect(partial(self.login))
        

    def login(self):
        """
        this function is used to authenticate an login the user to app

        Inputs: None

        Returns:
            result: a boolean value detrmining if the authentication done or not
            user_info: a dict containing infoes of the user
                {user_name: username in string, password: password in string}
        """
        
        # get enterd username and password from logon ui
        user, password = self.ui.get_user_pass()

        # check if both username and password are enterd
        if (user!='') and (password!=''):

            # check if there is any user in database with entered username, and if yes, get infoes (username and password) from database, to authenticate user
            user_info = self.db.search_user(user)

            try:
                
                # check if username exists on database and entered password is correct
                if len(user_info)!=0 and str(password)==user_info['password']:
                    # set login message
                    self.ui.set_login_message(text=texts.MESSEGES['login_success'][self.language], level=0)
                    cv2.waitKey(1000)

                    # clear fileds
                    self.ui.password.setText('')
                    self.ui.user_name.setText('')

                    # update current entered user infoes
                    self.username = user_info['user_name']
                    self.password = user_info['password']

                    return True, user_info

                # username or password incorrect, or failed to connect to database
                else:
                    try:
                        self.logger_obj.create_new_log(message='User tried to login with Incorrect Username or Password: %s - %s' % (str(user), str(password)), level=2)
                    except:
                        pass

                    self.ui.set_login_message(text=texts.ERRORS['username_password_incorrect'][self.language], level=2)
                    return False, 0

            # error
            except:
                self.ui.set_login_message(text=texts.ERRORS['user_authenticate_failed'][self.language], level=2)

        # username or password fields empty
        else:
            self.ui.set_login_message(text=texts.WARNINGS['username_password_empty'][self.language], level=1)
            return False, 0




    