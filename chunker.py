import base64

def chunk_file_base64(path: str, chunk_size: int = 600) -> list[str]:
    with open(path, "rb") as file:
        binary_data = file.read()

    # Convert to base64 text (so we can store in QR)
    b64_data = base64.b64encode(binary_data).decode()

    # Slice into chunks
    chunks = [b64_data[i:i+chunk_size] for i in range(0, len(b64_data), chunk_size)]

    return chunks
