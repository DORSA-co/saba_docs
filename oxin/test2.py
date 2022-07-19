# import sys
# from PySide6 import QtWidgets
# # from PySide2 import QtWidgets
# # from PyQt5 import QtWidgets
# from qt_material import apply_stylesheet

# # create the application and the main window
# app = QtWidgets.QApplication(sys.argv)
# window = QtWidgets.QMainWindow()

# # setup stylesheet
# apply_stylesheet(app, theme='dark_teal.xml')

# # run
# window.show()
# app.exec_()

# import PyQt5


# print(PyQt5.__version__)

# x='check_limit_1_btn'

# y=x.split('_',1)[1]
# print(y)
# # print(PyQt5.__version__)


# from distutils.dir_util import copy_tree

# # copy subdirectory example
# from_directory = "D:/995"
# i = 0

# while True:
#     to_directory = "D:/oxin_image_grabber/995_%s" % i
#     i+=1
#     print(to_directory)
#     copy_tree(from_directory, to_directory)

from wakeonlan import send_magic_packet
import os

ip='192.168.1.60'


turn_on=True
shut_down=False

if turn_on:

    send_magic_packet('18:C0:4D:DB:40:C9',ip_address=ip,port=9)

if shut_down :
    os.system('cmd /c "shutdown /s /m \\{} /t 1 /c"'.format(ip))
    

    # shutdown /s /m \\192.168.1.60 /t 120 /c