# from sqlalchemy import false, true
from . import database
import datetime

import os


class dataBaseUtils():
    def __init__(self, logger_obj=None) :
        self.db = database.dataBase('root','root','localhost','saba_database', logger_obj=logger_obj)

        self.table_user='users'
        self.table_cameras = 'camera_settings'
        self.table_general_settings = 'settings'
        self.table_multitasking = 'multi_tasking'
        self.camera_id = 'id'
        self.setting_tabel = 'settings'
        self.general_settings_id = 'id'
        self.plc='plc_path'

        self.logger_obj = logger_obj


    #________________________________________________________________
    #
    #________________________________________________________________
    def search_user(self,input_user_name):
        try:
            record = self.db.search( self.table_user , 'user_name', input_user_name )[0]
            #print('asd',record)
            return record
        except:
            return []


    def search_camera_by_ip(self, input_camera_ip):
        try:
            record = self.db.search( self.table_cameras , 'ip_address', input_camera_ip)[0]
            #print('asd',record)
            return record
        except:
            return []


    def search_camera_by_serial(self, input_camera_serial):
        try:
            record = self.db.search( self.table_cameras , 'serial_number', input_camera_serial)[0]
            #print('asd',record)
            return record
        except:
            return []
    

    def load_cam_params(self, input_camera_id):
        try:
            record = self.db.search( self.table_cameras , 'id', input_camera_id )[0]
            return record
        except:
            return []
            

    def update_cam_params(self, input_camera_id, input_camera_params):
        try:
            for camera_param in input_camera_params.keys():
                res = self.db.update_record(self.table_cameras, camera_param, str(input_camera_params[camera_param]), self.camera_id, input_camera_id)
            return res
        except:
            return False


    def update_general_setting_params(self, input_setting_params, is_mutitaskiing_params=False):
        try:
            for param in input_setting_params.keys():
                if is_mutitaskiing_params:
                    res = self.db.update_record(self.table_multitasking, param, str(input_setting_params[param]), self.general_settings_id, '0')
                else:
                    res = self.db.update_record(self.table_general_settings, param, str(input_setting_params[param]), self.general_settings_id, '0')
            return res
        except:
            return False
    

    def load_general_setting_params(self, is_mutitaskiing_params=False):
        try:
            if is_mutitaskiing_params:
                record = self.db.search( self.table_multitasking , self.general_settings_id, '0' )[0]
            else:
                record = self.db.search( self.table_general_settings , self.general_settings_id, '0' )[0]
            #print('camera info:', record)
            return record
        except:
            return []



    def load_users(self):
        try:
            users=self.db.get_all_content('users')

            return users
        
        except:

            return []


    def remove_users(self,users_name):

        for i in range(len(users_name)):
            
            self.db.remove_record(col_name='user_name',id=users_name[i],table_name='users')

    def add_user(self,parms):
        data=(parms['user_name'],parms['password'],parms['role'])
        #print(data)
        try:
            self.db.add_record(data, table_name='users', parametrs='(user_name,password,role)', len_parameters=3)
            return 'True'
        
        except:
            return 'Databas Eror'

    
    def search_user_by_user_name(self, input_user_name):
        try:
            record = self.db.search( self.table_user , 'user_name', input_user_name)[0]
            #print('asd',record)
            return record
        except:
            return []



    def set_image_processing_parms(self,data):

        # print(data[0])
        # self.db.update_record(table_name='image_processing', col_name=col_name[i], value=data[col_name[i]], id='id', id_value='0')
        #print('asd',data)

        col_name=['block_size','defect','noise']

        #print('asdwqd',data[col_name[0]])

        for i in range(3):

            # print(data[i])

            self.db.update_record(table_name='image_processing', col_name=col_name[i], value=str(data[col_name[i]]), id='id', id_value='0')

        
    
    def load_defects(self):
        try:
            defects=self.db.get_all_content('defects_info')

            return defects
        
        except:

            return []
    
    def search_defect_by_id(self, input_defect_id):
        try:
            record = self.db.search( 'defects_info' , 'defect_ID', input_defect_id)[0]
            #print('asd',record)
            return record
        except:
            return []
    

    def search_defect_by_group_id(self, input_defect_id):
        try:
            record = self.db.search( 'defects_info' , 'groupp', input_defect_id)[0]
            #print('asd',record)
            return record
        except:
            return []
    

    def search_defect_by_name(self, input_defect_name):
        try:
            record = self.db.search( 'defects_info' , 'name', input_defect_name)[0]
            #print('asd',record)
            return record
        except:
            return []
    
    
    def search_defect_by_color(self, input_color):
        try:
            record = self.db.search( 'defects_info' , 'color', input_color)[0]
            #print('asd',record)
            return record
        except:
            return []
    
    def search_defect_by_short_name(self, input_defect_name):
        try:
            record = self.db.search( 'defects_info' , 'short_name', input_defect_name)[0]
            #print('asd',record)
            return record
        except:
            return []


    def search_defect_by_filter(self, parms, cols):
        try:
            record = self.db.search( 'defects_info' , cols, parms, multi=True)
            #print('asd',record)
            return record
        except:
            return []


    def add_defect(self,parms):
        data=(parms['name'],parms['short_name'],parms['defect_ID'],parms['is_defect'],parms['groupp'],parms['level'],parms['color'],parms['date'])
        #print(data)
        try:
            self.db.add_record(data, table_name='defects_info', parametrs='(name,short_name,defect_ID,is_defect,groupp,level,color,date)', len_parameters=8)
            #print('yes')
            return 'True'
        
        except:
            #print('no')
            return 'Databas Eror'


    def remove_defects(self,defect_ids):

        for i in range(len(defect_ids)):
            res = self.db.remove_record(col_name='defect_ID',id=defect_ids[i],table_name='defects_info')

        return res


    def remove_defects_by_group_id(self,defect_ids):

        for i in range(len(defect_ids)):
            
            res = self.db.remove_record(col_name='groupp',id=defect_ids[i],table_name='defects_info')
        
        return res


    def update_defect(self, input_defect_params):
        try:
            for param in input_defect_params.keys():
                res = self.db.update_record('defects_info', param, str(input_defect_params[param]), 'defect_ID', str(input_defect_params['defect_ID']))
            return res
        except:
            return False

    
    def load_defect_groups(self):
        try:
            defects=self.db.get_all_content('defect_groups')

            return defects
        
        except:

            return []
    

    def search_defect_group_by_id(self, input_defect_group_id):
        try:
            record = self.db.search( 'defect_groups' , 'defect_group_id', input_defect_group_id)[0]
            #print('asd',record)
            return record
        except:
            return []
    

    def search_defect_group_by_name(self, input_defect_group_name):
        try:
            record = self.db.search( 'defect_groups' , 'defect_group_name', input_defect_group_name)[0]
            #print('asd',record)
            return record
        except:
            return []
    
    def search_defect_group_by_filter(self, parms, cols):
        try:
            record = self.db.search( 'defect_groups' , cols, parms, multi=True)
            #print('asd',record)
            return record
        except:
            return []


    def add_defect_group(self,parms):
        data=(parms['defect_group_name'],parms['defect_group_id'],parms['is_defect'],parms['date_created'])
        #print(data)
        try:
            self.db.add_record(data, table_name='defect_groups', parametrs='(defect_group_name,defect_group_id,is_defect,date_created)', len_parameters=4)
            #print('yes')
            return 'True'
        
        except:
            #print('no')
            return 'Databas Eror'
    

    def update_defect_group(self, input_defect_params):
        try:
            for param in input_defect_params.keys():
                res = self.db.update_record('defect_groups', param, str(input_defect_params[param]), 'defect_group_id', str(input_defect_params['defect_group_id']))
            return res
        except:
            return False
        

    def remove_defect_groups(self,defect_ids):

        for i in range(len(defect_ids)):
            res = self.db.remove_record(col_name='defect_group_id',id=defect_ids[i],table_name='defect_groups')
        
        return res
    


    def get_dataset_path(self):
        record =self.db.search(table_name=self.setting_tabel,param_name='id',value=0)[0 ]
        return record['parent_path']


    def load_plc_parms(self):
        try:
            parms=self.db.get_all_content(self.plc)
            #print(parms)
            return parms

        except:
            return None


    def update_plc_parms(self, plc_parms):
        try:
            for _,param in enumerate(plc_parms.keys()):
                # update_record(self,table_name,col_name,value,id,id_value):
                #print('_',_,'   ',param)
                #print(plc_parms[param])

                try:
                    min_value = str(int(plc_parms[param][1]))
                except:
                    min_value = '-1'
                #
                try:
                    max_value = str(int(plc_parms[param][2]))
                except:
                    max_value = '-1'

                res = self.db.update_record(self.plc, 'path', str(plc_parms[param][0]), 'id', _)
                res = self.db.update_record(self.plc, 'min_or_off_value', min_value, 'id', _)
                res = self.db.update_record(self.plc, 'max_or_on_value', max_value, 'id', _)

            return res
        #
        except:
            return False


    def update_plc_ip(self,ip):

        try:
            res = self.db.update_record(self.setting_tabel, 'plc_ip', ip, 'id', 0)
            return res
        except:
            return False

    def load_plc_ip(self):
        try:
            record = self.db.search( self.setting_tabel , 'id', 0 )[0]
            return record['plc_ip']
        except:
            return False
       


if __name__ == '__main__':
    db = dataBaseUtils()
    # records = db.load_coil_info(996)
    # db.get_camera_setting()
    #db.set_dataset_path('G:/dataset/')
    # print(db.get_dataset_path())

    # db.get_path(['997', 'up', (5, 5)])
    # pass

    # db.load_cam_params('1')

    # x=db.load_users()

    # user=['ali']

    # db.remove_users(user)


    # x=db.get_dataset_path()
    x=db.load_plc_ip()
    print(x)

    # print(x)