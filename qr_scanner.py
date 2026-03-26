import cv2
from pyzbar.pyzbar import decode
import base64
import re

# Only accept chunks that are valid base64 (the format produced by the encoder).
# Reject anything that looks like a URL or contains unexpected characters,
# preventing arbitrary remote-resource fetching from malicious QR codes.
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')
# Reasonable upper bound: 600 base64 chars per chunk as set in the encoder.
_MAX_CHUNK_LEN = 800


def _validate_chunk(data: str) -> bool:
    """Return True only if data looks like a safe base64 chunk."""
    if len(data) > _MAX_CHUNK_LEN:
        return False
    if not _BASE64_RE.match(data):
        return False
    return True


def scan_qr_chunks() -> bytes:
    cap = cv2.VideoCapture(0)
    seen = set()
    chunks = []

    print("\U0001f4f7 Scanning... Press Q to quit.")

    while True:
        ret, frame = cap.read()
        if not ret:
            break

        decoded_objects = decode(frame)

        for obj in decoded_objects:
            try:
                data = obj.data.decode("ascii")
            except (UnicodeDecodeError, ValueError):
                print("\u26a0\ufe0f  Skipping chunk with non-ASCII content.")
                continue

            if data in seen:
                continue

            if not _validate_chunk(data):
                print("\u26a0\ufe0f  Skipping invalid/suspicious chunk.")
                continue

            print(f"\U0001f9e9 New chunk captured ({len(chunks)})")
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
        # validate again at decode time for defence-in-depth
        if not _validate_chunk(chunk):
            raise ValueError("Refusing to decode an invalid base64 chunk.")
        binary_data += base64.b64decode(chunk)
    return binary_data
