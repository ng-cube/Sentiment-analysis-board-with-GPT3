from tracemalloc import stop
import mysql.connector
from userconfig import *
from mysql.connector import connect,Error
#from getpass import getpass
#from __future__ import all_feature_names
#from venv import create


class sqlManagement:
    SQL_DOMAIN = SQL_DOMAIN 
    SQL_USERNAME = SQL_USERNAME
    SQL_PASSWORD = SQL_PASSWORD

    database = "users_info"

    users_table_content = create_users_table_query
    usersfav_content = create_users_fav_query
    
    def __init__(self) -> None:
        self.conn = None
        self.cursor = None


    def create_connection(self):
        #create a database connection to mysql database
        #store a MySQLConnection object in the conncection variable
        if True or self.conn == None:
            try:
                self.conn = mysql.connector.connect(
                    host=self.SQL_DOMAIN,
                    user=self.SQL_USERNAME,
                    password=self.SQL_PASSWORD
                )
                self.conn.ping(True)
                self.cursor = self.conn.cursor( buffered= True)
            except Error as e:
                print("Error message: ",e)     
    

    def initialize_db(self):
        try:
            create_db_query = "CREATE DATABASE users_info"
            self.cursor.execute(create_db_query)
            self.conn.commit()
        except Exception as e:
            print(f"EXCEPTION when creating database ...{e}")


    def close_connection(self):
        """ close the current database connection """
        if self.conn != None:
            self.conn.close()
        self.conn = None
        self.cursor = None

    def initialize_user_table(self):
        self.create_connection()

        table_command = self.users_table_content #.format(keyword)
        self.execute_sql_command(command = table_command)

    def initialize_usersfav_table(self):
        self.create_connection()

        table_command = self.usersfav_content #.format(keyword)
        self.execute_sql_command(command = table_command)

    def display_tables(self):
        #doesnt work
        self.execute_sql_command(command = select_db_query)
        result = self.cursor.fetchall()
        print(result)

    #////////////////////////////////////////////////////////////    
    def createINIAccount(self):
        #DONE
        #get user input
        self.create_connection()
        self.execute_sql_command(command = create_acc_input)
        self.conn.commit()

    def checkuserNpass(self,inputusername,inputpw):
        #DONE
        #SQL command
        check_user_n_pass_query = """
        SELECT
        
        CASE WHEN EXISTS 
        (   SELECT users.username,users.password
            FROM users_info.users
            WHERE username = '%s' and password = '%s') 
        THEN 'Welcome,%s!'
        
        WHEN EXISTS 
        (   SELECT users.username,users.password
            FROM users_info.users
            WHERE username = '%s' and password <> '%s')
        THEN 'Password is incorrect. Please retry.'
       
        ELSE 'User does not exist. Please sign up as a new user.'
        
        END"""% (inputusername,inputpw,inputusername,inputusername,inputpw)
   
        self.execute_sql_command(check_user_n_pass_query)
        result = self.cursor.fetchone()
        return result[0]
    

    def createNew (self,username,email,password,plan,nickname):
        #DONE
        #SQL Insert new account command
        create_new_query = """
        INSERT INTO users_info.users(username,email,password,plan,nickname)
        VALUES ('%s','%s','%s',%s,'%s')
        """%(username,email,password,plan,nickname)
  
        self.execute_sql_command(create_new_query)

    #specially for Jacky
    def validate_username (self,inputusername):
        validate_query = """
        SELECT users.username
        FROM users_info.users
        WHERE users.username = '%s'
        """%(inputusername)

        self.execute_sql_command(command=validate_query)
        result = self.cursor.fetchone()

        if result == None:
            return 1
        else:
            #print ("Username exists!")
            return 0
       
        

    def editpassword(self,username,nickname,oldpw,newpw):
        #DONE
        #SQL command
        check_pw_query = """
        SELECT 
        CASE WHEN EXISTS
        (   SELECT users.username,users.password
            FROM users_info.users
            WHERE username = '%s' and password = '%s')
        THEN  ( 'correct')
        ELSE 'Please check your username and password.'
        END"""%(username,oldpw)

        verify_nickname = """
        SELECT 
        CASE WHEN EXISTS
        (   SELECT users.username,users.nickname
            FROM users_info.users
            WHERE username = '%s' and nickname = '%s')
        THEN  ( 'correct')
        ELSE 'Please check your username and verification.'
        END"""%(username,nickname)

        #edit_pw_query_part2
        edit_pw_query = """
            UPDATE users_info.users
            SET password = '%s'
            WHERE username = '%s'
        """%(newpw,username)
 
        self.execute_sql_command(check_pw_query)
        result = self.cursor.fetchone()

        if result[0] == 'correct':
            self.execute_sql_command(verify_nickname)
            result2 = self.cursor.fetchone()
            if result2[0] == 'correct':
                self.execute_sql_command(edit_pw_query)
        else: 
            print("error!")
        self.conn.commit()


    def forget_password(self,username,nickname,newpass):
        verify_nickname = """
        SELECT 
        CASE WHEN EXISTS
        (   SELECT users.username,users.nickname
            FROM users_info.users
            WHERE username = '%s' and nickname = '%s')
        THEN  ( 'correct')
        ELSE 'Please check your username and verification.'
        END"""%(username,nickname)

        update_password = """
        UPDATE users_info.users
        SET users.password = '%s'
        WHERE users.username = '%s'
        """%(newpass,username)
 
        self.execute_sql_command(verify_nickname)
        result = self.cursor.fetchone()

        if result[0] == 'correct':
            self.execute_sql_command(update_password)
        else: 
            print("error!")
        self.conn.commit()

    def editUserSubscription(self,username,password,newplan):
        #NOT DONE
        #SQL command
        check_pw_query = """
        SELECT 
        CASE WHEN EXISTS
        (   SELECT users.username,users.password
            FROM users_info.users
            WHERE username = '%s' and password = '%s')
        THEN  ( 'correct')
        ELSE 'Please check your username and password.'
        END"""%(username,password)

        edit_plan = """
        UPDATE users_info.users
        SET plan = %s
        WHERE username = '%s'
        """ %(newplan,username)

        self.execute_sql_command(check_pw_query)
        result = self.cursor.fetchone()
        #if password is correct
        if result[0] == 'correct':
            self.execute_sql_command(edit_plan)
        else: 
            print("error!")
        self.conn.commit()


    #insert word into usersfav table
    def insert_new_word(self,username,word):
        #SQL command
        look_for_id = """
        SELECT users.id 
        FROM users_info.users
        WHERE users.username = '%s'
        """ % (username)

        self.execute_sql_command(look_for_id)
        userid = self.cursor.fetchone()
        if userid[0] != None:
            insert_word_query = """
            INSERT INTO users_info.usersfav(id,word)
            VALUES (%s,'%s')
            """%(userid[0],word)

            self.execute_sql_command(command = insert_word_query)
        else: 
            print('error!')


    def altertable(self):
        #DONE, utility function to alter table
        self.execute_sql_command(command = alter_table_query)

    def display_current_table(self):
        self.execute_sql_command(command = display_table_query)
        result = self.cursor.fetchall()
        print(result)
    
    ##getters################################
    def getemail(self,username):
        getemail_query = """
        SELECT users.email 
        FROM users_info.users
        WHERE users.username = '%s'
        """%(username)

        self.execute_sql_command(command = getemail_query)
        result = self.cursor.fetchone()
        return result[0]

    def getplan(self,username):
        getplan_query = """
        SELECT users.plan
        FROM users_info.users
        WHERE users.username = '%s'
        """%(username)

        self.execute_sql_command(command = getplan_query)
        result = self.cursor.fetchone()
        return result[0]

    def getnickname(self,username):
        getnickname_query = """
        SELECT users.nickname
        FROM users_info.users
        WHERE users.username = '%s'
        """%(username)

        self.execute_sql_command(command = getnickname_query)
        result = self.cursor.fetchone()
        return result[0]
    
    #///////////////////////////////////////////////////////////////////
    def execute_sql_command(self, command):
        """ execute and handle potential errors / exceptions of input commands """
        # check whether a connection already exists and create a new one if necessary
        try:
            self.create_connection()
            self.cursor.execute(command)
            self.conn.commit()
        except Exception as e:
            print(f"Unexpected Error in execute_sql_command: {e}")
            print(f"\tattmpted command: {command}")
   

    def execute_sql_command_with_input(self, command, tuple):
        """ execute and handle potential errors / exceptions of input commands """
        # check whether a connection already exists and create a new one if necessary
        try:
            self.create_connection()
            self.cursor.execute(command,tuple)
            self.conn.commit()
        except Exception as e:
            print(f"Unexpected Error in execute_sql_command: {e}")
            print(f"\tattmpted command: {command}")