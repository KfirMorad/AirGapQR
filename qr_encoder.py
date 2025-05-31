import qrcode
import os

def save_qr_chunks(chunks, output_folder="qr_output"):
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
