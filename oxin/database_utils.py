from . import database


class dataBaseUtils():
    """
    this class is used as an API to work with database

    Inputs:
        logger_obj: the logger object to take loggs

    :returns:
        database object
    """
    
    def __init__(self, logger_obj=None) :
        self.db = database.dataBase('root','Dorsa1400@','localhost','saba_database', logger_obj=logger_obj)

        # table names
        self.table_user = 'users'
        self.table_cameras = 'camera_settings'
        self.table_general_settings = 'settings'
        self.table_multitasking = 'multi_tasking'
        self.table_defects = 'defects_info'
        self.table_defect_groups = 'defect_groups'
        self.setting_tabel = 'settings'
        self.plc='plc_path'

        self.camera_id = 'id'
        self.defect_group_id = 'defect_group_id'
        self.general_settings_id = 'id'
        self.user_id = 'user_name'
        self.defect_id = 'defect_ID'
        self.defect_shortname = 'short_name'
        self.defect_name = 'name'
        

        # logger object
        self.logger_obj = logger_obj


    #________________________________________________________________
    #
    #________________________________________________________________
    def search_user(self, input_user_name):
        """
        this funcion is used to search if any user is available in users table with input username,
        if username is vailable, user info are returened,
        else an empty list is returned

        Inputs:
            input_user_name: input username to search (in string)
        
        :returns:
            user_info: a dict containing user info:
                {user_name: username in string, password: password in string}
        """
        
        try:
            record = self.db.search(self.table_user, self.user_id, input_user_name)[0]
            return record

        except:
            # return emoty list if failed to connect to database
            return []


    def search_camera_by_ip(self, input_camera_ip):
        """
        this function is used to search camera by its ip

        Args:
            input_camera_ip (_type_): in string

        :returns:
            record: dict f camera params of camera with input ip
        """

        try:
            record = self.db.search( self.table_cameras , 'ip_address', input_camera_ip)[0]
            #print('asd',record)
            return record

        except:
            return []


    def search_camera_by_serial(self, input_camera_serial):
        """
        this function is used to search camera by its serial

        Args:
            input_camera_serial (_type_): in string

        :returns:
            record: dict f camera params of camera with input serila
        """

        try:
            record = self.db.search( self.table_cameras , 'serial_number', input_camera_serial)[0]
            #print('asd',record)
            return record

        except:
            return []
    

    def load_cam_params(self, input_camera_id):
        """
        this function is used to load camear parameters from camera tables, using the camera id

        Inputs:
            input_camera_id: id of camera (in string)
        
        :returns:
            camera_params: a dict containing camera parameters
        """
        
        try:
            record = self.db.search( self.table_cameras , 'id', input_camera_id )[0]
            return record

        except:
            return []
            

    def update_cam_params(self, input_camera_id, input_camera_params):
        """
        this function is used to update camera params of input camera id on table

        Inputs:
            input_camera_id: id of crrent camera (in string)
            input_camera_params: camera parameters (in dict)

        :returns:
            result: a bolean value determining if the settings are updated on database or not
        """
        
        try:
            # update one column in table each time
            for camera_param in input_camera_params.keys():
                res = self.db.update_record(self.table_cameras, camera_param, str(input_camera_params[camera_param]), self.camera_id, input_camera_id)
            #
            return res

        except:
            return False


    def update_general_setting_params(self, input_setting_params, is_mutitaskiing_params=False):
        """
        this function is used to update general-setting params on table

        Args:
            input_setting_params (_type_): _description_
            is_mutitaskiing_params (bool, optional): a boolean to determine if params are belong to multitask params. Defaults to False.

        :returns:
            resault: a boolean determining if the update is done
        """
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
        """
        this function is used to get general-settings params from table

        Args:
            is_mutitaskiing_params (bool, optional): a boolean determining wheather to load multitasing params from multitasking table. Defaults to False.

        :returns:
            record: list of one dict
        """

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
        """
        this function is used to load users list from database

        Inputs: None

        :returns:
            users_list: list of users (in dict)
        """
        
        try:
            users=self.db.get_all_content(self.table_user)

            return users
        
        except:

            return []


    def remove_users(self, users_name):
        """
        this function is used to remove input users from database

        Args:
            users_name (_type_): list of user_names
        
        :returns: None
        """

        for i in range(len(users_name)):
            res = self.db.remove_record(col_name=self.user_id,id=users_name[i],table_name=self.table_user)
        
        return res


    def add_user(self, parms):
        """
        this function is used to add a new user to users table

        Args:
            parms (_type_): user infoes (in dict)

        :returns:
            resault: a text message determining if the user is added
                "True":
                'Databas Eror':
        """

        data=(parms[self.user_id], parms['password'], parms['role'], parms['date_created'])
        
        try:
            self.db.add_record(data, table_name=self.table_user, parametrs='(user_name,password,role,date_created)', len_parameters=4)
            return 'True'
        
        except:
            return 'Databas Eror'

    
    def search_user_by_user_name(self, input_user_name):
        """
        this function is used to search a user by its usrnam

        Args:
            input_user_name (_type_): in string

        :returns:
            record: user_info (in dict)
        """
        try:
            record = self.db.search( self.table_user , self.user_id, input_user_name)[0]
            #print('asd',record)
            return record

        except:
            return []


    def get_image_processing_parms(self):
        """
        this function is used to set input image processing params for Miss.Abtahi algo to database

        Args:
            data (_type_): image processing params
        
        :returns: image_procesing_params
        """

        try:
            record = self.db.search( 'image_processing' , 'id', '0')[0]
            #print('asd',record)
            return record

        except:
            return []


    def set_image_processing_parms(self, data):
        """
        this function is used to get input image processing params for Miss.Abtahi algo to database

        Args:
            data (_type_): image processing params
        
        :returns: None
        """

        col_name=['block_size','defect','noise', 'noise_flag']
        #print('asdwqd',data[col_name[0]])
        for i in range(len(col_name)):
            # print(data[i])
            res = self.db.update_record(table_name='image_processing', col_name=col_name[i], value=str(data[col_name[i]]), id='id', id_value='0')
        
        return res

        
    
    def load_defects(self):
        """
        this function is used to get all defects from defects table

        :returns:
            defects: list of defects (in dict)
        """

        try:
            defects=self.db.get_all_content(self.table_defects)
            return defects
        
        except:
            return []
    

    def search_defect_by_id(self, input_defect_id):
        """
        this function is used to serach a defect in database, according to its defect-id

        Args:
            input_defect_id (_type_): in string

        :returns:
            defect_info: a list with single record (in dict)
        """
        try:
            record = self.db.search( self.table_defects , self.defect_id, input_defect_id)[0]
            #print('asd',record)
            return record

        except:
            return []
    

    def search_defect_by_group_id(self, input_defect_id):
        """
        this function is used to search defects with specific defect-group-id

        Args:
            input_defect_id (_type_): input defect-group-id

        :returns:
            defects_info: a list of defect_infoes (in dict)
        """
        try:
            record = self.db.search( self.table_defects , 'groupp', input_defect_id)[0]
            #print('asd',record)
            return record

        except:
            return []
    

    def search_defect_by_name(self, input_defect_name):
        """
        this function is used to search a defect by its name in database

        Inputs:
            input_defect_name: in string
        
        :returns:
            defects_list: a list of one defect record (in dict)
        """
        
        try:
            record = self.db.search( self.table_defects , self.defect_name, input_defect_name)[0]
            #print('asd',record)
            return record

        except:
            return []
    
    
    def search_defect_by_color(self, input_color):
        """
        this function is used to search a defect in database by its color

        Inputs:
            input_color: string html code
        
        :returns:
            defect_list: a list with single defect (in dict)
        """
        
        try:
            record = self.db.search( self.table_defects , 'color', input_color)[0]
            #print('asd',record)
            return record
        except:
            return []

    
    def search_defect_by_short_name(self, input_defect_name):
        """
        this function is used to search a defect by its short-name in database

        Inputs:
            input_defect_name: in string
        
        :returns:
            defects_list: a list of one defect record (in dict)
        """

        try:
            record = self.db.search( self.table_defects , self.defect_shortname, input_defect_name)[0]
            #print('asd',record)
            return record
        except:
            return []


    def search_defect_by_filter(self, parms, cols):
        """
        this function is used to search/filter defects by filter params

        Args:
            parms (_type_): value of columns to filter
            cols (_type_): columns to filter

        :returns:
            defect_info: list of filterd defects
        """

        try:
            record = self.db.search( self.table_defects , cols, parms, multi=True)
            #print('asd',record)
            return record

        except:
            return []


    def add_defect(self, parms):
        """
        this function is used to add new defect to database

        Args:
            parms (_type_): new defect infoes

        :returns:
            message: determinig if ok or not
        """

        data=(parms[self.defect_name],parms[self.defect_shortname],parms[self.defect_id],parms['is_defect'],parms['groupp'],parms['level'],parms['color'],parms['date'])
        #print(data)
        try:
            self.db.add_record(data, table_name=self.table_defects, parametrs='(name,short_name,defect_ID,is_defect,groupp,level,color,date)', len_parameters=8)
            #print('yes')
            return 'True'
        
        except:
            #print('no')
            return 'Databas Eror'


    def remove_defects(self, defect_ids):
        """
        this function is used to remove one or multiple defects from database, using their ids

        Inputs:
            defect_ids: list if defect-ids (in string)
        
        :returns:
            results: a boolean determining if the removing is done
        """
        
        # 
        for i in range(len(defect_ids)):
            res = self.db.remove_record(col_name=self.defect_id, id=defect_ids[i], table_name=self.table_defects)

        return res


    def remove_defects_by_group_id(self, defect_ids):
        """
        this function is used to remove all defects with a specific defect-group-id

        Inputs:
            defect_ids: input defect-group-id (in string)

        :returns:
            resault: a boolean determining if removig defects is done
        """

        for i in range(len(defect_ids)):
            res = self.db.remove_record(col_name='groupp',id=defect_ids[i],table_name=self.table_defects)
        
        return res


    def update_defect(self, input_defect_params):
        """
        this function is used to update a defect on table

        Args:
            input_defect_params (_type_): in dict

        :returns:
            resaults: in boolean to deternmine if update is ok
        """
        
        try:
            for param in input_defect_params.keys():
                res = self.db.update_record(self.table_defects, param, str(input_defect_params[param]), self.defect_id, str(input_defect_params[self.defect_id]))
            return res

        except:
            return False

    
    def load_defect_groups(self):
        """
        this function is used to load defect-groups from table

        :returns:
            defect_groups: list of defect-groups (in dict)
        """

        try:
            defects=self.db.get_all_content(self.table_defect_groups)
            return defects
        
        except:
            return []
    

    def search_defect_group_by_id(self, input_defect_group_id):
        """
        this function is used to search a defect-group in database with its id

        Inputs:
            input_defect_group_id: in string
        
        :returns:
            defect_group: list of returned defect groups (since the ids are unique, its a list of one record in dict format)
        """
        
        try:
            record = self.db.search( self.table_defect_groups , self.defect_group_id, input_defect_group_id)[0]
            #print('asd',record)
            return record

        except:
            return []
    

    def search_defect_group_by_name(self, input_defect_group_name):
        """
        this function is used to search a defect-group in table by its name

        Args:
            input_defect_group_name (_type_): _description_

        :returns:
            record: list of defects with this name (list of dicts)
        """

        try:
            record = self.db.search( self.table_defect_groups , 'defect_group_name', input_defect_group_name)[0]
            #print('asd',record)
            return record

        except:
            return []
    

    def search_defect_group_by_filter(self, parms, cols):
        """
        this function is used to search/filter defect-groups by filter params

        Args:
            parms (_type_): value of columns to filter
            cols (_type_): columns to filter

        :returns:
            defect_info: list of filterd defect-groups
        """

        try:
            record = self.db.search( self.table_defect_groups , cols, parms, multi=True)
            #print('asd',record)
            return record
            
        except:
            return []


    def add_defect_group(self,parms):
        """
        this function is used to add new defect-group to database

        Args:
            parms (_type_): new defect-group infoes

        :returns:
            message: determinig if ok or not
        """

        data=(parms['defect_group_name'],parms[self.defect_group_id], parms['is_defect'],parms['date_created'])
        #print(data)
        try:
            self.db.add_record(data, table_name=self.table_defect_groups, parametrs='(defect_group_name,defect_group_id,is_defect,date_created)', len_parameters=4)
            #print('yes')
            return 'True'
        
        except:
            #print('no')
            return 'Databas Eror'
    

    def update_defect_group(self, input_defect_params):
        """
        this function is used to update a defect-group on table

        Args:
            input_defect_params (_type_): in dict

        :returns:
            resaults: in boolean to deternmine if update is ok
        """

        try:
            for param in input_defect_params.keys():
                res = self.db.update_record(self.table_defect_groups, param, str(input_defect_params[param]), self.defect_group_id, str(input_defect_params[self.defect_group_id]))
            return res

        except:
            return False
        

    def remove_defect_groups(self, defect_ids):
        """
        this function is used to remove defect groups from database by their ids

        Inputs:
            defect_ids: list of input defect-group-ids (in string)
        
        :returns:
            resault: a boolean determining if the removing is done
        """

        for i in range(len(defect_ids)):
            res = self.db.remove_record(col_name=self.defect_group_id, id=defect_ids[i], table_name=self.table_defect_groups)
        
        return res
    


    def get_dataset_path(self):
        record = self.db.search(table_name=self.setting_tabel, param_name='id',value=0)[0 ]
        return record['parent_path']


    def load_plc_parms(self):
        """
        this function is used to load plc params from table

        Args: None

        :returns:
            plc_params: in dict, if failed to load from dataabse, return None
        """
        try:
            parms=self.db.get_all_content(self.plc)
            #print(parms)
            return parms

        except:
            return None


    def update_plc_parms(self, plc_parms):
        """
        this function is used to update plc params on database

        Args:
            plc_parms (_type_): in dict

        :returns:
            resault: a boolean determining wheather update is done
        """

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


    def update_plc_ip(self, ip):
        """
        this function is used to update plc ip on table

        Args:
            ip (_type_): plc ip (in string)

        :returns:
            resalt: a boolean determining wheather database updated
        """

        try:
            res = self.db.update_record(self.setting_tabel, 'plc_ip', ip, 'id', 0)
            return res

        except:
            return False


    def load_plc_ip(self):
        """
        this function is used to load plc ip from table on dataabase

        :returns:
            record: plc ip (in string), if failed return False
        """
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