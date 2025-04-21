import psycopg2
from psycopg2 import sql, OperationalError
import queryencrypt
import time
import sys


# is set to public becuase i don't think most people will change it
def print_database_schema(cursor, schema="public"):
    # Get all tables in the schema
    cursor.execute(
        """
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = %s;
    """,
        (schema,),
    )
    tables = cursor.fetchall()

    for table in tables:
        table_name = table[0]
        print(f"\nTable: {table_name}")
        cursor.execute(
            """
            SELECT column_name, data_type
            FROM information_schema.columns
            WHERE table_schema = %s AND table_name = %s;
        """,
            (schema, table_name),
        )
        columns = cursor.fetchall()

        for col in columns:
            print(f"  {col[0]} ({col[1]})")


def list_databases(cursor):
    try:
        # datistemplate = false filters out template databases (template0, template1) that PostgreSQL uses internally when creating new databases
        cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
        dbs = cursor.fetchall()
        print("Available Databases:")
        for db in dbs:
            print(f" - {db[0]}")
    except Exception as e:
        print(f"Error listing databases: {e}")


# SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';
# have this implemented so suer can see tables
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


def create_database(
    host: str, port: int, user: str, password: str, new_db_name: str
) -> None:
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

            # made raw so python knows its on purpose
            # elif user_query.strip().lower() == "dn":
            #     print_database_schema(cursor, schema="public")

            # # made raw so python knows its on purpose
            # elif user_query.strip().lower() == "l":
            #     list_databases(cursor)

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
            print(f"The Error: {e}")
            connection.rollback()


# Long function for creating or connecting to a database
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
#             return None, None
#         default_db = input("Would you like to use the default parameters? y/n?: \n")
#         if default_db.lower() == "n":
#             host_name = input("Please enter the host name: \n")
#             port_num = input("Please enter the port number: \n")
#             user = input("Please enter the user name: \n")
#             password = input("Please enter the password: \n")
#             database_name = input("Please enter the new database name: \n")

#         elif default_db.lower() == "y":
#             host_name = "localhost"
#             port_num = "5432"
#             user = "postgres"
#             password = "your_password"
#             database_name = "mynewdatabase57"

#         else:
#             print("Please enter a valid response")

#         print(
#             f"Your host name is {host_name}, port is {port_num}, the user is {user}, your password is {password}, your database name is {database_name}"
#         )
#         # If for some reason the above default database does not work, it will try
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


def create_or_connectdb() -> tuple:
    # Will either create a db or get db connection info
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
        # should check if there defualt already exists, if so, then it will not create a new one.
        # It will ask show all the databases using hte \l or SELECT datname FROM pg_database;
        default_db = input("Would you like to use the default parameters? y/n?: \n")
        if default_db.lower() == "n":
            host_name = input("Please enter the host name: \n")
            port_num = input("Please enter the port number: \n")
            user = input("Please enter the user name: \n")
            password = input("Please enter the password: \n")
            database_name = input("Please enter the new database name: \n")

        elif default_db.lower() == "y":
            host_name = "localhost"
            port_num = "5432"
            user = "postgres"
            password = "your_password"
            database_name = "mynewdatabase57"

        else:
            print("Please enter a valid response")

        print(
            f"Your host name is {host_name}, port is {port_num}, the user is {user}, your password is {password}, your database name is {database_name}"
        )

        # Create the database using the dedicated function
        try:
            create_database(host_name, port_num, user, password, database_name)
        except Exception as e:
            print(f"Error while creating database: {e}")
            print("That database already exists. Please try again.")
            sys.exit()

    return (host_name, port_num, user, password, database_name)


def main():
    print(
        "Do not set var or char limits, it will have cause an error due to the encrpytions length\n"
    )
    print("Please make the queries one line")
    time.sleep(2)
    db_info = create_or_connectdb()
    test_true = True
    # connection = None
    # cursor =
    # encrypted_db = None

    try:
        while test_true:
            # Connects to db by unpacking info from db_info
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
        # just makes sure the database is properly encrypted and closed
        if connection:
            if cursor and encrypted_db:
                encrypted_db.encrypt_database(cursor)
                connection.commit()
            cursor.close()
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
