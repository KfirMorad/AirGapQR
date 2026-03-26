import qrcode
import os
import base64
import re

# Only allow characters that appear in standard base64 output.
# This prevents arbitrary data (e.g. URLs) from being encoded into QR codes.
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')


def chunk_file_base64(path: str, chunk_size: int = 600) -> list:
    with open(path, "rb") as file:
        binary_data = file.read()

    # Convert to base64 text (so we can store in QR)
    b64_data = base64.b64encode(binary_data).decode()

    # Slice into chunks
    chunks = [b64_data[i:i + chunk_size] for i in range(0, len(b64_data), chunk_size)]

    return chunks


def encrypted_to_qr(path: str, output_folder: str = "qr_output"):
    chunks = chunk_file_base64(path)

    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Go through each chunk and create a QR code
    for i, chunk in enumerate(chunks):
        # Validate that the chunk is pure base64 before encoding into a QR code.
        # This prevents SSRF by ensuring no URL or arbitrary payload can be embedded.
        if not _BASE64_RE.match(chunk):
            raise ValueError(f"Chunk {i} contains unexpected characters and will not be encoded.")

        img = qrcode.make(chunk)

        # Format filename like qr_000.png, qr_001.png, etc.
        filename = f"qr_{i:03d}.png"

        # Full path to save
        full_path = os.path.join(output_folder, filename)
        img.save(full_path)

    print("\u2705 Saved " + str(len(chunks)) + " QR codes to folder: " + output_folder)
