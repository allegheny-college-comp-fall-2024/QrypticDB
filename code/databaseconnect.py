import psycopg2
from psycopg2 import sql, OperationalError
import queryencrypt
import re


# def connect_to_database(host, port, user, password, db_name):
#     try:
#         connection = psycopg2.connect(
#             host=host, port=port, user=user, password=password, database=db_name
#         )
#         print(f"Connected to the database '{db_name}' successfully.")
#         return connection
#     except OperationalError as e:
#         print(f"Error connecting to the database: {e}")
#         return None


def connect_to_database(host, port, user, password, db_name):
    try:
        connection = psycopg2.connect(
            host=host, port=port, user=user, password=password, database=db_name
        )
        print(f"Connected to the database '{db_name}' successfully.")

        # Initialize encryption and decrypt any encrypted tables
        encrypted_db = queryencrypt.EncryptedDatabase()
        cursor = connection.cursor()
        # here is where the function to decrypt the database will be (still needs to be made)
        encrypted_db.decrypt_database(cursor)
        connection.commit()

        return connection, cursor, encrypted_db
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None, None, None


def create_database(host, port, user, password, new_db_name):
    try:
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres",
        )
        connection.autocommit = True
        cursor = connection.cursor()
        cursor.execute(sql.SQL(f"CREATE DATABASE {new_db_name}"))
        print(f"Database '{new_db_name}' created successfully.")
        cursor.close()
        connection.close()
    except OperationalError as e:
        print(f"Error while creating database: this datbase becasue {e}")


# def display_database(cursor):
#     cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
#     db_list = cursor.fetchall()
#     print("Databases:")
#     for db in db_list:
#         print(f" - {db[0]}")

#     cursor.execute(
#         "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
#     )
#     tables = cursor.fetchall()
#     if tables:
#         print("Tables in the current database:")
#         for table in tables:
#             print(f" - {table[0]}")
#     else:
#         print("No tables in the current database.")


def user_sql_terminal(cursor, connection, encrypted_db) -> bool:
    while True:
        try:
            user_query = input("Enter SQL query (type 'exit' or '\\q' to quit): ")

            # Handle exit condition
            if user_query.strip().lower() in ("exit", "\\q"):
                print("Encrypting database before closing...")
                encrypted_db.encrypt_database(cursor)
                connection.commit()
                cursor.close()
                connection.close()
                return False

            # Execute the query
            try:
                results = encrypted_db.execute(cursor, user_query)
                if results is not None:
                    for row in results:
                        print(row)
                    connection.commit()
                else:
                    connection.commit()
                    print("Query executed successfully.")

            except psycopg2.ProgrammingError as e:
                if "no results to fetch" in str(e):
                    connection.commit()
                    print("Query executed successfully.")
                else:
                    print(f"Error executing query: {e}")
                    connection.rollback()

        except Exception as e:
            print(f"Error: {e}")
            connection.rollback()


# Long function for creating or connecting to a database
def create_or_connectdb() -> tuple:
    connect_to_db = input("Would you like to connect to an existing database? y/n: \n")
    if connect_to_db.lower() == "y":
        host_name = input("Please enter the host name: \n")
        port_num = input("Please enter the port number: \n")
        user = input("Please enter the user name: \n")
        password = input("Please enter the password: \n")
        database_name = input("Please enter the database name: \n")

    else:
        new_database = input("Would you like to make a new database? y/n: \n")
        if new_database.lower() == "n":
            print("Goodbye")
            return None, None
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
            database_name = "mynewdatabase26"

        print(
            f"Your host name is {host_name}, port is {port_num}, the user is {user}, your password is {password}, your database name is {database_name}"
        )
        # If for some reason the above default database does not work, it will try
        try:
            connection = psycopg2.connect(
                host=host_name,
                port=port_num,
                user=user,
                password=password,
                database="postgres",
            )
            connection.autocommit = True
            cursor = connection.cursor()
            cursor.execute(sql.SQL(f"CREATE DATABASE {database_name}"))
            print(f"Database '{database_name}' created successfully.")
            cursor.close()
            connection.close()
        except OperationalError as e:
            print(f"Error while creating database: {e}")
            return None, None, None, None, None
    return (host_name, port_num, user, password, database_name)


def main():
    db_info = create_or_connectdb()
    test_true = True
    connection = None
    cursor = None
    encrypted_db = None

    try:
        while test_true:
            connection, cursor, encrypted_db = connect_to_database(*db_info)
            if connection is None:
                print("Restart the program and check if you input the correct data")
                break
            if connection:
                stop = user_sql_terminal(cursor, connection, encrypted_db)
                if not stop:
                    break
    except KeyboardInterrupt:
        # Handles issues if the user press ctrl C
        print("\nCtrl + C pressed. Encrypting database before closing...")
        if connection and cursor and encrypted_db:
            encrypted_db.encrypt_database(cursor)
            connection.commit()
            cursor.close()
            connection.close()
            print("Database connection closed.")
    finally:
        if connection:
            if cursor and encrypted_db:
                encrypted_db.encrypt_database(cursor)
                connection.commit()
            cursor.close()
            connection.close()
            print("Database connection closed.")


# def display_database(cursor):
#     cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
#     db_list = cursor.fetchall()
#     print("Databases:")
#     for db in db_list:
#         print(f" - {db[0]}")

#     cursor.execute(
#         "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
#     )
#     tables = cursor.fetchall()
#     if tables:
#         print("Tables in the current database:")
#         for table in tables:
#             print(f" - {table[0]}")
#     else:
#         print("No tables in the current database.")

# I am ARE USING THIS AND QUERYENCRYPT FROM NOW ON,
# old cold I may keep if i want to make changes
# def user_sql_terminal(cursor, connection, encrypted_db) -> bool:
#     run = True
#     while run:
#         try:
#             user_query = input(
#                 "Enter SQL query (type 'exit' or '\\q' to quit, type 'select all' to view a table): "
#             )
#             if user_query.strip().lower() in ("exit", "\\q"):
#                 # Encrypt all tables before closing
#                 print("Encrypting database before closing...")
#                 encrypted_db.encrypt_database(cursor)
#                 connection.commit()
#                 cursor.close()
#                 connection.close()
#                 run = False
#                 return False

#             elif user_query.strip().lower() in ("select all"):
#                 table_name = input("Type your table name: ")
#                 columns = get_all_columns(table_name, cursor)
#                 print(f"Columns for table {table_name}:\n")
#                 print(f"{'Column':<20} {'Type':<20} {'Nullable':<10}")
#                 print("-" * 50)
#                 for column in columns:
#                     print(f"{column[0]:<20} {column[1]:<20} {column[2]:<10}")

#             elif user_query.strip().upper().startswith("CREATE TABLE"):
#                 try:
#                     cursor.execute(user_query)
#                     connection.commit()
#                     table_name = re.search(
#                         r"CREATE TABLE\s+(\w+)", user_query, re.IGNORECASE
#                     )
#                     if table_name:
#                         verify_query = """
#                         SELECT EXISTS (
#                             SELECT FROM information_schema.tables
#                             WHERE table_name = %s
#                         );
#                         """
#                         cursor.execute(verify_query, (table_name.group(1),))
#                         if cursor.fetchone()[0]:
#                             print(
#                                 f"Table '{table_name.group(1)}' created successfully."
#                             )
#                         else:
#                             print(f"Failed to create table '{table_name.group(1)}'.")
#                 except Exception as e:
#                     print(f"Error creating table: {e}")
#                     connection.rollback()

#             elif user_query.strip().lower().startswith("select"):
#                 try:
#                     results = encrypted_db.execute(cursor, user_query)
#                     if results is not None:
#                         for row in results:
#                             print(row)
#                     else:
#                         print(
#                             "Query executed successfully, no rows returned or there is nothing in the table."
#                         )

#                 except Exception as e:
#                     print(f"Error executing query: on line 152 {e}")
#                     connection.rollback()

#                 results = encrypted_db.execute(cursor, user_query)
#                 if results is not None:
#                     for row in results:
#                         print(row)
#                 else:
#                     print(
#                         "Query executed successfully, no rows returned or there is nothing in the table."
#                     )

#             elif user_query.strip().upper().startswith("INSERT INTO"):
#                 try:
#                     cursor.execute(user_query)
#                     connection.commit()
#                     print("Data inserted successfully.")
#                 except Exception as e:
#                     print(f"Error executing query: on line 155 {e}")
#                     connection.rollback()

#             else:
#                 encrypted_db.execute(cursor, user_query)
#                 connection.commit()
#                 print("Query executed successfully.")
#         except ValueError as ve:
#             print(f"ValueError: {ve}")
#             connection.rollback()
#         except TypeError as te:
#             print(f"TypeError: {te}")
#             connection.rollback()
#         except Exception as e:
#             print(f"Unexpected error: {e}")
#             connection.rollback()

# def main():
#     db_info = create_or_connectdb()
#     test_true = True
#     try:
#         while test_true:
#             connection = connect_to_database(*db_info)
#             if connection is None:
#                 print("Restart the program and check if you input the correct data")
#                 break
#             if connection:
#                 cursor = connection.cursor()
#                 encrypted_db = queryencrypt.EncryptedDatabase()
#                 stop = user_sql_terminal(cursor, connection, encrypted_db)
#                 if not stop:
#                     break
#     except KeyboardInterrupt:
#         print("\nCtrl + C pressed. Closing the database connection and exiting.")
#     finally:
#         if connection:
#             cursor.close()
#             connection.close()
#             print("Database connection closed.")

# def get_all_columns(table_name, cursor):
#     query = f"""
#     SELECT column_name, data_type, is_nullable
#     FROM information_schema.columns
#     WHERE table_name = '{table_name}';
#     """
#     cursor.execute(query)
#     return cursor.fetchall()


# def connect_to_database(host, port, user, password, db_name):
#     try:
#         connection = psycopg2.connect(
#             host=host, port=port, user=user, password=password, database=db_name
#         )
#         print(f"Connected to the database '{db_name}' successfully.")
#         return connection
#     except OperationalError as e:
#         print(f"Error connecting to the database: {e}")
#         return None


# def display_database(cursor):
#     cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
#     db_list = cursor.fetchall()
#     print("Databases:")
#     for db in db_list:
#         print(f" - {db[0]}")

#     cursor.execute(
#         "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
#     )
#     tables = cursor.fetchall()
#     if tables:
#         print("Tables in the current database:")
#         for table in tables:
#             print(f" - {table[0]}")
#     else:
#         print("No tables in the current database.")


if __name__ == "__main__":
    main()
