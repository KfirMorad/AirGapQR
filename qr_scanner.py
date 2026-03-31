import cv2
from pyzbar.pyzbar import decode
import base64
import re

# Only allow characters valid in base64 (A-Z, a-z, 0-9, +, /, =)
BASE64_PATTERN = re.compile(r'^[A-Za-z0-9+/=]+$')

def is_valid_base64_chunk(data: str) -> bool:
    """Validate that the scanned data is a pure base64 string and nothing else."""
    if not data:
        return False
    if not BASE64_PATTERN.match(data):
        return False
    # Attempt an actual base64 decode to confirm it is well-formed
    try:
        base64.b64decode(data, validate=True)
    except Exception:
        return False
    return True

def scan_qr_chunks():
    cap = cv2.VideoCapture(0)
    seen = set()
    chunks = []

    print("📷 Scanning... Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            # Decode raw bytes to string safely
            try:
                data = obj.data.decode('ascii')
            except (UnicodeDecodeError, ValueError):
                print("⚠️  Skipping chunk: could not decode as ASCII.")
                continue

            # Validate that the chunk is a legitimate base64 payload
            if not is_valid_base64_chunk(data):
                print("⚠️  Skipping chunk: failed base64 validation.")
                continue

            if data not in seen:
                print(f"🧩 New chunk captured ({len(chunks)})")
                seen.add(data)
                chunks.append(data)

        cv2.imshow("QR Scanner - Press Q to Stop", frame)

        if cv2.waitKey(1) & 0xFF == ord("q"):
            break

    cap.release()
    cv2.destroyAllWindows()
    return chunks_to_bytes(chunks)

def chunks_to_bytes(chunks: list) -> bytes:
    binary_data = b""
    for chunk in chunks:
        binary_data += base64.b64decode(chunk)
    return binary_data
