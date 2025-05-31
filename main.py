from encryptor import encrypt_file, decrypt_file
from chunker import  chunk_file_base64
from qr_encoder import save_qr_chunks
from qr_scanner import scan_qr_chunks

encrypt_file("secret.txt", "password123")
chunks = chunk_file_base64("encrypted.bin")
save_qr_chunks(chunks)
decrypt_file(scan_qr_chunks(), "password123")