from distutils.debug import DEBUG
import logging
import os

from . import date_funcs


class app_logger():
    def __init__(self, name='saba_setting-app_logger', log_mainfolderpath='./app_logs', console_log=True):
        """
        This class initializes a logger object that will be used for logging all things happening in the program. The logs are written in a log file, and can be shown
        in the console too. The logs are saved daya by day, and on every app start/close

        :param name: logger object name (in string)
        :param log_mainfolderpath: main folder path to create logs (in string)
        :param console_log: a boolean value to wheter show or not show logs in console (in boolean)
        
        :returns: logger object        
        """

        # Create a custom logger
        self.logger = logging.getLogger(name)

        # create log folders and files
        self.console_log = console_log
        self.main_folderpath = log_mainfolderpath
        self.daily_folderpath = date_funcs.get_date(persian=True, folder_path=True)
        self.current_filepath = os.path.join(self.main_folderpath, self.daily_folderpath, date_funcs.get_datetime(persian=True, folder_path=True)+'.log')
        self.create_mainfolder()
        self.create_dailyfolder()

        # set log levels to write logs
        self.logger_level = logging.DEBUG
        self.console_level = logging.DEBUG
        self.file_level = logging.DEBUG
        self.logger.setLevel(self.logger_level)

        # current user
        self.current_username = 'root'

        # 1.Create log handlers
        # console handler
        if self.console_log:
            self.console_handler = logging.StreamHandler()
            self.console_handler.setLevel(self.console_level)

        # file handler
        self.file_handler = logging.FileHandler(filename=self.current_filepath, mode='w')
        self.file_handler.setLevel(self.file_level)

        # 2.Create formatters and add it to handlers (format of logging)
        # console formatter
        if self.console_log:
            self.console_format = logging.Formatter('%(levelname)s - %(message)s')
            self.console_handler.setFormatter(self.console_format)

        # file formatter
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
        """
        this function creates the main folder to store log files

        :returns: None
        
        """

        # create if not exist
        if not os.path.exists(self.main_folderpath):
            os.mkdir(self.main_folderpath)


    # create daily folders to create logs
    def create_dailyfolder(self):
        """
        this function creates day by day folders in the main folder, to sotring the log files of each day

        :returns: None
        """

        # create if not exist
        if not os.path.exists(os.path.join(self.main_folderpath, self.daily_folderpath)):
            os.mkdir(os.path.join(self.main_folderpath, self.daily_folderpath))

    
    # create new log
    def create_new_log(self, message='nothing', level=1):
        """
        this function creates a log with input message and log level

        :param message: the log message (in string)
        :param level: the log level (in int), an int value between [0, 5] specifing the log level)
                0: debug
                1: info
                2: warning
                3: error
                4: critical error
                5: excepion error
        
        :returns: None
        """
        
        # get date and tme
        datetime = date_funcs.get_datetime(persian=True, folder_path=False)

        # do log by levels
        # debug
        if level == 0:
            self.logger.debug(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        # info
        elif level == 1:
            self.logger.info(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        # warning
        elif level == 2:
            self.logger.warning(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        # error
        elif level == 3:
            self.logger.error(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        # critical error
        elif level == 4:
            self.logger.critical(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))
        #
        # exception error (with logging exception message)
        elif level == 5:
            self.logger.exception(msg='%s - %s : %s\n------------------------------------------------------------------------------' % (datetime, self.current_username, message))

    
    # set current logged-in user to logger
    def set_current_user(self, current_username=None):
        """
        this function sets the input username as the current user of the app and logging

        :param current_username: current username logged-in the app (in string)
        
        :returns: None
        """
        
        self.current_username = current_username if current_username!=None else 'root'
        
        

    
if __name__ == "__main__":

    logger = app_logger()

    logger.create_new_log(message='hi', level=1)
    logger.create_new_log(message='hi2', level=1)