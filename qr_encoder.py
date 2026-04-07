import qrcode
import os
import base64
import re

# Only allow printable standard base64 characters in a chunk before encoding into a QR code
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')
_MAX_CHUNK_SIZE = 600   # must match the scanner's _MAX_CHUNK_LENGTH expectation
_MAX_CHUNKS = 512       # guard against absurdly large inputs slipping past the file-size check


def chunk_file_base64(path: str, chunk_size: int = _MAX_CHUNK_SIZE) -> list:
    # Clamp chunk_size to a safe positive integer to prevent integer-overflow-style abuse
    if not isinstance(chunk_size, int) or chunk_size <= 0 or chunk_size > _MAX_CHUNK_SIZE:
        raise ValueError(f"chunk_size must be a positive integer <= {_MAX_CHUNK_SIZE}")

    with open(path, "rb") as file:
        binary_data = file.read()

    # Convert to base64 text (so we can store in QR)
    b64_data = base64.b64encode(binary_data).decode("ascii")

    # Slice into chunks
    chunks = [b64_data[i:i + chunk_size] for i in range(0, len(b64_data), chunk_size)]

    if len(chunks) > _MAX_CHUNKS:
        raise ValueError(f"Encoded data produces too many chunks ({len(chunks)} > {_MAX_CHUNKS}).")

    return chunks


def _validate_chunk(chunk: str) -> bool:
    """Ensure the chunk is a non-empty string containing only base64 characters."""
    if not isinstance(chunk, str):
        return False
    return bool(chunk) and bool(_BASE64_RE.fullmatch(chunk))


def encrypted_to_qr(path: str, output_folder: str = "qr_output"):
    chunks = chunk_file_base64(path)

    # Resolve and validate the output folder to prevent path traversal
    safe_output = os.path.realpath(output_folder)
    cwd = os.path.realpath(os.getcwd())
    if not safe_output.startswith(cwd + os.sep) and safe_output != cwd:
        raise ValueError("output_folder must be inside the current working directory.")

    # Create the folder if it doesn't exist
    if not os.path.exists(safe_output):
        os.makedirs(safe_output)

    saved = 0
    for i, chunk in enumerate(chunks):
        if not _validate_chunk(chunk):
            print(f"⚠️  Skipping chunk {i} – failed validation.")
            continue

        img = qrcode.make(chunk)

        # Format filename like qr_000.png, qr_001.png, etc.
        filename = f"qr_{i:03d}.png"

        # Full path to save
        full_path = os.path.join(safe_output, filename)
        img.save(full_path)
        saved += 1

    print("✅ Saved " + str(saved) + " QR codes to folder: " + safe_output)
