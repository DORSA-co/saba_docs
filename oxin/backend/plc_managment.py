from opcua import Client, ua
import os
import json

from .backend import texts


class management():
    """
    this class is used to create and manage opc/plc object

    Args:
        ip: plc ip (in string)
        ui_obj: main ui object
    
    Returns: PLC object
    """

    def __init__(self, ip, ui_obj):
        self.ip=ip
        self.set_file_name('text_plc_parms')
        self.ui_obj = ui_obj
        # self.connection()
    

    def connection(self):
        """
        this function is used to connect to plc

        Returns:
            resault: a boolean deermining if connected or not
        """

        #print('Start Connecting to {}'.format(self.ip))
        self.ui_obj.logger.create_new_log(message=texts.MESSEGES['plc_start_connecting']['en'] + ' ip: ' + str(self.ip), level=1)
        self.client = Client(self.ip)
        # client = Client("opc.tcp://admin@localhost:4840/freeopcua/server/") #connect using a user
        try:
            self.client.connect()
            #print('Connection Successed')
            return True

        except:
            #print('Connection Eror')
            return False

    
    def disconnect(self):
        """
        this functino is used to disconnect from plc

        Args: None

        Returns: None
        """

        self.client.disconnect()


    def get_value(self, path):
        """
        this function is used to get value of a logic from plc using its path

        Args:
            path (_type_): plc logic path (in string)

        Returns:
            value: value stored in path, if failed to load, return '-'
            data_value: if failed to load, return message error
        """

        try:
            var = self.client.get_node(path)
            # print(var)
            data_value=var.get_data_value() # get value of node as a DataValue object
            value=var.get_value() # get value of node as a python builtin
            # print('x'*5,value)
            return (value, data_value)

        except:
            # print('except')
            return '-', texts.ERRORS['plc_path_error'][self.ui_obj.language]


    def set_value(self, path, value):
        """
        this function is used to set/update value of a logic, using its path on plc

        Args:
            path (_type_): path of the logic (in string)
            value (_type_): input value to update (digit or boolean)

        Returns: None
        """

        var = self.client.get_node(path)
        
        if value.isdigit():
            # print('number')
            var = self.client.get_node(path)
            var.set_value(ua.Variant(int(value), ua.VariantType.Int64)) #set node value using explicit data type
            var.set_value(int(value)) # set node value using implicit data type

        else:
            # print('value:',value)
            if value=='False':
                value_=False
                #print(value_)
            else:
                value_=True

            value = ua.DataValue(ua.Variant(value_,ua.VariantType.Boolean))
            var.set_value(value)
        

    def set_file_name(self, name):
        """
        this function is used to set json file name to store plc params

        Arge: None

        Returns: None
        """

        self.text_plc_parms=name  


    def write(self, value):
        """
        this function is used to write plc values on json file

        Args:
            value (_type_): in dict
        """
        
        # print('write',path)
        path = os.path.join(self.text_plc_parms+'.json')
        # print('value',value)
        with open(str(path), 'w') as f:
            json.dump(value, f,indent=4, sort_keys=True)

