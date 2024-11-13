from cryptography.fernet import Fernet
import psycopg2
import re


class EncryptedDatabase:
    def __init__(self, db_name, user, password, host="localhost"):
        # Generate or load the encryption key (In practice, store this securely)
        self.key = Fernet.generate_key()
        self.cipher = Fernet(self.key)
        self.connection = psycopg2.connect(
            database=db_name, user=user, password=password, host=host
        )
        self.cursor = self.connection.cursor()

    def execute(self, query, params=None):
        # Automatically encrypt data for INSERT or UPDATE queries
        if re.match(r"^\s*(INSERT|UPDATE)", query, re.IGNORECASE):
            encrypted_params = [
                self.encrypt(param) if isinstance(param, str) else param
                for param in params
            ]
            self.cursor.execute(query, encrypted_params)
        # Automatically decrypt data for SELECT queries
        elif re.match(r"^\s*SELECT", query, re.IGNORECASE):
            self.cursor.execute(query, params)
            rows = self.cursor.fetchall()
            decrypted_rows = [
                tuple(
                    self.decrypt(col) if isinstance(col, bytes) else col for col in row
                )
                for row in rows
            ]
            return decrypted_rows
        else:
            self.cursor.execute(query, params)

        self.connection.commit()

    def encrypt(self, plaintext):
        return self.cipher.encrypt(plaintext.encode())

    def decrypt(self, ciphertext):
        return self.cipher.decrypt(ciphertext).decode()

    def close(self):
        self.cursor.close()
        self.connection.close()


# Example usage
if __name__ == "__main__":
    db = EncryptedDatabase(db_name="testdb", user="user", password="password")

    # Create a test table
    db.execute("""
        CREATE TABLE IF NOT EXISTS secure_table (
            id SERIAL PRIMARY KEY,
            username TEXT,
            data BYTEA
        )
    """)

    # Insert plaintext data (it will be encrypted automatically)
    db.execute(
        "INSERT INTO secure_table (username, data) VALUES (%s, %s)",
        ("user1", "Sensitive Information"),
    )

    # Retrieve data (it will be decrypted automatically)
    results = db.execute("SELECT id, username, data FROM secure_table")
    for row in results:
        print(row)

    db.close()
