import qrcode
import os
import base64
def chunk_file_base64(path: str, chunk_size: int = 600) -> list[str]:
    with open(path, "rb") as file:
        binary_data = file.read()

    # Convert to base64 text (so we can store in QR)
    b64_data = base64.b64encode(binary_data).decode()

    # Slice into chunks
    chunks = [b64_data[i:i + chunk_size] for i in range(0, len(b64_data), chunk_size)]

    return chunks

def encrypted_to_qr(path: str, output_folder="qr_output"):

    chunks = chunk_file_base64(path)
    # Create the folder if it doesn't exist
    if not os.path.exists(output_folder):
        os.makedirs(output_folder)

    # Go through each chunk and create a QR code
    for i in range(len(chunks)):
        chunk = chunks[i]
        img = qrcode.make(chunk)

        # Format filename like qr_000.png, qr_001.png, etc.
        number = str(i)
        while len(number) < 3:
            number = "0" + number
        filename = "qr_" + number + ".png"

        # Full path to save
        full_path = os.path.join(output_folder, filename)
        img.save(full_path)

    print("✅ Saved " + str(len(chunks)) + " QR codes to folder: " + output_folder)
