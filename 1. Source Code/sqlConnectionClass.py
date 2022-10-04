import mysql.connector
from config import *

class sqlConnection:
    # load the connection data from the config file
    SQL_DOMAIN = SQL_DOMAIN
    SQL_USERNAME = SQL_USERNAME
    SQL_PASSWORD = SQL_PASSWORD

    # load the table names from the config file
    DB_LIST = DB_LIST

    # load the table schema from the config file
    SQL_TABLE_CONTENS = SQL_TABLE_CONTENS
    SQL_RESONING_TABLE_CONTENS = SQL_RESONING_TABLE_CONTENS

    def __init__(self):
        self.conn = None
        self.cursor = None


    def initialize_all_dbs(self):
        """
        create all necessary database tables as defined within the config file.
        """
        for db_name in self.DB_LIST:
            try:
                command = f"CREATE DATABASE {db_name}"
                self.cursor.execute(command)
                self.conn.commit()
            except Exception as exc:
                print(f"EXCEPTION when creating database {db_name}...{exc}")

    def create_connection(self):
        """ create a database connection to SQLite databse online """
        if True or self.conn == None:
            try:
                self.conn = mysql.connector.connect(
                    host=self.SQL_DOMAIN,
                    user=self.SQL_USERNAME,
                    password=self.SQL_PASSWORD,
                    port=3306
                )
                self.conn.ping(True)
                self.cursor = self.conn.cursor()
            except Exception as e:
                print(f"cannot connect to db: {e}")

    def close_connection(self):
        """ close the current database connection """
        if self.conn != None:
            self.conn.close()
        self.conn = None
        self.cursor = None

    def execute_sql_command(self, command):
        """ execute and handle potential errors / exceptions of input commands """
        # check whether a connection already exists and create a new one if necessary
        try:
            self.create_connection()
            if "--" in command:
                raise("A potential SQL-Injection attack was detected :( ")
            self.cursor.execute(command)
        except Exception as e:
            print(f"Unexpected Error in execute_sql_command: {e}")
            print(f"\tattmpted command: {command}")

    def push_update_command(self, dic, table, database="twitter_keyword"):
        self.create_connection()
        columns = ', '.join(dic.keys())
        placeholders = ', '.join(['%s'] * len(dic))
        try:
            query = 'INSERT INTO %s.%s (%s) VALUES (%s)' % (database, table, columns, placeholders)
            if "--" in query:
                raise("A potential SQL-Injection attack was detected :( ")
            self.cursor.execute(query, list(dic.values()))#dic)
            self.conn.commit()
        except Exception as exc:
            print(f"UNEXPECTED ERROR in update_database_with_dict on query {exc}: \n\t{query}\n\t{dic}")

    def initialize_sql_database_table(self, keyword):
        timeline = "@" in keyword
        keyword = keyword.replace(" ","_").replace("@","_")

        # create sentiment tweet table
        table_command = self.SQL_TABLE_CONTENS.format(keyword)
        self.execute_sql_command(
            command=table_command
        )

        # initialize the table that will hold the sentiment reasoning data
        table_command = self.SQL_RESONING_TABLE_CONTENS.format(keyword)
        self.execute_sql_command(
            command=table_command
        )

    def update_tweet_batch(self, keyword, tweet_list, database="twitter_keyword"):
            keyword = keyword.replace(" ","_").replace("@","_")
            # get largest primary key from relevant table
            for tweet_dict in tweet_list:
                # add new row to the relevant table
                self.push_update_command(
                    dic=tweet_dict,
                    table=keyword,
                    database=database
                )

    def load_batch_of_tweets(self, keyword, column, time_start=None, time_end=None, compound_min=None, compound_max=None, omitt_replies=False):
            keyword = keyword.replace(" ","_").replace("@","_")
            if time_start==time_end==compound_min==compound_max==None:
                command = f"SELECT {column} FROM twitter_keyword.{keyword} WHERE (LOWER(username) != LOWER('{keyword}'))"

            else:
                command = f"SELECT {column} FROM twitter_keyword.{keyword} WHERE (LOWER(username) != LOWER('{keyword}')) AND "
                time_command = None
                if time_start==time_end==None:
                    pass
                elif time_end==None:
                    time_command = f"(timestamp > {time_start})"
                elif time_start==None:
                    time_command = f"(timestamp < {time_end})"
                else:
                    time_command = f"(timestamp BETWEEN {time_start} AND {time_end})"

                if time_command != None:
                    command = command + time_command + " AND "

                if compound_min==compound_max==None:
                    pass
                elif compound_max==None:
                    command += f"(compound > {compound_min})"
                elif compound_min==None:
                    command += f"(compound < {compound_max})"
                else:
                    command += f"(compound BETWEEN {compound_min} AND {compound_max})"

                if omitt_replies:
                    command += f"AND in_reply_to_screen_name IS NULL"

            #self.cursor.execute(command)
            self.execute_sql_command(
                command=command
            )
            result = self.cursor.fetchall()
            return [e[0] for e in result]

    def update_sentiment_reasoning(self, keyword, update_dict, start_ts, end_ts):
        """ update the relevant sql table """
        keyword = keyword.replace(" ","_").replace("@","_")
        for key in update_dict.keys():
            start_sentiment, end_sentiment = key
            command = ADD_REASONING_BASE_COMMAND.format(keyword)
            self.cursor.execute(
                command,
                (start_ts, end_ts, start_sentiment, end_sentiment, update_dict[key])
            )
            self.conn.commit()


    def get_all_keywords(self):
        command = "USE twitter_keyword;"
        self.cursor.execute(command)
        command = "SHOW Tables"
        self.cursor.execute(command)
        data = self.cursor.fetchall()
        if len(data)== 0:
            return []
        else:
            return [e[0] for e in data]




    # util functions
    def get_most_recent_ts(self, keyword, column="timestamp", database="twitter_keyword"):
        keyword = keyword.replace(" ","_").replace("@","_")
        command = f"SELECT {column} FROM {database}.{keyword} ORDER BY {column} DESC LIMIT 1"
        try:
            self.cursor.execute(command)
            data = self.cursor.fetchall()
        except mysql.connector.errors.ProgrammingError as exc:
            # cause if there is not timestamp column (hence the table is empty)
            return None
        if len(data) == 0:
            return None
        else:
            return data[0][0] # return the actual TIMESTAMP

    def get_oldest_ts(self, keyword, database="twitter_keyword"):
        keyword = keyword.replace(" ","_").replace("@","_")
        command = f"SELECT timestamp FROM {database}.{keyword} ORDER BY timestamp ASC LIMIT 1"
        self.cursor.execute(command)
        data = self.cursor.fetchall()
        if len(data) == 0:
            return None
        else:
            return data[0][0] # return the actual TIMESTAMP


    def load_data_for_custom_command(self, command):
        self.cursor.execute(command)
        return [e[0] for e in self.cursor.fetchall()]


    def getPositiveSummary(self, keyword, database="twitter_sentiment_reasoning"):
         keyword = keyword.replace(" ","_").replace("@","_")
         command = f"SELECT summary, end_timestamp FROM {database}.{keyword} "+\
         f"WHERE start_sentiment = 0.25 "+\
         f"ORDER BY end_timestamp DESC, start_sentiment "+\
         f"LIMIT 7;"

         try:
             self.cursor.execute(command)
             data = self.cursor.fetchall()
         except mysql.connector.errors.ProgrammingError as exc:
             # cause if there is not timestamp column (hence the table is empty)
             return None
         return data


    def getNegativeSummary(self, keyword, database="twitter_sentiment_reasoning"):
        keyword = keyword.replace(" ","_").replace("@","_")
        command = f"SELECT summary, end_timestamp FROM {database}.{keyword} "+\
        f"WHERE start_sentiment = -1.0 "+\
        f"ORDER BY end_timestamp DESC, start_sentiment "+\
        f"LIMIT 7;"

        try:
            self.cursor.execute(command)
            data = self.cursor.fetchall()
        except mysql.connector.errors.ProgrammingError as exc:
            # cause if there is not timestamp column (hence the table is empty)
            return None
        return data

    def get_timestamp_sentiment(self, keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        display_table_query = """
        SELECT timestamp, compound FROM twitter_keyword.%s;
        """%(keyword)
        self.create_connection()
        self.execute_sql_command(command = display_table_query)
        result = self.cursor.fetchall()
        return result #return list of tuples

    #SQL
    #calculate mean
    def getmean(self,keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        getmean_query = """
        SELECT AVG(compound) FROM twitter_keyword.%s;
         """ %(keyword)
        self.execute_sql_command(command = getmean_query)
        result = self.cursor.fetchone()
        if result == None:
            return -1
        return round(result[0],2)

    #calculate variance
    def getvar(self,keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        getvar_query = """
        SELECT VARIANCE(compound) FROM twitter_keyword.%s;
        """ %(keyword)
        self.execute_sql_command(command = getvar_query)
        result = self.cursor.fetchone()
        if result == None:
            return -1
        return round(result[0],2)

    #calculate percentage of positive sentiment
    def calposperc(self,keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        countpos_query = f"""
        SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        WHERE compound >0.25
        """
        self.execute_sql_command(command = countpos_query)
        result1 = self.cursor.fetchone()

        if result1 == None:
            return -1

        countall_query = f"""
         SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        """
        self.execute_sql_command(command = countall_query)
        result2 = self.cursor.fetchone()
        final_res = result1[0]/result2[0]

        return round(final_res*100,2)

    #calculate percentage of negative sentiment
    def calnegperc(self,keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        countneg_query = f"""
        SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        WHERE compound <-0.25
        """
        self.execute_sql_command(command = countneg_query)
        result1 = self.cursor.fetchone()

        if result1 == None:
             return -1

        countall_query = f"""
        SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        """
        self.execute_sql_command(command = countall_query)
        result2 = self.cursor.fetchone()
        final_res = result1[0]/result2[0]

        return round(final_res*100,2)

    #calculate percentage of neutral sentiment
    def calneuperc(self,keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        countneu_query = f"""
        SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        WHERE compound >= -0.25 AND compound <= 0.25
        """
        self.execute_sql_command(command = countneu_query)
        result1 = self.cursor.fetchone()

        if result1 == None:
            return -1

        countall_query = f"""
        SELECT COUNT(*)
        FROM twitter_keyword.{keyword}
        """
        self.execute_sql_command(command = countall_query)
        result2 = self.cursor.fetchone()
        final_res = result1[0]/result2[0]

        return round(final_res*100,2)

    def checkIfExists(self, keyword):
        keyword = keyword.replace(" ","_").replace("@","_")
        query = f"SELECT * FROM twitter_keyword.{keyword}"

        self.execute_sql_command(command = query)
        result = self.cursor.fetchall()

        print(f'check if exists: {keyword}')

        if result == []:
            print('result is none')
            return False

        return True

