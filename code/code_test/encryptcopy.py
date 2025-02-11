from cryptography.fernet import Fernet
import psycopg2
import re
import os
import keyring
import time


# NEED PIP INSTALL
class EncryptedDatabase:
    def __init__(self):
        # Load or generate the encryption key
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)

    def load_or_generate_key(self) -> bytes:
        """Load the key from the system keyring, or generate and store it securely."""
        service_name = "EncryptedDatabase"
        key_name = "encryption_key"  # Single key for all databases

        try:
            # Try to get existing key
            key = keyring.get_password(service_name, key_name)

            if key:
                print("Encryption key loaded from system keyring")
                return key.encode()

            # If no key exists, generate new one
            new_key = Fernet.generate_key()
            # Store the key as a string in keyring
            keyring.set_password(service_name, key_name, new_key.decode())
            print("New encryption key generated and stored in system keyring")
            return new_key

        except Exception as e:
            raise RuntimeError(f"Error accessing system keyring: {e}")

    def encrypt(self, plaintext: str) -> str:
        return self.cipher.encrypt(plaintext.encode()).decode()

    def decrypt(self, ciphertext: str) -> str:
        return self.cipher.decrypt(ciphertext.encode()).decode()

    # This function will ONLY encrypt the data in columns, not the columns itself as that is used for the sql queries
    def encrypt_database(self, cursor, connection):
        start_time = time.time()
        # Step 1: Retrieve all table names in the public schema
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()

        # Step 2: Iterate over each table
        for table in tables:
            table_name = table[0]

            # Step 3: Retrieve all rows from the current table
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()

            # Step 4: Get the column names of the current table
            columns = [desc[0] for desc in cursor.description]

            # Step 5: Iterate over each row in the table
            for row in rows:
                # Step 6: Encrypt each string value in the row
                encrypted_row = [
                    self.encrypt(str(value)) if isinstance(value, str) else value
                    for value in row
                ]

                # Step 7: Create the SET clause for the UPDATE statement
                set_clause = ", ".join([f"{col} = %s" for col in columns])

                # Step 8: Create the UPDATE query
                update_query = (
                    f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s;"
                )

                # Step 9: Execute the UPDATE query with the encrypted values
                cursor.execute(update_query, encrypted_row + [row[0]])
        end_time = time.time()
        elpased_time = end_time - start_time
        print(f"elpased_time is {elpased_time}")
        connection.commit()
        cursor.close()
        connection.close()
        print("Database connection closed.")

    def decrypt_database(self, cursor):
        """Decrypts the database"""
        start_time = time.time()
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()
        # iterates through the tables and gets the data
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

            # looks for data starting with gAAAA then decrpyts it
            for row in rows:
                decrypted_row = [
                    self.decrypt(value)
                    if isinstance(value, str) and value.startswith("gAAAA")
                    else value
                    for value in row
                ]
                set_clause = ", ".join([f"{col} = %s" for col in columns])
                update_query = (
                    f"UPDATE {table_name} SET {set_clause} WHERE {columns[0]} = %s;"
                )
                cursor.execute(update_query, decrypted_row + [row[0]])
        end_time = time.time()
        elapsed_time = end_time - start_time
        print(f"decrypt time is {elapsed_time}")

    def execute(self, cursor, query):
        """Executes query"""
        try:
            # Execute the query
            cursor.execute(query)

            # Try to fetch results (for SELECT queries)
            try:
                results = cursor.fetchall()
                return results
            except psycopg2.ProgrammingError:
                # This happens for non-SELECT queries (INSERT, UPDATE, DELETE)
                return None

        except Exception as e:
            print(f"Error executing query: {e}")
            raise

    def close(self):
        self.cursor.close()
        self.connection.close()
