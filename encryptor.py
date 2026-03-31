import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.backends import default_backend


SALT_SIZE = 16
PBKDF2_ITERATIONS = 600_000


def derive_key_from_password(password: str, salt: bytes) -> bytes:
    """Derive a Fernet-compatible key from a password using PBKDF2-HMAC-SHA256."""
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=PBKDF2_ITERATIONS,
        backend=default_backend()
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return key


def encrypt_file(input_path: str, password: str, output_path: str = "encrypted.bin"):
    salt = os.urandom(SALT_SIZE)
    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)

    with open(input_path, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    # Prepend salt so it can be recovered during decryption
    with open(output_path, "wb") as file:
        file.write(salt + encrypted)

    print(f"File encrypted and saved to {output_path}")


def decrypt_file(data: bytes, password: str, output_path: str = "decrypted.bin"):
    if len(data) < SALT_SIZE:
        print("Decryption failed - data too short to contain salt.")
        return

    salt = data[:SALT_SIZE]
    encrypted = data[SALT_SIZE:]

    key = derive_key_from_password(password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception as e:
        print("Decryption failed - " + str(e))
        return

    with open(output_path, "wb") as file:
        file.write(decrypted)

    print(f"File decrypted and saved to {output_path}")
