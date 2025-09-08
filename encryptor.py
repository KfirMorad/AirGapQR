import hashlib
import base64
from cryptography.fernet import Fernet


def derive_key_from_password(password: str) -> bytes:
    sha256 = hashlib.sha256(password.encode()).digest()
    key = base64.urlsafe_b64encode(sha256)
    return key

def encrypt_file(input_path: str, password: str, output_path :str = "encrypted.bin"):
    key = derive_key_from_password(password)
    fernet = Fernet(key)

    with open(input_path, "rb") as file:
        data = file.read()

    encrypted = fernet.encrypt(data)

    with open(output_path, "wb") as file:
        file.write(encrypted)

    print(f"File encrypted and saved to {output_path}")

def decrypt_file(data: bytes, password: str, output_path: str = "decrypted.bin"):
    key = derive_key_from_password(password)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(data)  # decrypt raw bytes
    except Exception as e:
        print("Decryption failed - " + str(e))
        return

    with open(output_path, "wb") as file:
        file.write(decrypted)

    print(f"File decrypted and saved to {output_path}")
