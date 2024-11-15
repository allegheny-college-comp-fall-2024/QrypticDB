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

    def execute(self, cursor, query, params=None):
        # Automatically encrypt data for INSERT or UPDATE queries
        if re.match(r"^\s*(INSERT|UPDATE)", query, re.IGNORECASE):
            encrypted_params = [
                self.encrypt(param) if isinstance(param, str) else param
                for param in params
            ]
            cursor.execute(query, encrypted_params)

        # Automatically decrypt data for SELECT queries
        elif re.match(r"^\s*SELECT", query, re.IGNORECASE):
            cursor.execute(query, params)
            rows = cursor.fetchall()
            decrypted_rows = [
                tuple(
                    self.decrypt(col) if isinstance(col, bytes) else col for col in row
                )
                for row in rows
            ]
            return decrypted_rows

        # For other types of queries
        else:
            cursor.execute(query, params)

    def encrypt(self, plaintext):
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext):
        return self.cipher.decrypt(ciphertext).decode()

    def close(self):
        self.cursor.close()
        self.connection.close()
