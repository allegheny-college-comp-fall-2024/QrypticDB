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


def main():
    # Define pre set PostgreSQL credentials
    host = "localhost"
    port = "5432"
    user = "postgres"
    password = "your_password"
    target_db = "my_new_database"

    # connect to the target database
    connection = connect_to_database(host, port, user, password, target_db)

    if connection is None:
        # If no connection (database might not exist), create a new database
        print(f"Database '{target_db}' not found, attempting to create it.")
        create_database(host, port, user, password, target_db)

        # tries connecting to the new
        connection = connect_to_database(host, port, user, password, target_db)

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

        # Close the connection
        cursor.close()
        connection.close()


if __name__ == "__main__":
    main()
