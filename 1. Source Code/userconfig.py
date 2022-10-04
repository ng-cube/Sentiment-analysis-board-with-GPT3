# sql related info
SQL_DOMAIN = "cz2006.mysql.database.azure.com"
SQL_USERNAME = "leon@cz2006"
SQL_PASSWORD = "SurelyNotABot55#"
# create favourite words table
create_users_fav_query = """
    CREATE TABLE users_info.usersfav(
        id INT NOT NULL,
        FOREIGN KEY(id) REFERENCES users(id) ON UPDATE CASCADE,
        word VARCHAR(30) NOT NULL,

        PRIMARY KEY (id,word)
    )
"""
# create users table
create_users_table_query = """
    CREATE TABLE users_info.users(
        id int NOT NULL AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(30) UNIQUE,
        password VARCHAR(30),
        email VARCHAR(50) UNIQUE,
        plan int CHECK(plan>=1 AND plan<=3),
        nickname VARCHAR(30) NOT NULL
    )
    """    

# create new users (initial attempt)
create_acc_input = """
    INSERT INTO users_info.users(id,username,email,password,plan,nickname)
    VALUES
        (1,'Jack','jack@123.com','111111',2,'Ja'),
        (2,'Kate','kate@123.com','222222',2,'ka')
    """
# display table query
display_table_query = """
    SELECT * FROM users_info.users
"""

# alter table query
# current update: add a column to users_table * verification *
alter_table_query = """
    ALTER TABLE users_info.users 
    ADD nickname varchar(30)NOT NULL;
"""

#----------------------------------------
# select db
select_db_query = """USE users_info; SHOW FULL TABLES;"""
# display tbs
show_tb_command = """SHOW TABLES"""