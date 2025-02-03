from cryptography.fernet import Fernet
import psycopg2
import re
import os
import keyring


# NEED PIP INSTALL
class EncryptedDatabase:
    def __init__(self):
        # Load or generate the encryption key
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)

    # Future method will let the user chooes what file to write the key to. and have the option to change files if the wrong key is there
    # def key_file_check():
    #     cwd = os.getcwd()
    #     folder_name = "key_file"
    #     folder_path = os.path.join(cwd, folder_name)
    #     if not os.path.exists(folder_path):
    #         os.makedirs(folder_path)

    # AS OF NOW THE PROGRAM CAN ONLY WORK WITH 1 DATABASE BECAUSE OF HOW THE KEY IS HANDLED
    # takes a path, returns a key
    # def load_or_generate_key(self) -> bytes:
    #     """Load the key from a file, or generate a new one and save it."""
    #     # MAY CHANGE TO SAVE KEY FILE IN DOWNLOADS OR A SECURE SPOT IN DB
    #     # DB MAY HAVE TO HAVE A MARKING SO IT KNOWS WHICH SAVED KEY IS WHICH
    #     # Create the directory if it doesn't exist
    #     cwd = os.getcwd()
    #     folder_name = "key_file"
    #     key_folder_path = os.path.join(cwd, folder_name)
    #     key_file_path = os.path.join(key_folder_path, "secret.key")

    #     # If file does not exist
    #     if not os.path.exists(key_file_path):
    #         os.makedirs(key_folder_path)
    #         print(f"Directory '{key_file_path}' created.")

    #     # Check if the key file already exists
    #     if os.path.exists(key_file_path):
    #         with open(key_file_path, "rb") as file:
    #             key = file.read()
    #             print("Encryption key loaded from file.")
    #     else:
    #         # Generate a new key and save it to the file
    #         key = Fernet.generate_key()
    #         with open(key_file_path, "wb") as file:
    #             file.write(key)
    #             print("New encryption key generated and saved to file.")
    #     return key

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

    def encrypt_database(self, cursor):
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

    def decrypt_database(self, cursor):
        """Decrypts the database"""
        cursor.execute(
            "SELECT table_name FROM information_schema.tables WHERE table_schema = 'public';"
        )
        tables = cursor.fetchall()
        for table in tables:
            table_name = table[0]
            cursor.execute(f"SELECT * FROM {table_name};")
            rows = cursor.fetchall()
            columns = [desc[0] for desc in cursor.description]

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

    # def execute(self, cursor, query, params):
    #     # Automatically encrypt data for INSERT or UPDATE queries
    # if params is None:
    #     params = []

    # # params: This is a list or tuple of values
    # encrypted_params = [
    #     self.encrypt(param) if isinstance(param, str) else param
    #     for param in params
    # ]

    # # print(encrypted_params)
    # # print(query)
    # cursor.execute(query, encrypted_params)

    # Gpt explains the issue

    # The issue with your decryption code arose because PostgreSQL stores binary data (bytea type) in a hex-encoded format (e.g., \\x674141...).
    # When you queried the database, the encrypted data was returned as a hex string rather than raw bytes.
    # Your decryption function was expecting raw byte data, so when it received a hex-encoded string instead, it couldn’t decrypt it.
    # The solution involved checking if the data was hex-encoded (by looking for the \\x prefix) and converting it back to raw bytes using bytes.fromhex().
    # This way, the decrypted data could be processed correctly, fixing the problem and allowing your code to return the actual decrypted values.
    # def decrypt_execute(self, cursor, query):
    #     """Automatically decrypt data for SELECT queries"""
    #     try:
    #         if re.match(r"^\s*SELECT", query, re.IGNORECASE):
    #             cursor.execute(query)
    #             rows = cursor.fetchall()

    #             if not rows:
    #                 return []

    #         decrypted_rows = []
    #         for row in rows:
    #             decrypted_values = []
    #             for col in row:
    #                 try:
    #                     if isinstance(col, str) and col.startswith("\\x"):
    #                         # Handle encrypted data
    #                         decrypted_value = self.decrypt(bytes.fromhex(col[2:]))
    #                         decrypted_values.append(decrypted_value)
    #                     else:
    #                         # Pass through non-encrypted data
    #                         decrypted_values.append(col)
    #                 except Exception as e:
    #                     print(f"Error decrypting value {col}: {str(e)}")
    #                     decrypted_values.append(col)
    #             decrypted_rows.append(tuple(decrypted_values))

    #         return decrypted_rows
    #     except Exception as e:
    #         print(f"Error in decrypt_execute: {str(e)}")
    #         raise

    # def normal_execute(self, cursor, query):
    #     cursor.execute(query)
    #     print("executed query {query}")

    # def encrypt(self, plaintext):
    #     return self.cipher.encrypt(plaintext.encode())

    # def decrypt(self, ciphertext):
    #     return self.cipher.decrypt(ciphertext).decode()
