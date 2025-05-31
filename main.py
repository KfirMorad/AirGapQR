from encryptor import encrypt_file, decrypt_file
from qr_encoder import encrypted_to_qr
from qr_scanner import scan_qr_chunks

encrypt_file("secret.txt", "password123")
encrypted_to_qr("encrypted.bin")
decrypt_file(scan_qr_chunks(), "password123")
