import psycopg2
from psycopg2 import sql, OperationalError

# from encryptcopy import EncryptedDatabase
import re
import coderuntest
import time


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
                database_name = "mynewdatabase41"

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


def execute_queries_from_file(cursor, connection, filename, max_queries_per_file):
    """
    Reads and executes SQL queries from a file, processing max_queries_per_file before moving to next file.

    :param cursor: Database cursor
    :param connection: Database connection
    :param filename: The CSV file containing SQL queries
    :param max_queries_per_file: Maximum number of queries to execute per file
    :return: Number of queries executed for this file
    """
    count = 0
    try:
        with open(filename, "r") as file:
            print(f"\nProcessing {filename}")
            for line in file:
                # Check if we've hit the max queries for this file
                if count >= max_queries_per_file:
                    print(
                        f"Reached {max_queries_per_file} queries in {filename}. Moving to next file."
                    )
                    return count

                query = line.strip()  # Remove any whitespace/newlines

                if query.endswith(";"):
                    try:
                        cursor.execute(query)
                        connection.commit()
                        count += 1
                        print(f"Executed query {count}/{max_queries_per_file}")
                    except psycopg2.ProgrammingError as e:
                        if "no results to fetch" in str(e):
                            connection.commit()
                            print("Query executed successfully.")
                        else:
                            print(f"Error executing query: {e}")
                            connection.rollback()
                            return count  # Stop execution on error
                    except Exception as e:
                        print(f"Error: {e}")
                        connection.rollback()
                        return count  # Stop execution on error

    except Exception as e:
        print(f"Error reading file {filename}: {e}")

    return count


def user_sql_terminal(cursor, connection, encrypted_db):
    files = ["encryption_test_data.csv", "or.csv", "pr.csv"]
    max_queries_per_file = 10
    total_count = 0

    for file in files:
        print(f"\nStarting file: {file}")
        queries_processed = execute_queries_from_file(
            cursor, connection, file, max_queries_per_file
        )
        total_count += queries_processed
        print(f"Processed {queries_processed} queries from {file}")

    print(f"\nTotal queries executed across all files: {total_count}")


def check_and_create_table(cursor):
    # Define the table creation SQL statements
    tables = {
        "customers": "CREATE TABLE Customers (customer_id SERIAL PRIMARY KEY, name VARCHAR NOT NULL, email VARCHAR UNIQUE NOT NULL, phone VARCHAR, address TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP);",
        "orders": "CREATE TABLE Orders (order_id SERIAL PRIMARY KEY, total_amount DECIMAL(10,2) NULL, status VARCHAR DEFAULT 'Pending');",
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
                time.sleep(1)
            else:
                print(f"The table {table_name} already exists.")
                print("Dropping the table to make a new one")
                time.sleep(1)
                cursor.execute(
                    sql.SQL("DROP TABLE IF EXISTS {} CASCADE").format(
                        sql.Identifier(table_name)
                    )
                )

                print(f"The table {table_name} was dropped successfully.")
                time.sleep(1)
                print(f"Creating table {table_name}...")
                cursor.execute(creation_sql)
                print(f"The table {table_name} was created successfully.")

    except psycopg2.Error as e:
        print(f"Error executing query: {e}")


def main2():
    from encryptcopy import EncryptedDatabase

    try:
        # Connect to the database once
        connection, cursor, encrypted_db, elapsed_time = handle_database_connection()

        if connection is None:
            print("Restart the program and check if you input the correct data")
            return

        print("Going to make and check table...")
        check_and_create_table(cursor)

        print(f"Elapsed time: {elapsed_time}")

        # Run SQL terminal to insert queries
        user_sql_terminal(cursor, connection, encrypted_db)

        # Encrypt the database after inserting queries
        if connection and cursor and encrypted_db:
            encrypted_dbvar2 = EncryptedDatabase()
            encrypted_dbvar2.encrypt_database(cursor, connection)
            print("Database successfully encrypted.")

    except KeyboardInterrupt:
        print("\nCtrl + C pressed. Encrypting database before closing...")
        if connection and cursor and encrypted_db:
            encrypted_db.encrypt_database(cursor, connection)
            print("Database encrypted before exit.")

    except Exception as e:
        print(f"An error occurred: {e}")

    finally:
        # Ensure the database connection is always closed
        if connection:
            if cursor:
                cursor.close()
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main2()
