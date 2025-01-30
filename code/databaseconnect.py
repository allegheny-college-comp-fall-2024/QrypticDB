import psycopg2

# import QrypticDB.QrypticDB.deadcode.Nonaidecoy as Nonaidecoy
from psycopg2 import sql, OperationalError
import queryencrypt
import re


def connect_to_database(host, port, user, password, db_name):
    try:
        connection = psycopg2.connect(
            host=host, port=port, user=user, password=password, database=db_name
        )
        print(f"Connected to the database '{db_name}' successfully.")
        return connection
    except OperationalError as e:
        print(f"Error connecting to the database: {e}")
        return None


def get_all_columns(table_name, cursor):
    query = f"""
    SELECT column_name, data_type, is_nullable
    FROM information_schema.columns
    WHERE table_name = '{table_name}';
    """
    cursor.execute(query)
    return cursor.fetchall()


# Function to create a new database
def create_database(host, port, user, password, new_db_name):
    try:
        # Connects to the default postgres database to create a new database
        connection = psycopg2.connect(
            host=host,
            port=port,
            user=user,
            password=password,
            database="postgres",  # GPT said to always connect to the default postgres database to create a new one
        )
        connection.autocommit = True
        cursor = connection.cursor()

        # Create the new database
        cursor.execute(sql.SQL(f"CREATE DATABASE {new_db_name}"))
        print(f"Database '{new_db_name}' created successfully.")
        cursor.close()
        connection.close()

    except OperationalError as e:
        print(f"Error while creating database: {e}")


def display_database(cursor):
    cursor.execute("SELECT datname FROM pg_database WHERE datistemplate = false;")
    db_list = cursor.fetchall()
    print("Databases:")
    for db in db_list:
        print(f" - {db[0]}")

    cursor.execute(
        "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
    )
    tables = cursor.fetchall()
    if tables:
        print("Tables in the current database:")
        for table in tables:
            print(f" - {table[0]}")
    else:
        print("No tables in the current database.")


# SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';


def user_sql_terminal(cursor, connection, encrypted_db) -> bool:
    run = True
    while run:
        try:
            # Prompt for SQL query input
            user_query = input(
                "Enter SQL query (type 'exit' or '\\q' to quit, tpye 'select all' to view a table): "
            )
            if user_query.strip().lower() in ("exit", "\\q"):
                cursor.close()
                connection.close()
                run = False
                return False

            # gets metadata
            elif user_query.strip().lower() in ("select all"):
                table_name = input("Type your table name: ")
                columns = get_all_columns(table_name, cursor)
                print(f"Columns for table {table_name}:\n")
                print(f"{'Column':<20} {'Type':<20} {'Nullable':<10}")
                print("-" * 50)
                for column in columns:
                    print(f"{column[0]:<20} {column[1]:<20} {column[2]:<10}")

            # added stuff function. idk why it was not working berfor
            elif user_query.strip().upper().startswith("CREATE TABLE"):
                try:
                    cursor.execute(user_query)
                    connection.commit()  # Important: Commit the CREATE TABLE

                    # Verify table creation
                    table_name = re.search(
                        r"CREATE TABLE\s+(\w+)", user_query, re.IGNORECASE
                    )
                    if table_name:
                        verify_query = """
                        SELECT EXISTS (
                            SELECT FROM information_schema.tables 
                            WHERE table_name = %s
                        );
                        """
                        cursor.execute(verify_query, (table_name.group(1),))
                        if cursor.fetchone()[0]:
                            print(
                                f"Table '{table_name.group(1)}' created successfully."
                            )
                        else:
                            print(f"Failed to create table '{table_name.group(1)}'.")
                except Exception as e:
                    print(f"Error creating table: {e}")
                    connection.rollback()

            # If the query is a SELECT statement
            elif user_query.strip().lower().startswith("select"):
                results = encrypted_db.decrypt_execute(cursor, user_query)
                if results is not None:
                    for row in results:
                        print(row)
                else:
                    print(
                        "Query executed successfully, no rows returned or there is nothing in the table."
                    )

            # GPT to solve issue of not encrypting
            # If the query is an INSERT statement
            elif user_query.strip().upper().startswith("INSERT INTO"):
                try:
                    # Extract values from the query (handling multiple tuples correctly)
                    match = re.search(r"VALUES\s*(\(.+\))", user_query, re.IGNORECASE)
                    if match:
                        values_str = match.group(1)

                        # Extract tuples properly using regex
                        value_tuples = re.findall(r"\(([^)]+)\)", values_str)

                        params = []
                        for tuple_str in value_tuples:
                            values = [
                                v.strip().strip("'\"") for v in tuple_str.split(",")
                            ]

                            # Convert to appropriate types (int, float, or keep as string)
                            for i, v in enumerate(values):
                                if v.isdigit():
                                    values[i] = int(v)
                                else:
                                    try:
                                        values[i] = float(v)
                                    except ValueError:
                                        pass  # Keep as string

                            params.extend(values)  # Flatten into params list

                        # Create the correct number of placeholders
                        placeholders = ", ".join(
                            [
                                "("
                                + ", ".join(["%s"] * len(value_tuples[0].split(",")))
                                + ")"
                            ]
                            * len(value_tuples)
                        )

                        # Replace the VALUES section with placeholders
                        query_with_placeholders = re.sub(
                            r"VALUES\s*\(.+\)", f"VALUES {placeholders}", user_query
                        )

                        print("Original Params:", params)
                        print("Modified Query:", query_with_placeholders)

                        # Execute the query with placeholders and params
                        encrypted_db.execute(cursor, query_with_placeholders, params)
                        connection.commit()
                        print("Data inserted successfully.")
                    else:
                        print("Could not extract values from the query.")
                except Exception as e:
                    print(f"Error executing query: {e}")
                    connection.rollback()

                # For other non-SELECT queries
                try:
                    cursor.execute(user_query)
                    connection.commit()
                    print("Query executed successfully.")
                except Exception as e:
                    print(f"Error executing query: {e}")
                    connection.rollback()

        except Exception as e:
            print(f"Unexpected error: {e}")
            connection.rollback()
        except ValueError as ve:
            print(f"ValueError: {ve}")
            connection.rollback()  # Rollback any changes if there's an error

        except TypeError as te:
            print(f"TypeError: {te}")
            connection.rollback()

        except Exception as e:
            print(f"Unexpected error: {e}")
            connection.rollback()

        except Exception as e:
            print(f"Error executing query: {e}")


def create_or_connectdb() -> tuple:
    """Creates a database or connects to one."""
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
            exit()

        default_db = input("Would you like to use the default parameters? y/n?: \n")
        if default_db.lower() == "y":
            host_name = "localhost"
            port_num = "5432"
            user = "postgres"
            password = "your_password"
            database_name = "keyring"

        else:
            host_name = input("Please enter the host name: \n")
            port_num = input("Please enter the port number: \n")
            user = input("Please enter the user name: \n")
            password = input("Please enter the password: \n")
            database_name = input("Please enter the new database name: \n")

    # Try to connect to the target database
    try:
        connection = psycopg2.connect(
            host=host_name,
            port=port_num,
            user=user,
            password=password,
            database=database_name,
        )
        print(f"Successfully connected to {database_name}.")
        connection.close()

    except psycopg2.OperationalError:
        print(f"Database {database_name} does not exist. Creating it...")

        # Connect to default 'postgres' database to create the new database
        try:
            conn = psycopg2.connect(
                host=host_name,
                port=port_num,
                user=user,
                password=password,
                database="postgres",
            )
            conn.autocommit = True
            cursor = conn.cursor()
            cursor.execute(f"CREATE DATABASE {database_name};")
            print(f"Database {database_name} created successfully.")
            cursor.close()
            conn.close()
        except Exception as e:
            print(f"Failed to create database: {e}")
            exit()

    return (host_name, port_num, user, password, database_name)


def main():
    db_info = create_or_connectdb()
    test_true = True
    try:
        while test_true:
            # Connect to the target database
            # The * unpacks the tuple
            connection = connect_to_database(*db_info)

            if connection is None:
                print("Restart the program and check if you input the correct data")
                break

            if connection:
                cursor = connection.cursor()

                encrypted_db = queryencrypt.EncryptedDatabase()
                # Start the user SQL terminal
                stop = user_sql_terminal(cursor, connection, encrypted_db)
                if not stop:
                    break

    except KeyboardInterrupt:
        print("\nCtrl + C pressed. Closing the database connection and exiting.")
    finally:
        # Close the connection and cursor if they exist
        if connection:
            cursor.close()
            connection.close()
            print("Database connection closed.")


if __name__ == "__main__":
    main()
