import hashlib
import base64
import os
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from cryptography.hazmat.primitives import hashes

def derive_key_from_password(password: str, salt: bytes = None) -> tuple[bytes, bytes]:
    if salt is None:
        salt = os.urandom(16)
    kdf = PBKDF2HMAC(
        algorithm=hashes.SHA256(),
        length=32,
        salt=salt,
        iterations=100000,
    )
    key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
    return salt, key

def encrypt_file(input_path: str, password: str, output_path: str = "encrypted.bin"):
    salt, key = derive_key_from_password(password)
    fernet = Fernet(key)

    with open(input_path, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    with open(output_path, "wb") as file:
        file.write(salt + encrypted)

    print(f"File encrypted and saved to {output_path}")

def decrypt_file(data: bytes, password: str, output_path: str = "decrypted.bin"):
    if len(data) < 16:
        raise ValueError("Invalid encrypted data: too short for salt")
    salt = data[:16]
    encrypted = data[16:]
    _, key = derive_key_from_password(password, salt)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(encrypted)
    except Exception as e:
        print("Decryption failed - " + str(e))
        return

    with open(output_path, "wb") as file:
        file.write(decrypted)

    print(f"File decrypted and saved to {output_path}")