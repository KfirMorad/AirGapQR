import hashlib
import base64
from cryptography.fernet import Fernet


def derive_key_from_password(password: str) -> bytes:
    sha256 = hashlib.sha256(password.encode()).digest()
    key = base64.urlsafe_b64encode(sha256)
    return key

def encrypt_file(input_path: str, password: str, output_path :str = "encrypted.bin"):
    # 1. Derive encryption key from password
    key = derive_key_from_password(password)
    fernet = Fernet(key)

    # 2. Read input file as bytes
    with open(input_path, "rb") as file:
        data = file.read()

    # 3. Encrypt the data
    encrypted = fernet.encrypt(data)

    # 4. Save the encrypted binary to output_path
    with open(output_path, "wb") as file:
        file.write(encrypted)

    print(f"✅ File encrypted and saved to {output_path}")

def decrypt_file(data: bytes, password: str, output_path: str = "decrypted.bin"):
    key = derive_key_from_password(password)
    fernet = Fernet(key)

    try:
        decrypted = fernet.decrypt(data)  # decrypt raw bytes
    except Exception as e:
        print("❌ Decryption failed - " + str(e))
        return

    with open(output_path, "wb") as file:
        file.write(decrypted)

    print(f"✅ File decrypted and saved to {output_path}")