import cv2
from pyzbar.pyzbar import decode
import base64
import re

# Only allow characters valid in standard base64 alphabet (no URL-safe, no shell-special chars)
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')
_MAX_CHUNK_LENGTH = 1200  # tightened: two QR chunks of 600 chars each is the expected max
_MAX_CHUNKS = 512        # prevent unbounded memory accumulation


def _validate_chunk(data: str) -> bool:
    """Return True only if the chunk looks like valid base64-encoded data."""
    if not data or len(data) > _MAX_CHUNK_LENGTH:
        return False
    if not _BASE64_RE.fullmatch(data):  # fullmatch instead of match to cover entire string
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
            # Only accept QR codes whose raw bytes are pure ASCII base64 characters.
            # We do NOT follow, fetch, or execute any URL or command found in the data.
            try:
                data = obj.data.decode("ascii", errors="strict")
            except (UnicodeDecodeError, ValueError):
                print("⚠️  Skipping chunk with non-ASCII data.")
                continue

            if not _validate_chunk(data):
                print("⚠️  Skipping chunk that failed validation.")
                continue

            if len(chunks) >= _MAX_CHUNKS:
                print("⚠️  Maximum chunk count reached; ignoring further QR codes.")
                break

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
        # chunk has already been validated by _validate_chunk; decode it strictly.
        try:
            binary_data += base64.b64decode(chunk, validate=True)
        except Exception as e:
            print(f"⚠️  Skipping chunk that could not be base64-decoded: {e}")
    return binary_data
