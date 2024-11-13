import psycopg2
import QrypticDB.QrypticDB.deadcode.Nonaidecoy as Nonaidecoy
from psycopg2 import sql, OperationalError


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


def user_sql_terminal(cursor, connection) -> bool:
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

            # If the query is a SELECT statement
            elif user_query.strip().lower().startswith("select"):
                cursor.execute(user_query)
                rows = cursor.fetchall()
                if rows:
                    for row in rows:
                        print(row)
                else:
                    print("No data found.")

            elif user_query.strip().upper().startswith("INSERT INTO"):
                # If it's an insert statement, make the decoys
                # IF SET TOO HIGH WILL CAUSE ERROR, NOT ENOUGH
                try:
                        
                        except Exception as e:
                            print(f"Error executing query: {e}")
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

            # For non-SELECT queries
            else:
                cursor.execute(user_query)
                connection.commit()
                print("Query executed successfully.")

        except Exception as e:
            print(f"Error executing query: {e}")


def create_or_connectdb() -> tuple(str, str, str, str, str):
    """Creates a db or connects to one"""
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
            print("goodbye")

        else:
            default_db = input("Would you like to use the default parameters? y/n?: \n")
            if default_db.lower == "n":
                host_name = input("Please enter the host name: \n")
                port_num = input("Please enter the port number: \n")
                user = input("Please enter the user name: \n")
                password = input("Please enter the password: \n")
                database_name = input("Please enter the new database name: \n")

            else:
                # Preset PostgreSQL credentials for testing
                host_name = "localhost"
                port_num = "5432"
                user = "postgres"
                password = "your_password"
                database_name = "my_new_database"  # old was 23
                print(
                    f"Your host name is {host_name}, port is {port_num}, the user is {user}, your password is {password}, your database name is {database_name}  "
                )

    return (host_name, port_num, user, password, database_name)


def main():
    db_info = create_or_connectdb()
    test_true = True
    connection = None
    try:
        while test_true:
            # Connect to the target database
            connection = connect_to_database(db_info)

            if connection is None:
                print("Restart the program and check if you input the correct data")
                break  # Exit if user chooses not to create the database

            if connection:
                # Connection successful, proceed with database operations
                cursor = connection.cursor()

                # # Create a sample table if one does not exist
                # cursor.execute("""
                #     CREATE TABLE IF NOT EXISTS public.test_table (
                #         id SERIAL PRIMARY KEY,
                #         name VARCHAR(100)
                #     );
                # """)
                # connection.commit()  # Ensure changes are saved
                # print("Table 'test_table' created successfully.")
                # print("You can now run SQL queries on this database.")

                # Start the user SQL terminal
                stop = user_sql_terminal(cursor, connection)
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
