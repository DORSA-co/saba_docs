from matplotlib.pyplot import flag
import mysql.connector
from mysql.connector import Error

               

class dataBase:
    """
    this class is used to connect and working with database

    Inputs:
        username: username to connect to database
        password: password to connect to databse
        host: host of the database
        database_name: name of the database to work with
        logger_obj: the logger object to take logs
    
    :returns: None
    """
    
    def __init__(self, username, password, host, database_name, logger_obj=None):
        pass
        self.user_name=username
        self.password=password
        self.host=host
        self.data_base_name=database_name
        self.logger_obj = logger_obj

        # check the connection to database
        self.check_connection()
        
    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def get_log(self, message='nothing', level=1):
        """
        this function is used to get log from database tasks

        Args:
            message (str, optional): _description_. Defaults to 'nothing'.
            level (int, optional): level of log. Defaults to 1.

        """
        if self.logger_obj != None:
            self.logger_obj.create_new_log(message=message, level=level)


    def connect(self):
        """
        this function is used for connecting to database

        Inputs: None

        :returns:
            cursor: the object that is used to work with database by queries
            connection: ?
        """
        
        connection = mysql.connector.connect(host=self.host,
                                            database=self.data_base_name,
                                            user=self.user_name,
                                            password=self.password)  
        cursor = connection.cursor()

        return cursor, connection     


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def check_connection(self):
        """
        this function is used to check if the connection to databse can be esablished

        Inputs: None

        :returns: a boolean value determining if the connecton is stablished or not
        """

        flag=False

        try: 
            cursor, connection = self.connect() # connect to database
            #
            flag=True
            #
            if connection.is_connected():
                db_Info = connection.get_server_info() # get informations of database
                # log
                self.get_log(message='Connected to MySQL Server version %s' % (db_Info))
                #

                cursor = connection.cursor()
                cursor.execute("select database();")
                record = cursor.fetchall()

                # log
                self.get_log(message='Connected to database %s' % (record))
                #
                return True

        except Exception as e:
            # log
            self.get_log(message='Error while connecting to MySQL', level=5)
            #
            return False

        finally:
            if flag and connection.is_connected():
                cursor.close()
                connection.close()

            # log
            self.get_log(message='MySQL connection is closed')
            #

    
    def execute_quary(self, quary, cursor, connection, need_data=False, close=False):
        """
        this function is used to execute a query on database

        Inputs:
            quary: the input query to execute
            cursor:
            connection:
            need_data: a bolean value
            close:
        
        :returns: None
        """
        
        try:
            if need_data:
                cursor.execute(quary, data)

            else:
                cursor.execute(quary)

            # connection.commit()
            if close:
                cursor.close()
            else:
                return cursor

        except Exception as e:
            # log
            self.get_log(message='Error while connecting to MySQL')
            #
        


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def add_record(self, data, table_name, parametrs, len_parameters):
        """
        this function is used to add a new record a specified table of database

        Inputs:
            data: data to be added to database
            table_name: in string
            parametrs: list of parameters (column names) of the database
            len_parameters: number of parameters
        
        :returns: None
        """

        s = '%s,'*len_parameters
        s = s[:-1]
        s = '(' + s + ')'
        

        if self.check_connection:
            # connect to database
            cursor,connection=self.connect()

            # input query
            mySql_insert_query = """INSERT INTO {} {} 
                                VALUES 
                                {} """.format(table_name, parametrs, s)
            
            # execute query with input data
            cursor.execute(mySql_insert_query, data)
            # mySql_insert_query=(mySql_insert_query,data)
            # self.execute_quary(mySql_insert_query, cursor, connection, close=False,need_data=True )
            connection.commit()
            
            cursor.close()

            return True

        else:
            return False


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def update_record(self, table_name, col_name, value, id, id_value):
        """
        this function is used to update a parameter (column) in a table record, detrtmingn by record id

        Inputs:
            table_name: name of the table in database (in string)
            col_name: column name of table to update (in string)
            value: value will be assigned to column ((in string))
            id: name of id column in table, its used to determine which record to update
            id_value: value of the id column
        
        :returns:
            result: a boolean determining if the update on table is done or not
        """
        
        if self.check_connection:
            
            cursor,connection=self.connect()
            
            mySql_insert_query = """UPDATE {} 
                                    SET {} = {}
                                    WHERE {} ={} """.format(table_name, col_name, ("'"+value+"'"),id,id_value)

            #print(mySql_insert_query)
            
            #print(mySql_insert_query)
            cursor.execute(mySql_insert_query)
            # mySql_insert_query=(mySql_insert_query,data)
            # self.execute_quary(mySql_insert_query, cursor, connection, close=False,need_data=True )
            connection.commit()
            #print(cursor.rowcount, "Record Updated successfully ")
            cursor.close()
            return True

        else:
            return False






    def remove_record(self, col_name, id, table_name):
        """
        this function is used to remove a record from table acourding to specified column value

        Inputs:
            col_name: name of the column to check for (in string)
            id: value of the column (in string)
            table_name: name of the table (in string)
        
        :returns:
            results: a boolean determining if the record is removed or not
        """
        
        try:
            if self.check_connection:
                cursor,connection=self.connect()

                mySql_delete_query = """DELETE FROM {} WHERE {}={};""".format(table_name,col_name,"'"+id+"'")

                self.execute_quary(mySql_delete_query, cursor, connection, False )
                connection.commit()
                #print(cursor.rowcount, "Remove successfully from table {}".format(table_name))
                cursor.close()

                return True
            
            else:
                return False
        
        except:
            return False


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------
    def report_last(self,table_name,parametr,count):
        if self.check_connection:
            cursor,connection=self.connect()

            sql_select_Query = "select * from {} ORDER BY {} DESC LIMIT {}".format(table_name,parametr,count)
            cursor=self.execute_quary(sql_select_Query, cursor, connection)
            # cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            #print("Total number of rows in table: ", cursor.rowcount)
            #print(records)
            connection.close()
            cursor.close()
            #print("MySQL connection is closed")

            field_names = [col[0] for col in cursor.description]
            res = []
            for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    res.append( record_dict )

            return res


            return records


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def search(self, table_name, param_name, value, multi=False):
        """
        this function is used to search in table accoarding to one or multiple specifiic parameter (column name)

        Inputs:
            table_name: in string
            param_name: parameter (column) name in string, for multiple parameters, a list of strings
            value: value of the parameter to be (in string), for multiple values, a list of strings
            multi: a boolean value determining if the search is according to one parameter or multi parameters
        
        :returns:
            result: a list containing the returned/searched row (record) in table, if failed to connect to database or nothing was found in table,
            an empty list will be returned
        """
        
        try:
            # check connection 
            if self.check_connection:
                cursor, connection = self.connect()

                # single parameter
                if not multi:
                    sql_select_Query = "SELECT * FROM {} WHERE {} = '{}'".format(table_name, param_name, str(value))

                # mlti parameter
                else:
                    if len(value) == 1:
                        sql_select_Query = "SELECT * FROM %s WHERE %s=('%s')" % (table_name, param_name, value[0])
                    else:
                        sql_select_Query = "SELECT * FROM %s WHERE %s=%s" % (table_name, param_name, tuple(value))

                #
                #print(sql_select_Query)
                # execute query
                cursor=self.execute_quary(sql_select_Query, cursor, connection)
                records = cursor.fetchall() # get returned records

                #print("Total number of rows in table: ", cursor.rowcount)
                #print(len(records),records)
                #----------------------------
                
                field_names = [col[0] for col in cursor.description]
                res = []

                for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]

                    res.append( record_dict )
                    

                return res

            # return empty list if failed to connect to database
            return []

        except:
            #print('No record Found')
            return []


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def delete(self,db_name,table_name):
        try:
            if self.check_connection:
                cursor,connection=self.connect()
            sql_Delete_table = "DELETE FROM  {}.{};".format(db_name,table_name)
            cursor=self.execute_quary(sql_Delete_table, cursor, connection)       
            #print('delete')     
            #                               
        except Exception as e:
            self.get_log(message='Error reading data from MySQL table', level=5)


    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def get_col_name(self,table_name,param_name, value):
        if self.check_connection:
            cursor,connection=self.connect()
            

            cursor = connection.cursor()
            cursor.execute("select database();")

            field_names = [col[0] for col in cursor.description]

            #print(field_names)

        return field_names

    #--------------------------------------------------------------------------
    #--------------------------------------------------------------------------

    def get_all_content(self, table_name):
        """
        this function is used to get/return all contents of a table

        Inputs:
            table_name: in string

        :returns:
            table_content: list of records in table (in dict)
        """

        if self.check_connection:
            cursor,connection=self.connect()

            sql_select_Query = "select * from {} ".format(table_name)
            cursor=self.execute_quary(sql_select_Query, cursor, connection)
            # cursor.execute(sql_select_Query)
            records = cursor.fetchall()
            #print("Total number of rows in table: ", cursor.rowcount)
            # print(records)
            connection.close()
            cursor.close()
            #print("MySQL connection is closed")

            field_names = [col[0] for col in cursor.description]
            res = []

            for record in records:
                    record_dict = {}
                    for i in range( len(field_names) ):
                        record_dict[ field_names[i] ] = record[i]
                    res.append( record_dict )

            return res
    



if __name__ == "__main__":
    db=dataBase('root','root','localhost','saba_database')

    # db.get_col_name('996','camera_settings','id')

    # data=(0,)*10
    #data=(0,0,0,0,1920,1200,0,0,0,0,0)

    
    # x=db.get_all_content('users')
    # table_name,parametrs,len_parameters)

    # db.add_record(data,'coils_info','(id,coil_number,heat_number,ps_number,pdl_number,lenght,width,operator,time,date,main_path)',11)
    # db.add_record(data,'camera_settings','(gain_top,gain_bottom,expo_top,expo_bottom,width,height,offset_x,offset_y,interpacket_delay,packet_size,id)',11)
 
    #db.add_record(data,'coils_info','(id,coil_number,heat_number,ps_number,pdl_number,lenght,width,operator,time,date,main_path)',11)

    # x=db.report_last('users','id',30)

    # print(x)

    # db.remove_record('1920', 'camera_settings')

    # db.remove_record('user_name', 'milad', 'users')

    # data=('milad','1','operator')

    # db.add_record(data, table_name='users', parametrs='(user_name,password,role)', len_parameters=3)

    # db.report_last('coils_info','id',30) 

    # x=db.search('users','user_name','test')
    # print(x)


# report_last(self,table_name,parametr,count)



# CREATE SCHEMA `saba_database` ;


# CREATE TABLE `saba_database`.`coils_info` (
#   `id` INT NOT NULL,
#   `coil_number` VARCHAR(45) NOT NULL,
#   `heat_number` VARCHAR(45) NULL,
#   `ps_number` VARCHAR(45) NULL,
#   `pdl_number` VARCHAR(45) NULL,
#   `lenght` VARCHAR(45) NULL,
#   `width` VARCHAR(45) NULL,
#   `operator` VARCHAR(45) NULL,
#   `time` VARCHAR(45) NULL,
#   `date` VARCHAR(45) NULL,
#   PRIMARY KEY (`id`));