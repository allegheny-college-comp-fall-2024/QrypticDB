from cryptography.fernet import Fernet
import psycopg2
import re
import os


class EncryptedDatabase:
    def __init__(self):
        # Load or generate the encryption key
        self.key = self.load_or_generate_key()
        self.cipher = Fernet(self.key)

    # Future method will let the user chooes what file to write the key to. and have the option to change files if the wrong key is there
    def key_file_check():
        cwd = os.getcwd()
        folder_name = "key_file"
        folder_path = os.path.join(cwd, folder_name)
        if not os.path.exists(folder_path):
            os.makedirs(folder_path)

    # AS OF NOW THE PROGRAM CAN ONLY WORK WITH 1 DATABASE BECAUSE OF HOW THE KEY IS HANDLED
    # takes a path, returns a key
    def load_or_generate_key(self) -> bytes:
        """Load the key from a file, or generate a new one and save it."""
        # MAY CHANGE TO SAVE KEY FILE IN DOWNLOADS OR A SECURE SPOT IN DB
        # DB MAY HAVE TO HAVE A MARKING SO IT KNOWS WHICH SAVED KEY IS WHICH
        # Create the directory if it doesn't exist
        cwd = os.getcwd()
        folder_name = "key_file"
        key_folder_path = os.path.join(cwd, folder_name)
        key_file_path = os.path.join(key_folder_path, "secret.key")

        # If file does not exist
        if not os.path.exists(key_file_path):
            os.makedirs(key_folder_path)
            print(f"Directory '{key_file_path}' created.")

        # Check if the key file already exists
        if os.path.exists(key_file_path):
            with open(key_file_path, "rb") as file:
                key = file.read()
                print("Encryption key loaded from file.")
        else:
            # Generate a new key and save it to the file
            key = Fernet.generate_key()
            with open(key_file_path, "wb") as file:
                file.write(key)
                print("New encryption key generated and saved to file.")
        return key

    def execute(self, cursor, query, params):
        # Automatically encrypt data for INSERT or UPDATE queries
        # if params is None:
        #     params = []
        if re.match(r"^\s*(INSERT|UPDATE)", query, re.IGNORECASE):
            # params: This is a list or tuple of values
            encrypted_params = [
                self.encrypt(param) if isinstance(param, str) else param
                for param in params
            ]

            # print(encrypted_params)
            # print(query)
            cursor.execute(query, encrypted_params)

    # Gpt explains the issue

    # The issue with your decryption code arose because PostgreSQL stores binary data (bytea type) in a hex-encoded format (e.g., \\x674141...).
    # When you queried the database, the encrypted data was returned as a hex string rather than raw bytes.
    # Your decryption function was expecting raw byte data, so when it received a hex-encoded string instead, it couldn’t decrypt it.
    # The solution involved checking if the data was hex-encoded (by looking for the \\x prefix) and converting it back to raw bytes using bytes.fromhex().
    # This way, the decrypted data could be processed correctly, fixing the problem and allowing your code to return the actual decrypted values.
    def decrypt_execute(self, cursor, query):
        # Automatically decrypt data for SELECT queries
        if re.match(r"^\s*SELECT", query, re.IGNORECASE):
            cursor.execute(query)
            rows = cursor.fetchall()
            #     for i in rows:
            #         if isinstance(i, bytes):
            #             self.decrypt(i)
            #     return rows

            decrypted_rows = [
                tuple(
                    self.decrypt(bytes.fromhex(col[2:]))
                    if isinstance(col, str) and col.startswith("\\x")
                    else col
                    for col in row
                )
                for row in rows
            ]
            return decrypted_rows

    def normal_execute(self, cursor, query):
        cursor.execute(query)
        print("executed query {query}")

    def encrypt(self, plaintext):
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext):
        return self.cipher.decrypt(ciphertext).decode()

    def close(self):
        self.cursor.close()
        self.connection.close()
