import psycopg2
import Nonaidecoy
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
                # IF SET TOO HIGH WILL CAUSE ERROR, NOT ENOUGH SPACE
                number_of_decoys = 3

                # Parse the query to get table name, columns, and real values
                parsed_data = Nonaidecoy.query_parse(user_query)

                # Generate an insert statement with decoys
                query_with_decoys = Nonaidecoy.generate_insert_with_decoys(
                    user_query, parsed_data, number_of_decoys
                )

                # Execute the modified insert query
                cursor.execute(query_with_decoys)
                connection.commit()

            # For non-SELECT queries
            else:
                cursor.execute(user_query)
                connection.commit()
                print("Query executed successfully.")

        except Exception as e:
            print(f"Error executing query: {e}")


def main():
    # Preset PostgreSQL credentials for testing
    host = "localhost"
    port = "5432"
    user = "postgres"
    password = "your_password"
    target_db = "my_new_database23"

    test_true = True
    connection = None
    try:
        while test_true:
            # Connect to the target database
            connection = connect_to_database(host, port, user, password, target_db)

            if connection is None:
                # If no connection, prompt to create a new database
                print(f"Database '{target_db}' not found. Would you like to create it?")
                user_ans = input("y/n? ")
                if user_ans.lower() == "y":
                    create_database(host, port, user, password, target_db)
                else:
                    print("The database was not created.")
                    break  # Exit if user chooses not to create the database

            if connection:
                # Connection successful, proceed with database operations
                cursor = connection.cursor()

                # Create a sample table if one does not exist
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100)
                    );
                """)
                connection.commit()  # Ensure changes are saved
                print("Table 'test_table' created successfully.")
                print("You can now run SQL queries on this database.")

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
