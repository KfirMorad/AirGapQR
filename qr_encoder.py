import qrcode
import os
import base64
import re

# Only allow printable base64 characters in a chunk before encoding into a QR code
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')


def chunk_file_base64(path: str, chunk_size: int = 600) -> list:
    with open(path, "rb") as file:
        binary_data = file.read()

    # Convert to base64 text (so we can store in QR)
    b64_data = base64.b64encode(binary_data).decode("ascii")

    # Slice into chunks
    chunks = [b64_data[i:i + chunk_size] for i in range(0, len(b64_data), chunk_size)]

    return chunks


def _validate_chunk(chunk: str) -> bool:
    """Ensure the chunk contains only base64 characters before making a QR code."""
    return bool(chunk) and bool(_BASE64_RE.match(chunk))


def encrypted_to_qr(path: str, output_folder: str = "qr_output"):
    chunks = chunk_file_base64(path)

    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    saved = 0
    for i, chunk in enumerate(chunks):
        if not _validate_chunk(chunk):
            print(f"⚠️  Skipping chunk {i} – failed validation.")
            continue

        img = qrcode.make(chunk)

        # Format filename like qr_000.png, qr_001.png, etc.
        filename = f"qr_{i:03d}.png"

        # Full path to save
        full_path = os.path.join(output_folder, filename)
        img.save(full_path)
        saved += 1

    print("✅ Saved " + str(saved) + " QR codes to folder: " + output_folder)
