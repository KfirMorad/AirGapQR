import cv2
from pyzbar.pyzbar import decode
import base64

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
            data = obj.data.decode()
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