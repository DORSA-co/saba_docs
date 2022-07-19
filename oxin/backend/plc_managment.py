from opcua import Client,ua
import os
import json

from . import texts


class management():
    def __init__(self, ip, ui_obj):
        self.ip=ip
        self.set_file_name('text_plc_parms')
        self.ui_obj = ui_obj
        # self.connection()
    

    def connection(self):
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
        self.client.disconnect()


    def get_value(self, path):
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


    def set_value(self,path,value):
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
        

    def set_file_name(self,name):
        self.text_plc_parms=name  


    # def create_parms(self):


    def write(self,value):    
        # print('write',path)
        path = os.path.join(self.text_plc_parms+'.json')
        # print('value',value)
        with open(str(path), 'w') as f:
            json.dump(value, f,indent=4, sort_keys=True)



    # def write_plc_parms(self,parms):

    #     str1 = ""
    #     # traverse in the string 
    #     for i in s:
    #         str1 += i 
    #     print(str1)

    #     parms=

    #     self.writ(parms)

    # def writ(self,parms):
    #     f = open(self.text_plc_parms,'r+')
    #     f.write(parms)
    #     f.close()