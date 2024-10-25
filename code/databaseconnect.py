import psycopg2
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
            # Next is to pass the data in to the llm to generate decoy data to simulate superposition
            # When the user enters the correct password, db should be decerypted and their queries should use
            # lazy eval to get the correct data
            user_query = input("Enter SQL query (or type 'exit' or '\\q' to quit):")
            if user_query.strip().lower() in ("exit", "\\q"):
                cursor.close()
                connection.close()
                run = False
                return False
            cursor.execute(user_query)
            connection.commit()
        except Exception as e:
            print(f"Error executing query: {e}")


def main():
    # pre set PostgreSQL credentials for test
    host = "localhost"
    port = "5432"
    user = "postgres"
    password = "your_password"
    target_db = "my_new_database23"

    test_true = True
    connection = None
    try:
        while test_true:
            # connect to the target database
            connection = connect_to_database(host, port, user, password, target_db)

            if connection is None:
                # If no connection (database might not exist), create a new database
                print(f"Database '{target_db}' not found, would you like to create it?")
                # Add button here for yes or no
                user_ans = input("y/n?")
                if user_ans.lower() == "y":
                    # tries connecting to the new
                    create_database(host, port, user, password, target_db)
                else:
                    print("The database was not been created")

            if connection:
                # does database stuff if connected
                cursor = connection.cursor()

                # Create a sample table if one does not exists
                cursor.execute("""
                    CREATE TABLE IF NOT EXISTS public.test_table (
                        id SERIAL PRIMARY KEY,
                        name VARCHAR(100)
                    );
                """)
                print("Table 'test_table' created successfully.")
                print("You can now run SQL queries on this database.")
                stop = user_sql_terminal(cursor, connection)
                if stop == False:
                    break
                # INSERT INTO name (brand, model, year) VALUES ('Ford', 'Mustang', 1964')

        # Close the connection
    except KeyboardInterrupt:
        print("\nCtrl + C pressed. Closing the database connection and exiting.")
    finally:
        # Close the connection if it exists
        if connection:
            connection.close()
            print("Database connection closed.")
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
