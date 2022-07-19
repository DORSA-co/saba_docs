# from backend import add_remove_label
from functools import partial
import cv2
from . import database_utils





#down_side_technical     ,   up_side_technical
class API:

    def __init__(self, ui, logger_obj=None):
        self.ui = ui
        self.logger_obj = logger_obj
        self.username = ''
        self.password = ''

        #-------------------------------------
        #connet buttons to correspondings functions in API               ////////////////////
        # self.button_connector()
        #connet mouse event to correspondings functions in API
        self.db = database_utils.dataBaseUtils(logger_obj=logger_obj)

    #----------------------------------------------------------------------------------------
    # 
    #---------------------------------------------------------------------------------------- 
    def button_connector(self):
        self.ui.login_btn.clicked.connect(partial(self.login))
        

    def login(self):
        user, password = self.ui.get_user_pass()

        if (user!='') and (password!=''):

            user_info = self.db.search_user(user)

            try:

                if len(user_info)!=0 and str(password)==user_info['password']:
                    #print('ok')
                    
                    self.ui.set_login_message('Login Successfully','019267')
                    cv2.waitKey(1000)
                    self.ui.password.setText('')
                    self.ui.user_name.setText('')

                    self.ui.set_login_message('','019267')

                    self.username = user_info['user_name']
                    self.password = user_info['password']
                    return True, user_info

                else:
                    try:
                        self.logger_obj.create_new_log(message='User tried to login with Incorrect Username or Password: %s - %s' % (str(user), str(password)), level=2)
                    except:
                        pass

                    self.eror_login('Username or Password Incorrect')
                    return False, 0

            except:
                self.eror_login()
        else:
            self.eror_login('Username or Password Empty')
            return False, 0


    def eror_login(self,message='Username or Password Empty',color='FF1700'):
        #self.ui.password.setText('')
        self.ui.set_login_message(message, color)


    