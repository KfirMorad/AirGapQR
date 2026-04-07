import cv2
from pyzbar.pyzbar import decode
import base64
import re

# Only allow characters valid in standard base64 (no URL-safe variants to reduce attack surface)
_BASE64_RE = re.compile(r'^[A-Za-z0-9+/=]+$')
_MAX_CHUNK_LENGTH = 1200  # tightly bounded: chunk_size=600 base64-encodes to ~800 chars; 1200 is a safe ceiling
_MAX_TOTAL_CHUNKS = 2048  # prevent unbounded memory growth during a scan session


def _validate_chunk(data: str) -> bool:
    """Return True only if the chunk looks like valid base64-encoded data.

    Rejects:
    - empty strings
    - strings exceeding the maximum expected chunk length
    - strings containing characters outside the standard base64 alphabet
    """
    if not data or len(data) > _MAX_CHUNK_LENGTH:
        return False
    if not _BASE64_RE.fullmatch(data):
        return False
    return True


def scan_qr_chunks():
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
            # Guard against excessively large raw payloads before decoding
            if len(obj.data) > _MAX_CHUNK_LENGTH:
                print("\u26a0\ufe0f  Skipping oversized chunk.")
                continue

            try:
                # Strict ASCII decode – any non-ASCII byte raises UnicodeDecodeError
                data = obj.data.decode("ascii", errors="strict")
            except (UnicodeDecodeError, ValueError):
                print("\u26a0\ufe0f  Skipping chunk with non-ASCII data.")
                continue

            if not _validate_chunk(data):
                print("\u26a0\ufe0f  Skipping chunk that failed validation.")
                continue

            if len(chunks) >= _MAX_TOTAL_CHUNKS:
                print("\u26a0\ufe0f  Maximum chunk count reached; ignoring further QR codes.")
                break

            if data not in seen:
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
        try:
            binary_data += base64.b64decode(chunk, validate=True)
        except Exception as e:
            print(f"\u26a0\ufe0f  Skipping chunk that could not be base64-decoded: {e}")
    return binary_data
