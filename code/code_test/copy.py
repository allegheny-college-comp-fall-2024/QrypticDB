import psycopg2
from psycopg2 import sql, OperationalError

# from encryptcopy import EncryptedDatabase
import re
import coderuntest
import time

# def connect_to_database(host, port, user, password, db_name):
#     try:
#         connection = psycopg2.connect(
#             host=host, port=port, user=user, password=password, database=db_name
#         )
#         print(f"Connected to the database '{db_name}' successfully.")
#         from encryptcopy import EncryptedDatabase

#         # Initialize encryption and decrypt any encrypted tables
#         encrypted_db = EncryptedDatabase()
#         cursor = connection.cursor()
#         start_time = time.time()
#         # here is where the function to decrypt the database will be (still needs to be made)
#         encrypted_db.decrypt_database(cursor)
#         end_time = time.time()  # End the timer
#         elapsed_time = end_time - start_time
#         connection.commit()

#         return connection, cursor, encrypted_db, elapsed_time
#     except OperationalError as e:
#         print(f"Error connecting to the database: {e}")
#         return None, None, None, None


def user_sql_terminal(cursor, connection, encrypted_db):
    count = 0
    try:
        with open("encryption_test_data.csv", "r") as file:
            for line in file:
                query = line.strip()  # Remove any whitespace/newlines

                if query.endswith(";"):
                    try:
                        print("putting in query")
                        print(f"Executing query: {query}")
                        cursor.execute(query)
                        connection.commit()
                        print(f"Executed query: {query}")
                        count += 1
                    except psycopg2.ProgrammingError as e:
                        if "no results to fetch" in str(e):
                            connection.commit()
                            print("Query executed successfully.")
                        else:
                            print(f"Error executing query: {e}")
                            connection.rollback()
                            break
                    except Exception as e:
                        print(f"Error: {e}")
                        connection.rollback()
                # 1250,2500,5000,10000,20000
                if count >= 20000:
                    return True
    except Exception as e:
        print(f"Error reading file: {e}")
    return False


# def check_and_create_table(cursor):
#     # Check if the table exists
#     createq1 = "CREATE TABLE Customers (customer_id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, email VARCHAR(100) UNIQUE NOT NULL, phone VARCHAR(15), address TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);"
#     createq2 = "CREATE TABLE Orders (order_id SERIAL PRIMARY KEY, customer_id INT, order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total_amount DECIMAL(10,2) NOT NULL, status VARCHAR(20) DEFAULT 'Pending', FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE);"
#     createq3 = "CREATE TABLE Products (product_id SERIAL PRIMARY KEY, name VARCHAR(100) NOT NULL, price DECIMAL(10,2) NOT NULL, stock INT NOT NULL);"
#     table_namelst = [createq1, createq2, createq3]

#     try:

#         cursor.execute(
#             sql.SQL(
#                 "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);"
#             ),
#             [createq1]
#         )
#         cursor.execute(sql.SQL(
#                 "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);"
#             ),
#             [createq1],

#         )
#         cursor.execute(
#             sql.SQL(
#                 "SELECT EXISTS (SELECT 1 FROM information_schema.tables WHERE table_name = %s);"
#             ),
#             [createq1],
#         )
#         exists = cursor.fetchone()[0]

#         if not exists:
#             try:
#                 # Create the table if it does not exist
#                 if i == "Customers":
#                     print("Making table")
#                     cursor.execute(createq1)
#                 elif i == "Orders":
#                     print("Making table")
#                     cursor.execute(createq2)
#                 elif i == "Products":
#                     print("Making table")
#                     cursor.execute(createq3)
#                 else:
#                     print(f"Table '{i}' already exists.")
#             except psycopg2.Error as e:
#                 print("error is here")
#                 print(f"Error executing query: {e}")


def check_and_create_table(cursor):
    # Define the table creation SQL statements
    tables = {
        "customers": "CREATE TABLE Customers (customer_id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, email VARCHAR UNIQUE NOT NULL, phone VARCHAR, address TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "orders": "CREATE TABLE Orders (order_id SERIAL PRIMARY KEY, customer_id INT, order_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP, total_amount DECIMAL(10,2) NOT NULL, status VARCHAR DEFAULT 'Pending', FOREIGN KEY (customer_id) REFERENCES Customers(customer_id) ON DELETE CASCADE);",
        "products": "CREATE TABLE Products (product_id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, price DECIMAL(10,2) NOT NULL, stock INT NOT NULL);",
    }

    try:
        # here would be check for exists. if it does, drop the tables
        for table_name, creation_sql in tables.items():
            # Check if table exists
            cursor.execute(
                """
                SELECT EXISTS (
                    SELECT FROM information_schema.tables 
                    WHERE table_schema = 'public' 
                    AND table_name = %s
                );
            """,
                (table_name,),
            )

            table_exists = cursor.fetchone()[0]

            if not table_exists:
                cursor.execute(creation_sql)
                print(f"The table {table_name} was created successfully.")
            else:
                print(f"The table {table_name} already exists.")
                print("Dropping the table to make a new one")
                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                        sql.Identifier(table_name)
                    )
                )

                print(f"The table {table_name} was dropped successfully.")
                print(f"Creating table {table_name}...")
                cursor.execute(creation_sql)
                print(f"The table {table_name} was created successfully.")

    except psycopg2.Error as e:
        print(f"Error executing query: {e}")
    # ISSUE IM HAVING IS THAT MY CODE IS REMOVING COMMAS FROM THE INSERT AND I DON'T KNOW IF THE TABLES ARE BEING MADE
    # Check if each table exists and create it if it does no
    # try:
    #     cursor.execute(table_creation_sql)
    #     print("The table cutsomers was created successfully.")
    #     print("making orders")
    #     cursor.execute(table_creation_sql2)
    #     print("The table orders was created successfully.")
    #     print("Making Products table")
    #     cursor.execute(table_create_table_sql3)
    #     print("The table products was created successfully.")
    # except psycopg2.Error as e:
    #     print(f"Error executing query: {e}")


# def create_or_connectdb() -> tuple:
#     connect_to_db = input("Would you like to connect to an existing database? y/n: \n")
#     if connect_to_db.lower() == "y":
#         host_name = input("Please enter the host name: \n")
#         port_num = input("Please enter the port number: \n")
#         user = input("Please enter the user name: \n")
#         password = input("Please enter the password: \n")
#         database_name = input("Please enter the database name: \n")
#     else:
#         new_database = input("Would you like to make a new database? y/n: \n")
#         if new_database.lower() == "n":
#             print("Goodbye")
#             return None, None, None, None, None
#         default_db = input("Would you like to use the default parameters? y/n?: \n")
#         if default_db.lower() == "n":
#             host_name = input("Please enter the host name: \n")
#             port_num = input("Please enter the port number: \n")
#             user = input("Please enter the user name: \n")
#             password = input("Please enter the password: \n")
#             database_name = input("Please enter the new database name: \n")
#         else:
#             host_name = "localhost"
#             port_num = "5432"
#             user = "postgres"
#             password = "your_password"
#             database_name = "mynewdatabase27"

#         print(
#             f"Your host name is {host_name}, port is {port_num}, the user is {user}, your password is {password}, your database name is {database_name}"
#         )
#         try:
#             connection = psycopg2.connect(
#                 host=host_name,
#                 port=port_num,
#                 user=user,
#                 password=password,
#                 database="postgres",
#             )
#             connection.autocommit = True
#             cursor = connection.cursor()
#             cursor.execute(sql.SQL(f"CREATE DATABASE {database_name}"))
#             print(f"Database '{database_name}' created successfully.")
#             cursor.close()
#             connection.close()
#         except OperationalError as e:
#             print(f"Error while creating database: {e}")
#             return None, None, None, None, None
#     return (host_name, port_num, user, password, database_name)


# Data is not encrpyting
def handle_database_connection() -> tuple:
    try:
        # Get connection details
        connect_to_db = input(
            "Would you like to connect to an existing database? y/n: \n"
        )

        if connect_to_db.lower() == "y":
            # Get connection parameters for existing database
            host_name = input("Please enter the host name: \n")
            port_num = input("Please enter the port number: \n")
            user = input("Please enter the user name: \n")
            password = input("Please enter the password: \n")
            database_name = input("Please enter the database name: \n")

        else:
            new_database = input("Would you like to make a new database? y/n: \n")
            if new_database.lower() == "n":
                print("Goodbye")
                return None, None, None, None

            # Handle new database creation
            default_db = input("Would you like to use the default parameters? y/n?: \n")
            if default_db.lower() == "n":
                host_name = input("Please enter the host name: \n")
                port_num = input("Please enter the port number: \n")
                user = input("Please enter the user name: \n")
                password = input("Please enter the password: \n")
                database_name = input("Please enter the new database name: \n")
            else:
                host_name = "localhost"
                port_num = "5432"
                user = "postgres"
                password = "your_password"
                database_name = "mynewdatabase39"

            print(
                f"Your host name is {host_name}, port is {port_num}, the user is {user}, "
                f"your password is {password}, your database name is {database_name}"
            )

            # Create new database
            try:
                temp_connection = psycopg2.connect(
                    host=host_name,
                    port=port_num,
                    user=user,
                    password=password,
                    database="postgres",
                )
                temp_connection.autocommit = True
                temp_cursor = temp_connection.cursor()
                temp_cursor.execute(sql.SQL(f"CREATE DATABASE {database_name}"))
                print(f"Database '{database_name}' created successfully.")
                temp_cursor.close()
                temp_connection.close()
            except OperationalError as e:
                print(f"Error while creating database: {e}")
                return None, None, None, None

        # Connect to the database (either existing or newly created)
        connection = psycopg2.connect(
            host=host_name,
            port=port_num,
            user=user,
            password=password,
            database=database_name,
        )
        print(f"Connected to the database '{database_name}' successfully.")

        # Initialize encryption
        from encryptcopy import EncryptedDatabase

        encrypted_db = EncryptedDatabase()
        cursor = connection.cursor()

        # Handle decryption
        print("Decrypting database")
        start_time = time.time()
        encrypted_db.decrypt_database(cursor)
        elapsed_time = time.time() - start_time
        connection.commit()
        print("Going to pause for 10 sec")
        time.sleep(10)

        return connection, cursor, encrypted_db, elapsed_time

    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None, None, None, None


def main2():
    from encryptcopy import EncryptedDatabase

    # try:
    # Connect to database once
    connection, cursor, encrypted_db, elapsed_time = handle_database_connection()

    if connection is None:
        print("Restart the program and check if you input the correct data")
        return

    print("going to make and check table")
    check_and_create_table(cursor)

    # Run SQL terminal in a loop if needed
    print(elapsed_time)
    run = True
    # Use the return value to control the loop
    user_sql_terminal(cursor, connection, encrypted_db)
    if connection and cursor and encrypted_db:
        encrypted_dbvar2 = EncryptedDatabase()
        encrypted_dbvar2.encrypt_database(cursor, connection)
        print("Database connection closed.")

    # Or alternatively:
    # run = False if user_sql_terminal(cursor, connection, encrypted_db) else True


# except KeyboardInterrupt:
#     print("\nCtrl + C pressed. Encrypting database before closing...")
#     if connection and cursor and encrypted_db:
#         encrypted_db.encrypt_database(cursor)
#         connection.commit()
#         cursor.close()
#         connection.close()
#         print("Database connection closed.")
# finally:
#     if connection:
#         if cursor and encrypted_db:
#             encrypted_db.encrypt_database(cursor)
#             connection.commit()
#         cursor.close()
#         connection.close()
#         print("Database connection closed.")


if __name__ == "__main__":
    main2()
