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

    def load_or_generate_key(self) -> bytes:
        """Load the key from the system keyring, or generate and store it securely."""
        service_name = "EncryptedDatabase"
        key_name = "encryption_key"  # Single key for all databases

        try:
            # Try to get existing key, looks for nane in key ring
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

                # encrypted_row = []
                # for value in rows:
                #         encrypted_value = self.encrypt(value)
                #         encrypted_row.append(encrypted_value)

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


# from cryptography.hazmat.primitives.ciphers import Cipher, algorithms, modes
# from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
# from cryptography.hazmat.primitives import hashes
# from cryptography.hazmat.backends import default_backend
# import os
# import base64
# import keyring

# class EncryptedDatabase:
#     def __init__(self):
#         self.key = self.load_or_generate_key()
#         self.backend = default_backend()
#         self.block_size = algorithms.AES.block_size // 8

#     def load_or_generate_key(self) -> bytes:
#         service_name = "EncryptedDatabase"
#         key_name = "encryption_key"

#         try:
#             key = keyring.get_password(service_name, key_name)
#             if key:
#                 print("Encryption key loaded from system keyring")
#                 return base64.urlsafe_b64decode(key)

#             new_key = os.urandom(32)
#             keyring.set_password(service_name, key_name, base64.urlsafe_b64encode(new_key).decode())
#             print("New encryption key generated and stored in system keyring")
#             return new_key

#         except Exception as e:
#             raise RuntimeError(f"Error accessing system keyring: {e}")

#     def encrypt(self, plaintext: str) -> str:
#         iv = os.urandom(self.block_size)
#         cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=self.backend)
#         encryptor = cipher.encryptor()
#         ciphertext = encryptor.update(plaintext.encode()) + encryptor.finalize()
#         return base64.urlsafe_b64encode(iv + ciphertext).decode()

#     def decrypt(self, ciphertext: str) -> str:
#         data = base64.urlsafe_b64decode(ciphertext)
#         iv = data[:self.block_size]
#         cipher = Cipher(algorithms.AES(self.key), modes.CFB(iv), backend=self.backend)
#         decryptor = cipher.decryptor()
#         plaintext = decryptor.update(data[self.block_size:]) + decryptor.finalize()
#         return plaintext.decode()

#     # ... rest of the class remains unchanged ...
