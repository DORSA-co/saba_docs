from distutils.debug import DEBUG
import logging
import os

from . import date_funcs


class app_logger():
    def __init__(self, name='saba_setting-app_logger', log_mainfolderpath='./app_logs', console_log=True):
        # Create a custom logger
        self.logger = logging.getLogger(name)

        # log folders and files
        self.console_log = console_log
        self.main_folderpath = log_mainfolderpath
        self.daily_folderpath = date_funcs.get_date(persian=True, folder_path=True)
        self.current_filepath = os.path.join(self.main_folderpath, self.daily_folderpath, date_funcs.get_datetime(persian=True, folder_path=True)+'.log')
        self.create_mainfolder()
        self.create_dailyfolder()

        # levels
        self.logger_level = logging.DEBUG
        self.console_level = logging.DEBUG
        self.file_level = logging.DEBUG
        self.logger.setLevel(self.logger_level)

        # current user
        self.current_username = 'root'

        # 1.Create handlers
        # comsole
        if self.console_log:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.console_level)
        # file
        self.file_handler = logging.FileHandler(filename=self.current_filepath, mode='w')
        self.file_handler.setLevel(self.file_level)

        # 2.Create formatters and add it to handlers
        # console
        if self.console_log:
            self.console_format = logging.Formatter('%(levelname)s - %(message)s')
            self.console_handler.setFormatter(self.console_format)
        # file
        self.file_format = logging.Formatter('%(levelname)s - %(message)s')
        self.file_handler.setFormatter(self.file_format)

        # 3.Add handlers to the logger
        # console
        if self.console_log:
            self.logger.addHandler(self.console_handler)
        # file
        self.logger.addHandler(self.file_handler)


    # create main folder to create logs 
    def create_mainfolder(self):
        # create if not exist
        if not os.path.exists(self.main_folderpath):
            os.mkdir(self.main_folderpath)


    # create daily folders to create logs
    def create_dailyfolder(self):
        # create if not exist
        if not os.path.exists(os.path.join(self.main_folderpath, self.daily_folderpath)):
            os.mkdir(os.path.join(self.main_folderpath, self.daily_folderpath))

    
    # create new log
    def create_new_log(self, message='nothing', level=1):
        datetime = date_funcs.get_datetime(persian=True, folder_path=False)
        # do by levels
        if level == 0:
            self.logger.debug(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        elif level == 1:
            self.logger.info(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        elif level == 2:
            self.logger.warning(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        elif level == 3:
            self.logger.error(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        elif level == 4:
            self.logger.critical(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        elif level == 5:
            self.logger.exception(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))

    
    def set_current_user(self, current_username=None):
        self.current_username = current_username if current_username!=None else 'root'
        
        

    
if __name__ == "__main__":

    logger = app_logger()

    logger.create_new_log(message='hi', level=1)
    logger.create_new_log(message='hi2', level=1)